"""
简化的BugDetectionAgent API服务
只保留接口调用，具体逻辑在agents层
"""

import asyncio
import uuid
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# 添加项目根目录到Python路径
import sys
sys.path.append(str(Path(__file__).parent.parent))

# 导入真正的BugDetectionAgent
from agents.bug_detection_agent.agent import BugDetectionAgent
# 预留其它Agent导入（录屏展示用途，暂不启用）
# from agents.fix_execution_agent.agent import FixExecutionAgent
# from agents.test_validation_agent.agent import TestValidationAgent
# from agents.code_analysis_agent.agent import CodeAnalysisAgent
# from agents.code_quality_agent.agent import CodeQualityAgent
# from agents.performance_optimization_agent.agent import PerformanceOptimizationAgent
from coordinator.coordinator import Coordinator

# 简化的设置
class Settings:
    AGENTS = {"bug_detection_agent": {"enabled": True}}

settings = Settings()

# 数据模型
class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(True, description="是否成功")
    message: str = Field("操作成功", description="响应消息")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")

class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    message: str = Field(..., description="状态消息")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")

# 创建FastAPI应用
app = FastAPI(
    title="AI Agent 缺陷检测 API",
    description="专注于缺陷检测的API服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局实例
bug_detection_agent = None
# fix_execution_agent = None
# test_validation_agent = None
# code_analysis_agent = None
# code_quality_agent = None
# performance_optimization_agent = None
coordinator = None

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    global bug_detection_agent, coordinator
    try:
        config = settings.AGENTS.get("bug_detection_agent", {})
        bug_detection_agent = BugDetectionAgent(config)
        await bug_detection_agent.start()
        print("BugDetectionAgent 启动成功")
    except Exception as e:
        print(f"BugDetectionAgent 启动失败: {e}")
        bug_detection_agent = None

    try:
        coordinator = Coordinator(config={})
        await coordinator.start()
        print("Coordinator 启动成功")
    except Exception as e:
        print(f"Coordinator 启动失败: {e}")
        coordinator = None

    # 注册检测Agent到协调中心（关键：否则无法分配任务给真实Agent）
    try:
        if coordinator and bug_detection_agent:
            await coordinator.register_agent('bug_detection_agent', bug_detection_agent)
            print("BugDetectionAgent 已注册到 Coordinator")
    except Exception as e:
        print(f"注册 BugDetectionAgent 失败: {e}")

    # 预留：其它Agent启动与注册（录屏注释占位，需要时取消注释即可）
    # global fix_execution_agent, test_validation_agent, code_analysis_agent, code_quality_agent, performance_optimization_agent
    # try:
    #     fix_execution_agent = FixExecutionAgent(config={})
    #     await fix_execution_agent.start()
    #     if coordinator:
    #         await coordinator.register_agent('fix_execution_agent', fix_execution_agent)
    #     print("FixExecutionAgent 启动并注册成功")
    # except Exception as e:
    #     print(f"FixExecutionAgent 启动/注册失败: {e}")
    # try:
    #     test_validation_agent = TestValidationAgent(config={})
    #     await test_validation_agent.start()
    #     if coordinator:
    #         await coordinator.register_agent('test_validation_agent', test_validation_agent)
    #     print("TestValidationAgent 启动并注册成功")
    # except Exception as e:
    #     print(f"TestValidationAgent 启动/注册失败: {e}")
    # try:
    #     code_analysis_agent = CodeAnalysisAgent(config={})
    #     await code_analysis_agent.start()
    #     if coordinator:
    #         await coordinator.register_agent('code_analysis_agent', code_analysis_agent)
    #     print("CodeAnalysisAgent 启动并注册成功")
    # except Exception as e:
    #     print(f"CodeAnalysisAgent 启动/注册失败: {e}")
    # try:
    #     code_quality_agent = CodeQualityAgent(config={})
    #     await code_quality_agent.start()
    #     if coordinator:
    #         await coordinator.register_agent('code_quality_agent', code_quality_agent)
    #     print("CodeQualityAgent 启动并注册成功")
    # except Exception as e:
    #     print(f"CodeQualityAgent 启动/注册失败: {e}")
    # try:
    #     performance_optimization_agent = PerformanceOptimizationAgent(config={})
    #     await performance_optimization_agent.start()
    #     if coordinator:
    #         await coordinator.register_agent('performance_optimization_agent', performance_optimization_agent)
    #     print("PerformanceOptimizationAgent 启动并注册成功")
    # except Exception as e:
    #     print(f"PerformanceOptimizationAgent 启动/注册失败: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    global bug_detection_agent, coordinator
    if bug_detection_agent:
        await bug_detection_agent.stop()
        print("BugDetectionAgent 已停止")
    # 预留：其它Agent停止（需要时取消注释）
    # if fix_execution_agent:
    #     await fix_execution_agent.stop()
    #     print("FixExecutionAgent 已停止")
    # if test_validation_agent:
    #     await test_validation_agent.stop()
    #     print("TestValidationAgent 已停止")
    # if code_analysis_agent:
    #     await code_analysis_agent.stop()
    #     print("CodeAnalysisAgent 已停止")
    # if code_quality_agent:
    #     await code_quality_agent.stop()
    #     print("CodeQualityAgent 已停止")
    # if performance_optimization_agent:
    #     await performance_optimization_agent.stop()
    #     print("PerformanceOptimizationAgent 已停止")
    if coordinator:
        await coordinator.stop()
        print("Coordinator 已停止")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    global bug_detection_agent, coordinator
    
    if bug_detection_agent and coordinator:
        agent_status = bug_detection_agent.get_status()
        coord_status = await coordinator.health_check()
        return HealthResponse(
            status="healthy",
            message=f"API服务运行正常，Agent状态: {agent_status['status']}，Coordinator: running={coord_status['is_running']}",
            timestamp=datetime.now().isoformat()
        )
    else:
        return HealthResponse(
            status="error",
            message="BugDetectionAgent 或 Coordinator 未启动",
            timestamp=datetime.now().isoformat()
        )

@app.post("/api/v1/detection/upload", response_model=BaseResponse)
async def upload_file_for_detection(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    enable_static: bool = Query(True, description="启用自定义静态检测"),
    enable_pylint: bool = Query(True, description="启用Pylint检测"),
    enable_flake8: bool = Query(True, description="启用Flake8检测"),
    enable_bandit: bool = Query(True, description="启用Bandit安全检测"),
    enable_mypy: bool = Query(True, description="启用Mypy类型检查"),
    enable_ai_analysis: bool = Query(True, description="启用AI分析"),
    analysis_type: str = Query("file", description="分析类型: file(单文件) 或 project(项目)")
):
    """上传文件进行缺陷检测 - 支持复杂项目压缩包"""
    global coordinator
    
    if not coordinator:
        raise HTTPException(status_code=500, detail="Coordinator 未启动")
    
    # 验证文件大小
    content = await file.read()
    file_size = len(content)
    
    # 根据分析类型设置不同的限制
    if analysis_type == "project":
        max_size = 100 * 1024 * 1024  # 100MB for projects
        supported_extensions = ['.zip', '.tar', '.tar.gz', '.rar', '.7z']
    else:
        max_size = 10 * 1024 * 1024  # 10MB for single files
        supported_extensions = ['.py', '.java', '.c', '.cpp', '.h', '.hpp', '.js', '.ts', '.go']
    
    if file_size > max_size:
        raise HTTPException(status_code=413, detail=f"文件过大，最大支持{max_size // (1024*1024)}MB")
    
    # 验证文件类型
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in supported_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件类型。支持的类型: {', '.join(supported_extensions)}"
        )
    
    # 保存文件
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / f"{file.filename}"
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 根据分析类型创建检测任务
    if analysis_type == "file":
        # 单文件检测
        task_data = {
            "file_path": str(file_path),
            "analysis_type": "file",
            "options": {
                "enable_static": enable_static,
                "enable_pylint": enable_pylint,
                "enable_flake8": enable_flake8,
                "enable_bandit": enable_bandit,
                "enable_mypy": enable_mypy,
                "enable_ai_analysis": enable_ai_analysis
            }
        }
    elif analysis_type == "project":
        # 项目检测
        task_data = {
            # 提示：这里传入上传的压缩包路径，由Agent负责解压
            "file_path": str(file_path),
            "analysis_type": "project",
            "options": {
                "enable_static": enable_static,
                "enable_pylint": enable_pylint,
                "enable_flake8": enable_flake8,
                "enable_bandit": enable_bandit,
                "enable_mypy": enable_mypy,
                "enable_ai_analysis": enable_ai_analysis
            }
        }
    else:
        raise HTTPException(status_code=400, detail=f"无效的分析类型: {analysis_type}")
    
    try:
        # 通过协调中心创建 detect_bugs 任务并分配给 bug_detection_agent
        task_id = await coordinator.create_task('detect_bugs', task_data)
        await coordinator.assign_task(task_id, 'bug_detection_agent')

        # 后台任务：基于协调中心的任务结果生成报告与结构化数据
        background_tasks.add_task(generate_report_task, task_id, str(file_path))
        background_tasks.add_task(store_structured_data, task_id, str(file_path), analysis_type)

        return BaseResponse(
            message="文件上传成功，开始检测",
            data={
                "task_id": task_id,
                "filename": file.filename,
                "file_size": file_size,
                "agent_id": "bug_detection_agent",
                "analysis_type": analysis_type
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交检测任务失败: {str(e)}")

@app.get("/api/v1/tasks/{task_id}", response_model=BaseResponse)
async def get_task_status(task_id: str):
    """获取任务状态"""
    global coordinator
    
    if not coordinator:
        raise HTTPException(status_code=500, detail="Coordinator 未启动")
    
    try:
        task = coordinator.task_manager.tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        data = {
            "task_id": task_id,
            "status": task['status'].value,
            "created_at": task['created_at'].isoformat(),
            "started_at": task['started_at'].isoformat() if task['started_at'] else None,
            "completed_at": task['completed_at'].isoformat() if task['completed_at'] else None,
            "result": task['result'],
            "error": task['error']
        }
        return BaseResponse(message="获取任务状态成功", data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")

@app.get("/api/v1/detection/rules", response_model=BaseResponse)
async def get_detection_rules():
    """获取检测规则"""
    global bug_detection_agent
    if not bug_detection_agent:
        raise HTTPException(status_code=500, detail="BugDetectionAgent 未启动")
    try:
        rules = await bug_detection_agent.get_detection_rules()
        return BaseResponse(message="获取检测规则成功", data=rules)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取检测规则失败: {str(e)}")

@app.get("/api/v1/ai-reports/{task_id}")
async def get_ai_report(task_id: str):
    """获取AI生成的自然语言报告"""
    global coordinator
    if not coordinator:
        raise HTTPException(status_code=500, detail="Coordinator 未启动")
    try:
        # 获取任务状态
        task = coordinator.task_manager.tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        if task['status'].value != "completed":
            raise HTTPException(status_code=400, detail="任务尚未完成")
        
        # 检查AI报告文件是否存在
        ai_report_path = Path("reports") / f"ai_report_{task_id}.md"
        
        if ai_report_path.exists():
            # 读取AI报告内容
            with open(ai_report_path, 'r', encoding='utf-8') as f:
                ai_report_content = f.read()
            
            return BaseResponse(
                message="获取AI报告成功",
                data={
                    "task_id": task_id,
                    "ai_report": ai_report_content,
                    "report_type": "markdown"
                }
            )
        else:
            # 如果没有AI报告文件，实时生成一个
            detection_results = (task.get('result') or {}).get("detection_results", {})
            file_path = (task.get('result') or {}).get("file_path", "")
            
            if detection_results:
                ai_report = await generate_ai_report(detection_results, file_path)
                
                # 保存AI报告
                ai_report_path.parent.mkdir(exist_ok=True)
                with open(ai_report_path, 'w', encoding='utf-8') as f:
                    f.write(ai_report)
                
                return BaseResponse(
                    message="获取AI报告成功",
                    data={
                        "task_id": task_id,
                        "ai_report": ai_report,
                        "report_type": "markdown"
                    }
                )
            else:
                raise HTTPException(status_code=404, detail="检测结果不存在")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取AI报告失败: {str(e)}")

@app.get("/api/v1/ai-reports/{task_id}/download")
async def download_ai_report(task_id: str):
    """下载AI报告文件"""
    try:
        # 检查AI报告文件是否存在
        ai_report_path = Path("reports") / f"ai_report_{task_id}.md"
        
        if not ai_report_path.exists():
            raise HTTPException(status_code=404, detail="AI报告文件不存在")
        
        # 返回文件下载
        from fastapi.responses import FileResponse
        return FileResponse(
            path=str(ai_report_path),
            filename=f"ai_report_{task_id}.md",
            media_type="text/markdown"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载AI报告失败: {str(e)}")

@app.get("/api/v1/structured-data/{task_id}", response_model=BaseResponse)
async def get_structured_data(task_id: str):
    """获取结构化数据给修复agent"""
    try:
        # 检查结构化数据文件是否存在
        structured_file = Path("structured_data") / f"structured_data_{task_id}.json"
        
        if not structured_file.exists():
            raise HTTPException(status_code=404, detail="结构化数据不存在")
        
        # 读取结构化数据
        with open(structured_file, 'r', encoding='utf-8') as f:
            structured_data = json.load(f)
        
        return BaseResponse(
            message="获取结构化数据成功",
            data=structured_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取结构化数据失败: {str(e)}")

@app.get("/api/v1/reports/{task_id}")
async def download_report(task_id: str):
    """下载检测报告"""
    global coordinator
    if not coordinator:
        raise HTTPException(status_code=500, detail="Coordinator 未启动")
    
    try:
        # 获取任务状态
        task = coordinator.task_manager.tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        if task['status'].value != "completed":
            raise HTTPException(status_code=400, detail="任务尚未完成")
        
        # 生成报告
        detection_results = (task.get('result') or {}).get("detection_results", {})
        file_path = (task.get('result') or {}).get("file_path", "")
        
        if not detection_results:
            raise HTTPException(status_code=404, detail="检测结果不存在")
        
        # 检查BugDetectionAgent是否有generate_downloadable_report方法
        if hasattr(bug_detection_agent, 'generate_downloadable_report'):
            report_path = await bug_detection_agent.generate_downloadable_report(detection_results, file_path)
        else:
            # 如果没有该方法，创建一个简化的报告
            report_path = await create_simple_report(detection_results, file_path, task_id)
        
        if not report_path or not Path(report_path).exists():
            raise HTTPException(status_code=404, detail="报告文件不存在")
        
        # 返回文件
        from fastapi.responses import FileResponse
        return FileResponse(
            path=report_path,
            filename=f"bug_detection_report_{task_id}.json",
            media_type="application/json"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载报告失败: {str(e)}")

async def create_simple_report(detection_results: Dict[str, Any], file_path: str, task_id: str) -> str:
    """创建简化的检测报告"""
    try:
        # 创建报告目录
        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        
        # 生成报告文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bug_detection_report_{timestamp}.json"
        report_path = report_dir / filename
        
        # 生成报告内容
        report_data = {
            "report_info": {
                "generated_at": datetime.now().isoformat(),
                "file_path": file_path,
                "task_id": task_id,
                "total_issues": detection_results.get("total_issues", 0),
                "summary": detection_results.get("summary", {}),
                "detection_tools": detection_results.get("detection_tools", [])
            },
            "issues": detection_results.get("issues", []),
            "statistics": {
                "by_severity": _get_issues_by_severity(detection_results.get("issues", [])),
                "by_type": _get_issues_by_type(detection_results.get("issues", [])),
            }
        }
        
        # 保存报告
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"简化检测报告已生成: {report_path}")
        return str(report_path)
        
    except Exception as e:
        print(f"生成简化报告失败: {e}")
        return None

def _get_issues_by_severity(issues: List[Dict[str, Any]]) -> Dict[str, int]:
    """按严重性统计问题"""
    severity_count = {}
    for issue in issues:
        severity = issue.get("severity", "info")
        severity_count[severity] = severity_count.get(severity, 0) + 1
    return severity_count

def _get_issues_by_type(issues: List[Dict[str, Any]]) -> Dict[str, int]:
    """按类型统计问题"""
    type_count = {}
    for issue in issues:
        issue_type = issue.get("type", "unknown")
        type_count[issue_type] = type_count.get(issue_type, 0) + 1
    return type_count

async def generate_report_task(task_id: str, file_path: str):
    """后台任务：生成检测报告"""
    global coordinator
    
    try:
        # 等待任务完成
        max_wait_time = 300  # 5分钟
        wait_interval = 2    # 2秒
        waited_time = 0
        
        while waited_time < max_wait_time:
            task = coordinator.task_manager.tasks.get(task_id)
            if task and task['status'].value == "completed":
                break
            await asyncio.sleep(wait_interval)
            waited_time += wait_interval
        
        if waited_time >= max_wait_time:
            print(f"任务 {task_id} 超时，无法生成报告")
            return
        
        # 生成报告
        detection_results = (task.get('result') or {}).get("detection_results", {})
        if detection_results:
            # 生成JSON报告
            report_path = await create_simple_report(detection_results, file_path, task_id)
            
            if report_path:
                print(f"JSON报告已生成: {report_path}")
        
    except Exception as e:
        print(f"生成报告任务失败: {e}")

async def store_structured_data(task_id: str, file_path: str, analysis_type: str):
    """后台任务：存储结构化信息给修复agent"""
    global coordinator
    
    try:
        # 等待任务完成
        max_wait_time = 300  # 5分钟
        wait_interval = 2    # 2秒
        waited_time = 0
        
        while waited_time < max_wait_time:
            task = coordinator.task_manager.tasks.get(task_id)
            if task and task['status'].value == "completed":
                break
            await asyncio.sleep(wait_interval)
            waited_time += wait_interval
        
        if waited_time >= max_wait_time:
            print(f"任务 {task_id} 超时，无法存储结构化数据")
            return
        
        # 获取检测结果
        detection_results = (task.get('result') or {}).get("detection_results", {})
        if not detection_results:
            print(f"任务 {task_id} 没有检测结果")
            return
        
        # 创建结构化数据存储目录
        structured_dir = Path("structured_data")
        structured_dir.mkdir(exist_ok=True)
        
        # 生成结构化数据
        structured_data = {
            "task_id": task_id,
            "file_path": file_path,
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_issues": detection_results.get("total_issues", 0),
                "error_count": detection_results.get("summary", {}).get("error_count", 0),
                "warning_count": detection_results.get("summary", {}).get("warning_count", 0),
                "info_count": detection_results.get("summary", {}).get("info_count", 0),
                "languages_detected": detection_results.get("languages_detected", []),
                "total_files": detection_results.get("total_files", 1)
            },
            "issues_by_priority": categorize_issues_by_priority(detection_results.get("issues", [])),
            "fix_recommendations": generate_fix_recommendations(detection_results.get("issues", [])),
            "project_structure": analyze_project_structure(detection_results, analysis_type),
            "detection_metadata": {
                "detection_tools": detection_results.get("detection_tools", []),
                "analysis_time": detection_results.get("analysis_time", 0),
                "project_path": detection_results.get("project_path", file_path)
            }
        }
        
        # 保存结构化数据
        structured_file = structured_dir / f"structured_data_{task_id}.json"
        with open(structured_file, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, ensure_ascii=False, indent=2)
        
        print(f"结构化数据已存储: {structured_file}")
        
    except Exception as e:
        print(f"存储结构化数据失败: {e}")

async def generate_ai_report(detection_results: Dict[str, Any], file_path: str) -> str:
    """生成AI分析报告"""
    try:
        issues = detection_results.get("issues", [])
        total_issues = detection_results.get("total_issues", 0)
        
        if total_issues == 0:
            return "# AI分析报告\n\n## 检测结果\n\n✅ 未发现明显的代码缺陷。\n\n## 建议\n\n- 代码质量良好，建议继续保持\n- 可以考虑添加更多的单元测试\n- 定期进行代码审查\n"
        
        # 按严重性分组问题
        error_issues = [issue for issue in issues if issue.get("severity") == "error"]
        warning_issues = [issue for issue in issues if issue.get("severity") == "warning"]
        info_issues = [issue for issue in issues if issue.get("severity") == "info"]
        
        report = f"# AI分析报告\n\n"
        report += f"## 文件信息\n\n- **文件路径**: {file_path}\n"
        report += f"- **总问题数**: {total_issues}\n"
        report += f"- **错误**: {len(error_issues)} 个\n"
        report += f"- **警告**: {len(warning_issues)} 个\n"
        report += f"- **信息**: {len(info_issues)} 个\n\n"
        
        # 严重问题分析
        if error_issues:
            report += "## 🚨 严重问题\n\n"
            for issue in error_issues[:5]:  # 只显示前5个
                report += f"### {issue.get('type', 'unknown')}\n"
                report += f"- **位置**: 第{issue.get('line', 0)}行\n"
                report += f"- **描述**: {issue.get('message', '')}\n"
                report += f"- **建议**: 需要立即修复此问题\n\n"
        
        # 警告问题分析
        if warning_issues:
            report += "## ⚠️ 警告问题\n\n"
            for issue in warning_issues[:5]:  # 只显示前5个
                report += f"### {issue.get('type', 'unknown')}\n"
                report += f"- **位置**: 第{issue.get('line', 0)}行\n"
                report += f"- **描述**: {issue.get('message', '')}\n"
                report += f"- **建议**: 建议修复以提高代码质量\n\n"
        
        # 代码质量建议
        report += "## 💡 代码质量建议\n\n"
        
        # 根据问题类型给出建议
        issue_types = set(issue.get('type', 'unknown') for issue in issues)
        
        if 'unhandled_exception' in issue_types:
            report += "- **异常处理**: 建议添加try-catch块来处理可能的异常\n"
        
        if 'potential_division_by_zero' in issue_types:
            report += "- **除零检查**: 建议在除法操作前检查除数是否为零\n"
        
        if 'unused_import' in issue_types:
            report += "- **代码清理**: 建议移除未使用的导入语句\n"
        
        if 'missing_docstring' in issue_types:
            report += "- **文档化**: 建议为函数和类添加文档字符串\n"
        
        if 'hardcoded_secrets' in issue_types:
            report += "- **安全性**: 建议将硬编码的密钥移到环境变量或配置文件中\n"
        
        report += "\n## 📊 总结\n\n"
        
        if len(error_issues) > 0:
            report += f"发现 {len(error_issues)} 个严重问题需要立即修复。\n"
        
        if len(warning_issues) > 0:
            report += f"发现 {len(warning_issues)} 个警告问题建议修复。\n"
        
        if len(info_issues) > 0:
            report += f"发现 {len(info_issues)} 个信息提示可以改进。\n"
        
        report += "\n建议按优先级逐步修复这些问题，以提高代码质量和可维护性。\n"
        
        return report
        
    except Exception as e:
        return f"# AI分析报告\n\n## 错误\n\n生成AI报告时发生错误: {str(e)}\n"

def categorize_issues_by_priority(issues):
    """按优先级分类问题"""
    priority_categories = {
        "critical": [],  # 错误级别，安全相关
        "high": [],      # 错误级别，非安全相关
        "medium": [],    # 警告级别
        "low": []        # 信息级别
    }
    
    for issue in issues:
        severity = issue.get("severity", "info")
        issue_type = issue.get("type", "")
        
        # 安全相关问题优先级最高
        if severity == "error" and any(keyword in issue_type.lower() for keyword in 
                                      ["security", "vulnerability", "injection", "xss", "csrf", "secret", "password"]):
            priority_categories["critical"].append(issue)
        elif severity == "error":
            priority_categories["high"].append(issue)
        elif severity == "warning":
            priority_categories["medium"].append(issue)
        else:
            priority_categories["low"].append(issue)
    
    return priority_categories

def generate_fix_recommendations(issues):
    """生成修复建议"""
    recommendations = {
        "immediate_actions": [],
        "short_term_improvements": [],
        "long_term_optimizations": []
    }
    
    error_count = sum(1 for issue in issues if issue.get("severity") == "error")
    warning_count = sum(1 for issue in issues if issue.get("severity") == "warning")
    
    # 立即行动
    if error_count > 0:
        recommendations["immediate_actions"].append(f"修复 {error_count} 个错误级别的问题")
    
    # 安全相关问题
    security_issues = [issue for issue in issues if "security" in issue.get("type", "").lower()]
    if security_issues:
        recommendations["immediate_actions"].append(f"优先处理 {len(security_issues)} 个安全问题")
    
    # 短期改进
    if warning_count > 10:
        recommendations["short_term_improvements"].append("进行代码审查，处理大量警告")
    
    # 长期优化
    recommendations["long_term_optimizations"].append("建立持续集成流程，定期进行代码质量检查")
    recommendations["long_term_optimizations"].append("制定代码规范和最佳实践指南")
    
    return recommendations

def analyze_project_structure(detection_results, analysis_type):
    """分析项目结构"""
    structure_info = {
        "analysis_type": analysis_type,
        "file_count": detection_results.get("total_files", 1),
        "languages": detection_results.get("languages_detected", []),
        "complexity_indicators": {
            "high_issue_files": 0,
            "average_issues_per_file": 0
        }
    }
    
    issues = detection_results.get("issues", [])
    if issues:
        # 统计每个文件的问题数量
        file_issue_count = {}
        for issue in issues:
            file_name = issue.get("file", "unknown")
            file_issue_count[file_name] = file_issue_count.get(file_name, 0) + 1
        
        # 计算高问题文件数量
        structure_info["complexity_indicators"]["high_issue_files"] = sum(
            1 for count in file_issue_count.values() if count > 5
        )
        
        # 计算平均问题数
        total_files = len(file_issue_count) or 1
        structure_info["complexity_indicators"]["average_issues_per_file"] = len(issues) / total_files
    
    return structure_info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)