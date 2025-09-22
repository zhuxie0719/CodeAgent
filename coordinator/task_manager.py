"""
任务管理器
"""

import asyncio
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime


class TaskManager:
    """任务管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tasks = {}
        self.task_queue = asyncio.Queue()
        self.is_running = False
    
    async def start(self):
        """启动任务管理器"""
        self.is_running = True
        asyncio.create_task(self._process_tasks())
        print("任务管理器已启动")
    
    async def stop(self):
        """停止任务管理器"""
        self.is_running = False
        print("任务管理器已停止")
    
    async def create_task(self, task_type: str, task_data: Dict[str, Any]) -> str:
        """创建任务"""
        task_id = str(uuid.uuid4())
        task = {
            'id': task_id,
            'type': task_type,
            'data': task_data,
            'status': 'pending',
            'assigned_agent': None,
            'created_at': datetime.now(),
            'started_at': None,
            'completed_at': None,
            'result': None,
            'error': None
        }
        
        self.tasks[task_id] = task
        await self.task_queue.put(task_id)
        
        print(f"任务 {task_id} 已创建")
        return task_id
    
    async def assign_task(self, task_id: str, agent_id: str):
        """分配任务"""
        if task_id in self.tasks:
            self.tasks[task_id]['assigned_agent'] = agent_id
            self.tasks[task_id]['status'] = 'assigned'
            print(f"任务 {task_id} 已分配给 {agent_id}")
    
    async def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务结果"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task['status'] == 'completed':
                return task['result']
            elif task['status'] == 'failed':
                return {'error': task['error']}
            else:
                # 等待任务完成
                while task['status'] in ['pending', 'assigned', 'running']:
                    await asyncio.sleep(0.1)
                
                if task['status'] == 'completed':
                    return task['result']
                else:
                    return {'error': task['error']}
        return None
    
    async def _process_tasks(self):
        """处理任务队列"""
        while self.is_running:
            try:
                task_id = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                task = self.tasks[task_id]
                
                if task['status'] == 'assigned':
                    # 这里应该调用相应的AGENT执行任务
                    # 暂时模拟任务执行
                    await self._simulate_task_execution(task_id)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"任务处理错误: {e}")
    
    async def _simulate_task_execution(self, task_id: str):
        """模拟任务执行"""
        task = self.tasks[task_id]
        task['status'] = 'running'
        task['started_at'] = datetime.now()
        
        # 模拟任务执行时间
        await asyncio.sleep(1)
        
        # 模拟任务结果
        task['status'] = 'completed'
        task['completed_at'] = datetime.now()
        task['result'] = {
            'task_id': task_id,
            'type': task['type'],
            'success': True,
            'message': f"任务 {task['type']} 执行完成"
        }
        
        print(f"任务 {task_id} 执行完成")
