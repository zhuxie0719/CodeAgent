"""
协调中心主类
"""

import asyncio
from typing import Dict, List, Any, Optional
from .task_manager import TaskManager
from .event_bus import EventBus
from .decision_engine import DecisionEngine


class Coordinator:
    """协调中心"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.task_manager = TaskManager(config)
        self.event_bus = EventBus(config)
        self.decision_engine = DecisionEngine(config)
        self.agents = {}
        self.is_running = False
    
    async def start(self):
        """启动协调中心"""
        self.is_running = True
        await self.task_manager.start()
        await self.event_bus.start()
        await self.decision_engine.start()
        print("协调中心已启动")
    
    async def stop(self):
        """停止协调中心"""
        self.is_running = False
        await self.task_manager.stop()
        await self.event_bus.stop()
        await self.decision_engine.stop()
        print("协调中心已停止")
    
    async def register_agent(self, agent_id: str, agent):
        """注册AGENT"""
        self.agents[agent_id] = agent
        print(f"AGENT {agent_id} 已注册")
    
    async def unregister_agent(self, agent_id: str):
        """注销AGENT"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            print(f"AGENT {agent_id} 已注销")
    
    async def create_task(self, task_type: str, task_data: Dict[str, Any]) -> str:
        """创建任务"""
        task_id = await self.task_manager.create_task(task_type, task_data)
        return task_id
    
    async def assign_task(self, task_id: str, agent_id: str):
        """分配任务给AGENT"""
        if agent_id in self.agents:
            await self.task_manager.assign_task(task_id, agent_id)
            print(f"任务 {task_id} 已分配给 {agent_id}")
        else:
            print(f"AGENT {agent_id} 不存在")
    
    async def process_workflow(self, project_path: str) -> Dict[str, Any]:
        """处理完整的工作流"""
        try:
            # 1. 创建分析任务
            analysis_task_id = await self.create_task('analyze', {'project_path': project_path})
            
            # 2. 分配给代码分析AGENT
            await self.assign_task(analysis_task_id, 'code_analysis_agent')
            
            # 3. 等待分析完成
            analysis_result = await self.task_manager.get_task_result(analysis_task_id)
            
            # 4. 创建缺陷检测任务
            detection_task_id = await self.create_task('detect_bugs', {
                'project_path': project_path,
                'analysis_result': analysis_result
            })
            # 5. 分配给缺陷检测AGENT
            await self.assign_task(detection_task_id, 'bug_detection_agent')
            
            # 6. 等待检测完成
            detection_result = await self.task_manager.get_task_result(detection_task_id)
            # 7. 根据检测结果决定是否需要修复
            if detection_result.get('total_issues', 0) > 0:
                # 创建修复任务
                fix_task_id = await self.create_task('fix_issues', {
                    'project_path': project_path,
                    'issues': detection_result.get('issues', [])
                })
                # 分配给修复执行AGENT
                await self.assign_task(fix_task_id, 'fix_execution_agent')
                
                # 等待修复完成
                fix_result = await self.task_manager.get_task_result(fix_task_id)
                
                # 创建验证任务
                validation_task_id = await self.create_task('validate_fix', {
                    'project_path': project_path,
                    'fix_result': fix_result
                })
                
                # 分配给测试验证AGENT
                await self.assign_task(validation_task_id, 'test_validation_agent')
                
                # 等待验证完成
                validation_result = await self.task_manager.get_task_result(validation_task_id)
                
                return {
                    'analysis': analysis_result,
                    'detection': detection_result,
                    'fix': fix_result,
                    'validation': validation_result,
                    'success': validation_result.get('passed', False)
                }
            else:
                return {
                    'analysis': analysis_result,
                    'detection': detection_result,
                    'message': '未发现需要修复的问题',
                    'success': True
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
