"""
Coordinator 管理 API
处理任务状态查询、Agent 管理等 Coordinator 相关接口
从 bug_detection_api.py 分离出来
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["协调中心"])

# 全局引用（在 main_api.py 中设置）
_coordinator_manager = None
_agent_manager = None

def set_managers(coord_mgr, agent_mgr):
    """设置全局管理器引用"""
    global _coordinator_manager, _agent_manager
    _coordinator_manager = coord_mgr
    _agent_manager = agent_mgr


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(True, description="是否成功")
    message: str = Field("操作成功", description="响应消息")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")


@router.get("/tasks/{task_id}", response_model=BaseResponse)
async def get_task_status(task_id: str):
    """获取任务状态"""
    if not _coordinator_manager or not _coordinator_manager.coordinator:
        raise HTTPException(status_code=500, detail="Coordinator 未启动")
    
    coordinator = _coordinator_manager.coordinator
    
    try:
        task = coordinator.task_manager.tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 安全获取状态值
        status_value = task['status'].value if hasattr(task['status'], 'value') else str(task['status'])
        
        # 安全转换时间戳
        def safe_isoformat(dt):
            if dt is None:
                return None
            return dt.isoformat() if hasattr(dt, 'isoformat') else str(dt)
        
        data = {
            "task_id": task_id,
            "status": status_value,
            "type": task.get('type'),
            "created_at": safe_isoformat(task.get('created_at')),
            "started_at": safe_isoformat(task.get('started_at')),
            "completed_at": safe_isoformat(task.get('completed_at')),
            "assigned_agent": task.get('assigned_agent'),
            "result": task.get('result'),
            "error": task.get('error')
        }
        
        return BaseResponse(message="获取任务状态成功", data=data)
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")


@router.get("/agents", response_model=BaseResponse)
async def get_all_agents():
    """获取所有 Agent 状态"""
    if not _agent_manager:
        raise HTTPException(status_code=500, detail="AgentManager 未启动")
    
    try:
        agents_status = _agent_manager.get_status()
        
        return BaseResponse(
            message="获取 Agent 状态成功",
            data={
                "total_agents": _agent_manager.active_count,
                "agents": agents_status
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取 Agent 状态失败: {str(e)}")


@router.get("/agents/{agent_id}", response_model=BaseResponse)
async def get_agent_status(agent_id: str):
    """获取指定 Agent 状态"""
    if not _agent_manager:
        raise HTTPException(status_code=500, detail="AgentManager 未启动")
    
    try:
        agent = _agent_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} 不存在")
        
        return BaseResponse(
            message=f"获取 Agent {agent_id} 状态成功",
            data={
                "agent_id": agent_id,
                "status": "running",
                "type": type(agent).__name__
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取 Agent 状态失败: {str(e)}")


@router.get("/coordinator/status", response_model=BaseResponse)
async def get_coordinator_status():
    """获取 Coordinator 状态"""
    if not _coordinator_manager:
        raise HTTPException(status_code=500, detail="CoordinatorManager 未启动")
    
    try:
        status = _coordinator_manager.get_status()
        
        return BaseResponse(
            message="获取 Coordinator 状态成功",
            data=status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取 Coordinator 状态失败: {str(e)}")


@router.post("/tasks/{task_id}/cancel", response_model=BaseResponse)
async def cancel_task(task_id: str):
    """取消任务（预留功能）"""
    if not _coordinator_manager or not _coordinator_manager.coordinator:
        raise HTTPException(status_code=500, detail="Coordinator 未启动")
    
    try:
        # TODO: 实现任务取消逻辑
        return BaseResponse(
            message="任务取消功能开发中",
            data={"task_id": task_id}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(e)}")

