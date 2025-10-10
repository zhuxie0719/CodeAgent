"""
AI Agent 系统主入口
统一管理所有 Agent、Coordinator 和路由
"""

import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent))

# 导入核心管理器
from core.agent_manager import AgentManager
from core.coordinator_manager import CoordinatorManager

# 导入各个 API 模块
# 注意：这些文件需要改为使用 APIRouter
# 目前我们先创建基础框架，后续再逐步迁移


# 数据模型
class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    message: str = Field(..., description="状态消息")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="时间戳")
    data: Optional[Dict[str, Any]] = Field(None, description="详细信息")


# 创建 FastAPI 应用
app = FastAPI(
    title="AI Agent 代码分析系统",
    description="多 Agent 协作的代码检测、分析和优化平台",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局管理器
agent_manager = None
coordinator_manager = None


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    global agent_manager, coordinator_manager
    
    print("\n" + "="*60)
    print("🚀 AI Agent 系统启动中...")
    print("="*60)
    
    # 1. 启动 Coordinator
    try:
        coordinator_manager = CoordinatorManager()
        await coordinator_manager.start()
    except Exception as e:
        print(f"❌ Coordinator 启动失败: {e}")
        import traceback
        traceback.print_exc()
        coordinator_manager = None
    
    # 2. 启动所有 Agent
    try:
        if coordinator_manager and coordinator_manager.coordinator:
            agent_manager = AgentManager(coordinator_manager.coordinator)
            await agent_manager.start_all_agents()
        else:
            print("⚠️  跳过 Agent 启动（Coordinator 未启动）")
    except Exception as e:
        print(f"❌ Agent 启动失败: {e}")
        import traceback
        traceback.print_exc()
        agent_manager = None
    
    # 3. 挂载各个子模块的路由
    try:
        # 导入并设置 coordinator_api 的全局管理器
        import coordinator_api
        coordinator_api.set_managers(coordinator_manager, agent_manager)
        app.include_router(coordinator_api.router)
        print("✅ Coordinator API 路由已挂载")
    except Exception as e:
        print(f"⚠️  挂载 Coordinator API 失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 挂载代码质量分析 API
    try:
        import code_quality_api
        code_quality_api.set_agent_manager(agent_manager)
        app.include_router(code_quality_api.router)
        print("✅ Code Quality API 路由已挂载")
    except Exception as e:
        print(f"⚠️  挂载 Code Quality API 失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 挂载代码分析 API
    try:
        import code_analysis_api
        code_analysis_api.set_agent_manager(agent_manager)
        app.include_router(code_analysis_api.router)
        print("✅ Code Analysis API 路由已挂载")
    except Exception as e:
        print(f"⚠️  挂载 Code Analysis API 失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 挂载缺陷检测 API
    try:
        import bug_detection_api
        bug_detection_api.set_managers(coordinator_manager, agent_manager)
        app.include_router(bug_detection_api.router)
        print("✅ Bug Detection API 路由已挂载")
    except Exception as e:
        print(f"⚠️  挂载 Bug Detection API 失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 打印启动总结
    print("\n" + "="*60)
    print("🎉 系统启动完成！")
    if agent_manager:
        print(f"✅ 活跃 Agent: {agent_manager.active_count} 个")
        for agent_id in agent_manager.get_all_agents().keys():
            print(f"   - {agent_id}")
    else:
        print("⚠️  没有活跃的 Agent")
    
    if coordinator_manager and coordinator_manager.coordinator:
        print(f"✅ Coordinator: 运行中")
    else:
        print("⚠️  Coordinator 未运行")
    
    print(f"📍 API 文档: http://localhost:8001/docs")
    print(f"📍 健康检查: http://localhost:8001/health")
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    global agent_manager, coordinator_manager
    
    print("\n" + "="*60)
    print("👋 AI Agent 系统正在关闭...")
    print("="*60)
    
    # 停止所有 Agent
    if agent_manager:
        await agent_manager.stop_all_agents()
    
    # 停止 Coordinator
    if coordinator_manager:
        await coordinator_manager.stop()
    
    print("="*60)
    print("🎉 系统已安全关闭")
    print("="*60 + "\n")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    global agent_manager, coordinator_manager
    
    # 收集系统状态
    agents_status = agent_manager.get_status() if agent_manager else {}
    coordinator_status = coordinator_manager.get_status() if coordinator_manager else {"status": "stopped"}
    
    # 判断整体健康状态
    is_healthy = (
        coordinator_status.get("status") == "running" and
        agent_manager and 
        agent_manager.active_count > 0
    )
    
    return HealthResponse(
        status="ok" if is_healthy else "degraded",
        message="系统运行正常" if is_healthy else "部分服务未启动",
        data={
            "coordinator": coordinator_status,
            "agents": {
                "total": agent_manager.active_count if agent_manager else 0,
                "details": agents_status
            }
        }
    )


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI Agent 代码分析系统 API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "协调中心": {
                "任务状态": "GET /api/v1/tasks/{task_id}",
                "Agent列表": "GET /api/v1/agents",
                "Coordinator状态": "GET /api/v1/coordinator/status"
            },
            "缺陷检测": {
                "上传检测": "POST /api/v1/detection/upload",
                "AI报告": "GET /api/v1/ai-reports/{task_id}",
                "下载报告": "GET /api/v1/reports/{task_id}"
            },
            "代码质量": {
                "上传分析": "POST /api/code-quality/analyze-upload"
            },
            "代码分析": {
                "项目分析": "POST /api/code-analysis/analyze",
                "上传分析": "POST /api/code-analysis/analyze-upload"
            }
        },
        "status": {
            "agents": agent_manager.active_count if agent_manager else 0,
            "coordinator": "running" if coordinator_manager and coordinator_manager.coordinator else "stopped"
        }
    }

