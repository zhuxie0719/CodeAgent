"""
AI AGENT系统主程序入口
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from config.settings import settings
from coordinator.coordinator import Coordinator
from agents.code_analysis_agent.agent import CodeAnalysisAgent
from agents.bug_detection_agent.agent import BugDetectionAgent
from agents.fix_execution_agent.agent import FixExecutionAgent
from agents.test_validation_agent.agent import TestValidationAgent
from agents.performance_optimization_agent.agent import PerformanceOptimizationAgent
from agents.code_quality_agent.agent import CodeQualityAgent


class AIAgentSystem:
    """AI AGENT系统主类"""
    
    def __init__(self):
        self.coordinator = Coordinator(settings.dict())
        self.agents = {}
        self.is_running = False
    
    async def initialize(self):
        """初始化系统"""
        print("正在初始化AI AGENT系统...")
        
        # 创建AGENT实例
        self.agents = {
            'code_analysis_agent': CodeAnalysisAgent(settings.AGENTS['code_analysis_agent']),
            'bug_detection_agent': BugDetectionAgent(settings.AGENTS['bug_detection_agent']),
            'fix_execution_agent': FixExecutionAgent(settings.AGENTS['fix_execution_agent']),
            'test_validation_agent': TestValidationAgent(settings.AGENTS['test_validation_agent']),
            'performance_optimization_agent': PerformanceOptimizationAgent(settings.AGENTS['performance_optimization_agent']),
            'code_quality_agent': CodeQualityAgent(settings.AGENTS['code_quality_agent'])
        }
        
        # 注册AGENT到协调中心
        for agent_id, agent in self.agents.items():
            await self.coordinator.register_agent(agent_id, agent)
        
        print("AI AGENT系统初始化完成")
    
    async def start(self):
        """启动系统"""
        if self.is_running:
            print("系统已在运行中")
            return
        
        print("正在启动AI AGENT系统...")
        
        # 启动协调中心
        await self.coordinator.start()
        
        # 启动所有AGENT
        for agent_id, agent in self.agents.items():
            if settings.AGENTS[agent_id]['enabled']:
                await agent.start()
                print(f"{agent_id} 已启动")
        
        self.is_running = True
        print("AI AGENT系统启动完成")
    
    async def stop(self):
        """停止系统"""
        if not self.is_running:
            print("系统未运行")
            return
        
        print("正在停止AI AGENT系统...")
        
        # 停止所有AGENT
        for agent_id, agent in self.agents.items():
            await agent.stop()
            print(f"{agent_id} 已停止")
        
        # 停止协调中心
        await self.coordinator.stop()
        
        self.is_running = False
        print("AI AGENT系统已停止")
    
    async def process_project(self, project_path: str):
        """处理项目"""
        if not self.is_running:
            print("系统未运行，请先启动系统")
            return
        
        print(f"开始处理项目: {project_path}")
        
        try:
            result = await self.coordinator.process_workflow(project_path)
            
            if result['success']:
                print("项目处理完成")
                print(f"分析结果: {result.get('analysis', {})}")
                print(f"检测结果: {result.get('detection', {})}")
                if 'fix' in result:
                    print(f"修复结果: {result.get('fix', {})}")
                if 'validation' in result:
                    print(f"验证结果: {result.get('validation', {})}")
            else:
                print(f"项目处理失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"处理项目时发生错误: {e}")


async def main():
    """主函数"""
    system = AIAgentSystem()
    
    try:
        # 初始化系统
        await system.initialize()
        
        # 启动系统
        await system.start()
        
        # 处理项目（这里可以替换为实际的项目路径）
        project_path = input("请输入项目路径: ").strip()
        if project_path:
            await system.process_project(project_path)
        
        # 保持系统运行
        print("系统正在运行中，按 Ctrl+C 停止...")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n收到停止信号")
    except Exception as e:
        print(f"系统运行错误: {e}")
    finally:
        # 停止系统
        await system.stop()


if __name__ == "__main__":
    asyncio.run(main())
