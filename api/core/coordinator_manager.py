"""
Coordinator 管理器
管理协调中心的生命周期
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from coordinator.coordinator import Coordinator


class CoordinatorManager:
    """Coordinator 管理器"""
    
    def __init__(self):
        self.coordinator = None
    
    async def start(self):
        """启动 Coordinator"""
        print("🎯 初始化 Coordinator...")
        self.coordinator = Coordinator(config={})
        await self.coordinator.start()
        print("✅ Coordinator 启动成功")
    
    async def stop(self):
        """停止 Coordinator"""
        if self.coordinator:
            await self.coordinator.stop()
            print("✅ Coordinator 已停止")
    
    def get_status(self):
        """获取 Coordinator 状态"""
        if not self.coordinator:
            return {"status": "stopped"}
        
        return {
            "status": "running",
            "registered_agents": len(self.coordinator.agents) if hasattr(self.coordinator, 'agents') else 0,
            "task_manager": {
                "total_tasks": len(self.coordinator.task_manager.tasks),
                "pending_tasks": len([
                    t for t in self.coordinator.task_manager.tasks.values()
                    if t['status'].value == 'pending'
                ])
            } if hasattr(self.coordinator, 'task_manager') else {}
        }

