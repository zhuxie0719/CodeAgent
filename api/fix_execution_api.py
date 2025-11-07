"""
修复执行 API 路由
提供修复执行Agent的API接口
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import asyncio
import logging
from datetime import datetime
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent))

# 设置日志
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/fix", tags=["修复执行"])

# 全局引用（在 main_api.py 中设置）
_coordinator_manager = None
_agent_manager = None

def set_managers(coord_mgr, agent_mgr):
    """设置全局管理器引用"""
    global _coordinator_manager, _agent_manager
    _coordinator_manager = coord_mgr
    _agent_manager = agent_mgr

# 存储修复任务状态
fix_tasks = {}


class FixRequest(BaseModel):
    """修复请求模型"""
    file_path: Optional[str] = Field(None, description="文件路径")
    project_path: Optional[str] = Field(None, description="项目路径")
    issues: Optional[List[Dict[str, Any]]] = Field(None, description="问题列表")
    decisions: Optional[Dict[str, Any]] = Field(None, description="决策结果")
    task_info_file: Optional[str] = Field(None, description="任务信息文件路径（综合检测结果）")
    task_info: Optional[List[Dict[str, Any]]] = Field(None, description="任务信息列表（综合检测结果）")


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(True, description="是否成功")
    message: str = Field("操作成功", description="响应消息")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")


@router.post("/execute", response_model=BaseResponse)
async def execute_fix(
    request: FixRequest,
    background_tasks: BackgroundTasks
):
    """
    执行代码修复
    
    Args:
        request: 修复请求
        background_tasks: 后台任务
    
    Returns:
        修复结果
    """
    try:
        # 生成任务ID
        import uuid
        task_id = str(uuid.uuid4())
        
        # 验证输入：支持两种模式
        # 模式1: 从agent_task_info文件读取（综合检测结果）
        # 模式2: 直接传递issues列表（传统模式）
        
        issues_list = []
        project_path = None
        
        if request.task_info_file or request.task_info:
            # 模式1: 从agent_task_info读取
            task_info_list = request.task_info or []
            
            if request.task_info_file:
                # 从文件读取
                import json
                task_info_path = Path(request.task_info_file)
                
                # 尝试解析路径（可能是相对路径或绝对路径）
                if not task_info_path.is_absolute():
                    # 如果是相对路径，尝试从项目根目录查找
                    project_root = Path(__file__).parent.parent
                    task_info_path = project_root / task_info_path
                
                if not task_info_path.exists():
                    logger.error(f"任务信息文件不存在: {task_info_path}")
                    logger.error(f"   尝试的路径: {task_info_path.absolute()}")
                    raise HTTPException(status_code=404, detail=f"任务信息文件不存在: {request.task_info_file}")
                
                logger.info(f"正在读取任务信息文件: {task_info_path}")
                try:
                    with open(task_info_path, 'r', encoding='utf-8') as f:
                        task_info_list = json.load(f)
                    logger.info(f"成功读取任务信息文件，包含 {len(task_info_list)} 个任务")
                except Exception as e:
                    logger.error(f"读取任务信息文件失败: {e}")
                    raise HTTPException(status_code=500, detail=f"读取任务信息文件失败: {str(e)}")
            
            if not task_info_list:
                raise HTTPException(status_code=400, detail="任务信息列表为空")
            
            # 将task_info转换为issues格式，并按文件分组
            logger.info(f"从任务信息读取: {len(task_info_list)} 个任务")
            
            # 获取项目路径（从第一个任务中获取）
            if task_info_list:
                project_path = task_info_list[0].get("project_root")
            
            # 按文件分组任务
            from collections import defaultdict
            tasks_by_file = defaultdict(list)
            for task_info in task_info_list:
                problem_file = task_info.get("problem_file")
                if problem_file:
                    tasks_by_file[problem_file].append(task_info)
            
            # 将任务信息转换为issues格式
            for file_path, tasks in tasks_by_file.items():
                for task_info in tasks:
                    defect_info = task_info.get("defect_info", {})
                    issue = {
                        "file": file_path,
                        "file_path": file_path,
                        "line": defect_info.get("line", 0),
                        "message": task_info.get("task", ""),
                        "severity": defect_info.get("severity", "info"),
                        "type": defect_info.get("tool", "unknown"),
                        "tool": defect_info.get("tool", "unknown"),
                        "source": defect_info.get("source", "static"),
                        "original_task": task_info  # 保留原始任务信息
                    }
                    issues_list.append(issue)
            
            logger.info(f"转换后的问题数量: {len(issues_list)}")
            
        elif request.issues:
            # 模式2: 直接使用传入的issues
            issues_list = request.issues
            project_path = request.project_path or request.file_path
        
        if not issues_list:
            raise HTTPException(status_code=400, detail="问题列表不能为空")
        
        if not project_path:
            # 从第一个问题中获取文件路径
            if issues_list:
                first_issue = issues_list[0]
                file_path = first_issue.get("file_path") or first_issue.get("file", "")
                if file_path:
                    project_path = os.path.dirname(file_path)
                else:
                    # 如果无法获取项目路径，使用当前工作目录
                    project_path = os.getcwd()
                    logger.warning(f"无法从问题列表中获取项目路径，使用当前工作目录: {project_path}")
            else:
                project_path = os.getcwd()
                logger.warning(f"问题列表为空，使用当前工作目录: {project_path}")
        
        # 创建任务数据
        task_data = {
            "file_path": request.file_path,
            "project_path": project_path,
            "issues": issues_list,
            "decisions": request.decisions or {}
        }
        
        # 存储任务状态
        fix_tasks[task_id] = {
            "status": "processing",
            "file_path": project_path or request.file_path or "",
            "issues_count": len(issues_list),
            "created_at": datetime.now().isoformat(),
            "progress": 0,
            "current_step": "任务已创建，等待执行",
            "fixed_files": 0,
            "total_files": 0,
            "fixed_issues": 0
        }
        
        # 异步执行修复任务
        background_tasks.add_task(_execute_fix_task, task_id, task_data)
        
        return BaseResponse(
            success=True,
            message="修复任务已提交，正在处理中...",
            data={
                "task_id": task_id,
                "status": "processing"
            }
        )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修复执行失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"修复执行失败: {str(e)}")


@router.get("/status/{task_id}", response_model=BaseResponse)
async def get_fix_status(task_id: str):
    """
    获取修复任务状态
    
    Args:
        task_id: 任务ID
    
    Returns:
        任务状态
    """
    if task_id not in fix_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = fix_tasks[task_id]
    return BaseResponse(
        success=True,
        message="获取任务状态成功",
        data=task
    )


@router.get("/result/{task_id}", response_model=BaseResponse)
async def get_fix_result(task_id: str):
    """
    获取修复结果
    
    Args:
        task_id: 任务ID
    
    Returns:
        修复结果
    """
    logger.info(f"📥 请求获取修复结果: {task_id}")
    
    if task_id not in fix_tasks:
        logger.warning(f"⚠️ 任务不存在: {task_id}")
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = fix_tasks[task_id]
    logger.info(f"📋 任务状态: {task.get('status')}")
    
    if task["status"] not in ["completed", "failed"]:
        logger.warning(f"⚠️ 任务尚未完成: {task_id}, 状态: {task.get('status')}")
        raise HTTPException(status_code=400, detail=f"任务尚未完成，当前状态: {task.get('status')}")
    
    result = task.get("result", {})
    logger.info(f"✅ 返回修复结果，结果键: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
    
    return BaseResponse(
        success=True,
        message="获取修复结果成功",
        data=result
    )


async def _execute_fix_task(task_id: str, task_data: Dict[str, Any]):
    """
    执行修复任务
    
    Args:
        task_id: 任务ID
        task_data: 任务数据
    """
    try:
        logger.info(f"{'='*60}")
        logger.info(f"🚀 开始执行修复任务: {task_id}")
        logger.info(f"   问题数量: {len(task_data.get('issues', []))}")
        logger.info(f"   项目路径: {task_data.get('project_path', 'N/A')}")
        logger.info(f"{'='*60}")
        
        # 更新进度
        fix_tasks[task_id]["progress"] = 5
        fix_tasks[task_id]["status"] = "processing"
        fix_tasks[task_id]["current_step"] = "初始化修复任务"
        
        # 方式1: 通过Coordinator执行（推荐）
        if _coordinator_manager and _coordinator_manager.coordinator:
            coordinator = _coordinator_manager.coordinator
            
            fix_tasks[task_id]["progress"] = 10
            fix_tasks[task_id]["current_step"] = "通过Coordinator创建修复任务"
            logger.info(f"📋 通过Coordinator创建修复任务...")
            
            # 创建修复任务
            fix_task_id = await coordinator.create_task('fix_issues', task_data)
            logger.info(f"✅ 修复任务已创建: {fix_task_id}")
            
            # 分配给修复Agent
            if 'fix_execution_agent' in coordinator.agents:
                fix_tasks[task_id]["progress"] = 15
                fix_tasks[task_id]["current_step"] = "分配给修复Agent"
                logger.info(f"🤖 分配给修复Agent: fix_execution_agent")
                await coordinator.assign_task(fix_task_id, 'fix_execution_agent')
                
                fix_tasks[task_id]["progress"] = 20
                fix_tasks[task_id]["current_step"] = "等待修复Agent执行"
                logger.info(f"⏳ 等待修复Agent执行（最多5分钟）...")
                
                # 等待修复完成（最多等待5分钟）
                logger.info(f"⏳ 开始等待修复结果...")
                try:
                    fix_result = await coordinator.task_manager.get_task_result(fix_task_id, timeout=300)
                    logger.info(f"✅ 修复结果已获取")
                    logger.info(f"   修复结果键: {list(fix_result.keys()) if isinstance(fix_result, dict) else 'N/A'}")
                except Exception as e:
                    logger.error(f"❌ 获取修复结果失败: {e}")
                    fix_tasks[task_id].update({
                        "status": "failed",
                        "error": f"获取修复结果失败: {str(e)}",
                        "completed_at": datetime.now().isoformat(),
                        "current_step": "获取结果失败"
                    })
                    return
                
                # 更新任务状态（包含修复结果中的统计信息）
                logger.info(f"📝 更新修复任务状态...")
                fix_tasks[task_id].update({
                    "status": "completed" if fix_result.get("success") else "failed",
                    "progress": 100,
                    "result": fix_result,
                    "completed_at": datetime.now().isoformat(),
                    "current_step": "修复完成",
                    "fixed_files": fix_result.get("fixed_files", 0),
                    "total_files": fix_result.get("total_files", 0),
                    "fixed_issues": fix_result.get("fixed_issues", 0),
                    "total_issues": fix_result.get("total_issues", 0)
                })
                
                logger.info(f"✅ 修复任务状态已更新: {task_id}")
                logger.info(f"   状态: {fix_tasks[task_id]['status']}")
                logger.info(f"   修复文件数: {fix_tasks[task_id].get('fixed_files', 0)}/{fix_tasks[task_id].get('total_files', 0)}")
                logger.info(f"   修复问题数: {fix_tasks[task_id].get('fixed_issues', 0)}/{fix_tasks[task_id].get('total_issues', 0)}")
                
                logger.info(f"{'='*60}")
                logger.info(f"✅ 修复任务完成: {task_id}")
                logger.info(f"   成功修复文件数: {fix_result.get('fixed_files', 0)}/{fix_result.get('total_files', 0)}")
                logger.info(f"   成功修复问题数: {fix_result.get('fixed_issues', 0)}/{fix_result.get('total_issues', 0)}")
                if fix_result.get('output_dir'):
                    logger.info(f"   修复结果目录: {fix_result.get('output_dir')}")
                logger.info(f"{'='*60}")
                return
            else:
                logger.warning("⚠️ fix_execution_agent 未注册，尝试直接创建Agent")
        
        # 方式2: 直接创建Agent执行（备用方案）
        logger.info(f"⚠️ 使用直接创建Agent方式执行修复")
        fix_tasks[task_id]["progress"] = 30
        fix_tasks[task_id]["current_step"] = "创建修复Agent"
        
        from agents.fix_execution_agent.agent import FixExecutionAgent
        
        # 创建修复Agent
        logger.info(f"🤖 正在创建修复Agent...")
        agent = FixExecutionAgent(config={
            "enabled": True,
            "LLM_MODEL": "deepseek-coder",
            "LLM_BASE_URL": "https://api.deepseek.com/v1/chat/completions"
        })
        
        fix_tasks[task_id]["progress"] = 40
        fix_tasks[task_id]["current_step"] = "初始化修复Agent"
        logger.info(f"🔧 正在初始化修复Agent...")
        await agent.initialize()
        
        fix_tasks[task_id]["progress"] = 50
        fix_tasks[task_id]["current_step"] = "执行修复任务"
        logger.info(f"🚀 开始执行修复任务...")
        
        # 执行修复
        logger.info(f"🚀 开始执行修复任务...")
        try:
            result = await agent.process_task(task_id, task_data)
            logger.info(f"✅ 修复任务执行完成")
            logger.info(f"   修复结果键: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        except Exception as e:
            logger.error(f"❌ 修复任务执行异常: {e}")
            import traceback
            logger.error(f"错误详情:\n{traceback.format_exc()}")
            fix_tasks[task_id].update({
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.now().isoformat(),
                "current_step": "执行失败"
            })
            return
        
        fix_tasks[task_id]["progress"] = 95
        fix_tasks[task_id]["current_step"] = "保存修复结果"
        
        # 更新任务状态（包含修复结果中的统计信息）
        logger.info(f"📝 更新修复任务状态...")
        fix_tasks[task_id].update({
            "status": "completed" if result.get("success") else "failed",
            "progress": 100,
            "result": result,
            "completed_at": datetime.now().isoformat(),
            "current_step": "修复完成",
            "fixed_files": result.get("fixed_files", 0),
            "total_files": result.get("total_files", 0),
            "fixed_issues": result.get("fixed_issues", 0),
            "total_issues": result.get("total_issues", 0)
        })
        
        logger.info(f"✅ 修复任务状态已更新: {task_id}")
        logger.info(f"   状态: {fix_tasks[task_id]['status']}")
        logger.info(f"   修复文件数: {fix_tasks[task_id].get('fixed_files', 0)}/{fix_tasks[task_id].get('total_files', 0)}")
        logger.info(f"   修复问题数: {fix_tasks[task_id].get('fixed_issues', 0)}/{fix_tasks[task_id].get('total_issues', 0)}")
        
        logger.info(f"{'='*60}")
        logger.info(f"✅ 修复任务完成: {task_id}")
        logger.info(f"   成功修复文件数: {result.get('fixed_files', 0)}/{result.get('total_files', 0)}")
        logger.info(f"   成功修复问题数: {result.get('fixed_issues', 0)}/{result.get('total_issues', 0)}")
        if result.get('output_dir'):
            logger.info(f"   修复结果目录: {result.get('output_dir')}")
        logger.info(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"{'='*60}")
        logger.error(f"❌ 修复任务执行失败: {task_id}")
        logger.error(f"   错误信息: {str(e)}")
        logger.error(f"{'='*60}")
        import traceback
        logger.error(f"错误详情:\n{traceback.format_exc()}")
        
        fix_tasks[task_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat(),
            "current_step": "修复失败"
        })


@router.get("/health")
async def health_check():
    """
    健康检查
    
    Returns:
        健康状态
    """
    active_tasks = len([t for t in fix_tasks.values() if t.get("status") == "processing"])
    
    return {
        "status": "healthy",
        "active_tasks": active_tasks,
        "total_tasks": len(fix_tasks),
        "coordinator_available": _coordinator_manager is not None and _coordinator_manager.coordinator is not None
    }
