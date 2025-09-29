"""
多Agent协作平台统一API接口
提供Agent管理和任务调度功能
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# 添加项目根目录到Python路径
import sys
sys.path.append(str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent, AgentStatus, TaskStatus
from agents.bug_detection_agent.agent import BugDetectionAgent
from agents.code_analysis_agent.agent import CodeAnalysisAgent
from agents.fix_execution_agent.agent import FixExecutionAgent
from agents.test_validation_agent.agent import TestValidationAgent
from agents.performance_optimization_agent.agent import PerformanceOptimizationAgent
from agents.code_quality_agent.agent import CodeQualityAgent
from config.settings import settings


# 数据模型
class AgentInfo(BaseModel):
    """Agent信息模型"""
    agent_id: str = Field(..., description="Agent ID")
    status: str = Field(..., description="Agent状态")
    capabilities: List[str] = Field(..., description="Agent能力列表")
    metrics: Dict[str, Any] = Field(..., description="Agent指标")


class TaskInfo(BaseModel):
    """任务信息模型"""
    task_id: str = Field(..., description="任务ID")
    agent_id: str = Field(..., description="分配的Agent ID")
    status: str = Field(..., description="任务状态")
    created_at: str = Field(..., description="创建时间")
    started_at: Optional[str] = Field(None, description="开始时间")
    completed_at: Optional[str] = Field(None, description="完成时间")
    result: Optional[Dict[str, Any]] = Field(None, description="任务结果")
    error: Optional[str] = Field(None, description="错误信息")


class DetectionRequest(BaseModel):
    """检测请求模型"""
    file_path: Optional[str] = Field(None, description="文件路径")
    project_path: Optional[str] = Field(None, description="项目路径")
    options: Dict[str, Any] = Field(default_factory=dict, description="检测选项")


class DetectionResult(BaseModel):
    """检测结果模型"""
    task_id: str = Field(..., description="任务ID")
    success: bool = Field(..., description="是否成功")
    detection_results: Optional[Dict[str, Any]] = Field(None, description="检测结果")
    report: Optional[Dict[str, Any]] = Field(None, description="检测报告")
    error: Optional[str] = Field(None, description="错误信息")
    timestamp: str = Field(..., description="时间戳")


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(True, description="是否成功")
    message: str = Field("操作成功", description="响应消息")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")


class AgentManager:
    """Agent管理器"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """初始化所有Agent"""
        agent_configs = {
            "bug_detection_agent": BugDetectionAgent,
            "code_analysis_agent": CodeAnalysisAgent,
            "fix_execution_agent": FixExecutionAgent,
            "test_validation_agent": TestValidationAgent,
            "performance_optimization_agent": PerformanceOptimizationAgent,
            "code_quality_agent": CodeQualityAgent
        }
        
        for agent_id, agent_class in agent_configs.items():
            config = settings.AGENTS.get(agent_id, {})
            if config.get("enabled", True):
                agent = agent_class(config)
                self.agents[agent_id] = agent
    
    async def start_all_agents(self):
        """启动所有Agent"""
        for agent in self.agents.values():
            await agent.start()
    
    async def stop_all_agents(self):
        """停止所有Agent"""
        for agent in self.agents.values():
            await agent.stop()
    
    async def get_agent_status(self, agent_id: str) -> Optional[AgentInfo]:
        """获取Agent状态"""
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        
        metrics = await agent.get_metrics()
        return AgentInfo(
            agent_id=agent_id,
            status=agent.status.value,
            capabilities=agent.get_capabilities(),
            metrics=metrics
        )
    
    async def get_all_agents_status(self) -> List[AgentInfo]:
        """获取所有Agent状态"""
        agents_info = []
        for agent_id in self.agents.keys():
            agent_info = await self.get_agent_status(agent_id)
            if agent_info:
                agents_info.append(agent_info)
        return agents_info
    
    async def submit_task(self, agent_id: str, task_data: Dict[str, Any]) -> str:
        """提交任务"""
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} 不存在")
        
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        
        # 提交任务到Agent
        success = await agent.submit_task(task_id, task_data)
        if not success:
            raise RuntimeError(f"提交任务到Agent {agent_id} 失败")
        
        # 记录任务信息
        self.tasks[task_id] = {
            "task_id": task_id,
            "agent_id": agent_id,
            "status": TaskStatus.PENDING,
            "created_at": datetime.now(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None
        }
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[TaskInfo]:
        """获取任务状态"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        # 从Agent获取最新状态
        agent = self.agents.get(task["agent_id"])
        if agent:
            agent_task_status = await agent.get_task_status(task_id)
            if agent_task_status:
                task.update(agent_task_status)
        
        return TaskInfo(
            task_id=task["task_id"],
            agent_id=task["agent_id"],
            status=task["status"],
            created_at=task["created_at"].isoformat(),
            started_at=task["started_at"].isoformat() if task["started_at"] else None,
            completed_at=task["completed_at"].isoformat() if task["completed_at"] else None,
            result=task["result"],
            error=task["error"]
        )


# 创建FastAPI应用
app = FastAPI(
    title="AI Agent 协作平台 API",
    description="多Agent协作的智能软件开发系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.SECURITY["cors_origins"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局Agent管理器
agent_manager = AgentManager()


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    await agent_manager.start_all_agents()


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    await agent_manager.stop_all_agents()


@app.get("/health", response_model=BaseResponse)
async def health_check():
    """健康检查接口"""
    agents_status = await agent_manager.get_all_agents_status()
    active_agents = len([a for a in agents_status if a.status == "running"])
    
    return BaseResponse(
        message="系统运行正常",
        data={
            "total_agents": len(agents_status),
            "active_agents": active_agents,
            "agents_status": [a.model_dump() for a in agents_status]
        }
    )


@app.get("/api/v1/agents", response_model=BaseResponse)
async def get_all_agents():
    """获取所有Agent状态"""
    agents_status = await agent_manager.get_all_agents_status()
    
    return BaseResponse(
        message="获取Agent状态成功",
        data={
            "agents": [a.model_dump() for a in agents_status],
            "total_agents": len(agents_status)
        }
    )


@app.get("/api/v1/agents/{agent_id}", response_model=BaseResponse)
async def get_agent_status(agent_id: str):
    """获取指定Agent状态"""
    agent_info = await agent_manager.get_agent_status(agent_id)
    if not agent_info:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} 不存在")
    
    return BaseResponse(
        message="获取Agent状态成功",
        data=agent_info.model_dump()
    )


@app.post("/api/v1/detection/upload", response_model=BaseResponse)
async def upload_file_for_detection(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    enable_static: bool = Query(True, description="启用自定义静态检测"),
    enable_pylint: bool = Query(True, description="启用Pylint检测"),
    enable_flake8: bool = Query(True, description="启用Flake8检测")
):
    """上传文件进行缺陷检测"""
    
    # 验证文件类型
    if not file.filename.endswith('.py'):
        raise HTTPException(status_code=400, detail="只支持Python文件(.py)")
    
    # 验证文件大小
    content = await file.read()
    file_size = len(content)
    
    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=413, detail="文件过大，最大支持10MB")
    
    # 保存文件
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / f"{file.filename}"
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # 创建检测任务
    task_data = {
        "file_path": str(file_path),
        "options": {
            "enable_static": enable_static,
            "enable_pylint": enable_pylint,
            "enable_flake8": enable_flake8
        }
    }
    
    try:
        task_id = await agent_manager.submit_task("bug_detection_agent", task_data)
        
        return BaseResponse(
            message="文件上传成功，开始检测",
            data={
                "task_id": task_id,
                "filename": file.filename,
                "file_size": file_size,
                "agent_id": "bug_detection_agent"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交检测任务失败: {str(e)}")


@app.post("/api/v1/detection/project", response_model=BaseResponse)
async def detect_project(
    background_tasks: BackgroundTasks,
    request: DetectionRequest
):
    """检测整个项目"""
    
    if not request.project_path:
        raise HTTPException(status_code=400, detail="缺少项目路径")
    
    # 创建检测任务
    task_data = {
        "project_path": request.project_path,
        "options": request.options
    }
    
    try:
        task_id = await agent_manager.submit_task("bug_detection_agent", task_data)
        
        return BaseResponse(
            message="项目检测任务已提交",
            data={
                "task_id": task_id,
                "project_path": request.project_path,
                "agent_id": "bug_detection_agent"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交项目检测任务失败: {str(e)}")


@app.get("/api/v1/tasks/{task_id}", response_model=BaseResponse)
async def get_task_status(task_id: str):
    """获取任务状态"""
    task_info = await agent_manager.get_task_status(task_id)
    if not task_info:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return BaseResponse(
        message="获取任务状态成功",
        data=task_info.model_dump()
    )


@app.get("/api/v1/detection/rules", response_model=BaseResponse)
async def get_detection_rules():
    """获取检测规则"""
    bug_agent = agent_manager.agents.get("bug_detection_agent")
    if not bug_agent:
        raise HTTPException(status_code=404, detail="缺陷检测Agent不存在")
    
    try:
        rules = await bug_agent.get_detection_rules()
        
        return BaseResponse(
            message="获取检测规则成功",
            data=rules
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取检测规则失败: {str(e)}")


@app.get("/api/v1/tasks", response_model=BaseResponse)
async def get_all_tasks(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态过滤")
):
    """获取所有任务"""
    
    # 过滤任务
    filtered_tasks = []
    for task in agent_manager.tasks.values():
        if status is None or task["status"].value == status:
            filtered_tasks.append(task)
    
    # 按创建时间倒序排序
    filtered_tasks.sort(key=lambda x: x["created_at"], reverse=True)
    
    # 分页
    total = len(filtered_tasks)
    start = (page - 1) * limit
    end = start + limit
    page_tasks = filtered_tasks[start:end]
    
    # 格式化任务信息
    tasks_info = []
    for task in page_tasks:
        tasks_info.append({
            "task_id": task["task_id"],
            "agent_id": task["agent_id"],
            "status": task["status"].value,
            "created_at": task["created_at"].isoformat(),
            "started_at": task["started_at"].isoformat() if task["started_at"] else None,
            "completed_at": task["completed_at"].isoformat() if task["completed_at"] else None
        })
    
    return BaseResponse(
        message="获取任务列表成功",
        data={
            "tasks": tasks_info,
            "total": total,
            "page": page,
            "limit": limit
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "agent_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
