"""
Agent 生命周期管理器
统一管理所有 Agent 的启动、停止和注册
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from agents.bug_detection_agent.agent import BugDetectionAgent
from agents.fix_execution_agent.agent import FixExecutionAgent
from agents.code_analysis_agent.agent import CodeAnalysisAgent
from agents.code_quality_agent.agent import CodeQualityAgent
from agents.test_validation_agent.agent import TestValidationAgent


class AgentManager:
    """Agent 管理器"""
    
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.agents = {}
        
    async def start_all_agents(self):
        """启动所有可用的 Agent"""
        
        # 检查是否启用Docker支持
        use_docker = os.getenv("USE_DOCKER", "false").lower() == "true"
        
        # 定义要启动的 Agent（只包含可用的）
        agent_configs = [
            ("bug_detection_agent", BugDetectionAgent, "📦", "缺陷检测", {"use_docker": use_docker}),
            ("fix_execution_agent", FixExecutionAgent, "🔧", "自动修复", {}),
            ("test_validation_agent", TestValidationAgent, "🧪", "测试验证", {}),
            ("code_analysis_agent", CodeAnalysisAgent, "📊", "代码分析", {}),
            ("code_quality_agent", CodeQualityAgent, "⭐", "代码质量", {}),
        ]
        
        print("\n" + "="*60)
        print("🚀 启动所有 Agent...")
        print("="*60)
        
        for agent_id, agent_class, icon, description, config in agent_configs:
            try:
                print(f"{icon} 初始化 {agent_id} ({description})...")
                agent = agent_class(config=config)
                await agent.start()
                
                # 注册到 Coordinator
                if self.coordinator:
                    await self.coordinator.register_agent(agent_id, agent)
                
                self.agents[agent_id] = agent
                print(f"✅ {agent_id} 启动并注册成功")
                
            except Exception as e:
                print(f"⚠️  {agent_id} 启动失败: {e}")
                import traceback
                traceback.print_exc()
    
    async def stop_all_agents(self):
        """停止所有 Agent"""
        import asyncio
        
        print("\n" + "="*60)
        print("👋 停止所有 Agent...")
        print("="*60)
        
        for agent_id, agent in self.agents.items():
            try:
                # 为每个agent的停止操作添加超时保护
                await asyncio.wait_for(
                    agent.stop(),
                    timeout=5.0  # 每个agent最多等待5秒
                )
                print(f"✅ {agent_id} 已停止")
            except asyncio.TimeoutError:
                print(f"⚠️  {agent_id} 停止超时，跳过")
            except Exception as e:
                print(f"⚠️  {agent_id} 停止失败: {e}")
                import traceback
                traceback.print_exc()
    
    @property
    def active_count(self):
        """活跃的 Agent 数量"""
        return len(self.agents)
    
    def get_agent(self, agent_id: str):
        """获取指定 Agent"""
        return self.agents.get(agent_id)
    
    def get_all_agents(self):
        """获取所有 Agent"""
        return self.agents
    
    def get_status(self):
        """获取所有 Agent 状态"""
        return {
            agent_id: {
                "status": "running",
                "type": type(agent).__name__
            }
            for agent_id, agent in self.agents.items()
        }

