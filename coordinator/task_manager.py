"""
任务管理器
负责任务创建、分配、执行和状态管理
"""

import asyncio
import uuid
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

from .message_types import TaskStatus, TaskMessage, ResultMessage, MessageFactory


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class TaskManager:
    """任务管理器 - 负责任务调度和状态管理"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tasks = {}
        self.task_queue = asyncio.PriorityQueue()
        self.agent_loads = {}  # agent_id -> current_load
        self.is_running = False
        self.logger = logging.getLogger(__name__)
        
        # 任务处理配置
        self.max_concurrent_tasks = config.get("max_concurrent_tasks", 10)
        self.task_timeout = config.get("task_timeout", 300)
        self.retry_attempts = config.get("retry_attempts", 3)
        
        # 统计信息
        self.stats = {
            "tasks_created": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_retried": 0,
            "average_completion_time": 0.0
        }
    
    async def start(self):
        """启动任务管理器"""
        self.is_running = True
        self.logger.info("任务管理器启动中...")
        
        # 启动任务处理循环
        asyncio.create_task(self._process_tasks())
        
        # 启动负载监控
        asyncio.create_task(self._monitor_agent_loads())
        
        self.logger.info("任务管理器已启动")
    
    async def stop(self):
        """停止任务管理器"""
        self.is_running = False
        self.logger.info("任务管理器已停止")
    
    async def create_task(self, task_type: str, task_data: Dict[str, Any], 
                         priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """创建任务"""
        task_id = str(uuid.uuid4())
        task = {
            'id': task_id,
            'type': task_type,
            'data': task_data,
            'status': TaskStatus.PENDING,
            'assigned_agent': None,
            'priority': priority,
            'created_at': datetime.now(),
            'started_at': None,
            'completed_at': None,
            'result': None,
            'error': None,
            'retry_count': 0,
            'timeout_at': None
        }
        
        self.tasks[task_id] = task
        
        # 设置超时时间
        task['timeout_at'] = datetime.now().timestamp() + self.task_timeout
        
        # 添加到优先级队列
        await self.task_queue.put((priority.value, task_id))
        
        self.stats["tasks_created"] += 1
        self.logger.info(f"任务已创建: {task_id} (类型: {task_type}, 优先级: {priority.name})")
        
        return task_id
    
    async def assign_task(self, task_id: str, agent_id: str):
        """分配任务给Agent"""
        if task_id not in self.tasks:
            self.logger.error(f"任务不存在: {task_id}")
            return False
        
        task = self.tasks[task_id]
        task['assigned_agent'] = agent_id
        task['status'] = TaskStatus.ASSIGNED
        
        # 更新Agent负载
        self.agent_loads[agent_id] = self.agent_loads.get(agent_id, 0) + 1
        
        self.logger.info(f"任务 {task_id} 已分配给 {agent_id}")
        return True
    
    async def get_task_result(self, task_id: str, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """获取任务结果"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        
        # 如果任务已完成，直接返回结果
        if task['status'] == TaskStatus.COMPLETED:
            return task['result']
        elif task['status'] == TaskStatus.FAILED:
            return {'error': task['error'], 'success': False}
        
        # 等待任务完成
        start_time = datetime.now()
        timeout_seconds = timeout or self.task_timeout
        
        # 等待任务完成，包括PROCESSING状态
        while task['status'] in [TaskStatus.PENDING, TaskStatus.ASSIGNED, TaskStatus.RUNNING, TaskStatus.PROCESSING]:
            await asyncio.sleep(0.1)
            
            # 检查超时
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > timeout_seconds:
                self.logger.warning(f"获取任务结果超时: {task_id} (已等待 {elapsed:.1f}秒)")
                return {'error': 'Timeout waiting for task result', 'success': False}
            
            # 每10秒记录一次等待日志（避免日志过多）
            if int(elapsed) % 10 == 0 and elapsed > 0:
                self.logger.debug(f"等待任务完成: {task_id}, 状态: {task['status'].value}, 已等待: {elapsed:.1f}秒")
        
        # 返回最终结果
        if task['status'] == TaskStatus.COMPLETED:
            self.logger.info(f"任务完成: {task_id}, 耗时: {(datetime.now() - start_time).total_seconds():.2f}秒")
            return task['result']
        else:
            self.logger.warning(f"任务失败: {task_id}, 状态: {task['status'].value}, 错误: {task.get('error', 'Unknown error')}")
            return {'error': task.get('error', 'Unknown error'), 'success': False}
    
    async def update_task_result(self, task_id: str, result: Dict[str, Any], success: bool = True):
        """更新任务结果"""
        if task_id not in self.tasks:
            self.logger.error(f"任务不存在: {task_id}")
            return
        
        task = self.tasks[task_id]
        task['completed_at'] = datetime.now()
        task['result'] = result
        
        if success:
            task['status'] = TaskStatus.COMPLETED
            self.stats["tasks_completed"] += 1
            
            # 计算完成时间
            if task['started_at']:
                completion_time = (task['completed_at'] - task['started_at']).total_seconds()
                self._update_average_completion_time(completion_time)
        else:
            task['status'] = TaskStatus.FAILED
            task['error'] = result.get('error', 'Unknown error')
            self.stats["tasks_failed"] += 1
        
        # 更新Agent负载
        if task['assigned_agent']:
            agent_id = task['assigned_agent']
            if agent_id in self.agent_loads:
                self.agent_loads[agent_id] = max(0, self.agent_loads[agent_id] - 1)
        
        self.logger.info(f"任务结果已更新: {task_id} (成功: {success})")
    
    async def retry_task(self, task_id: str) -> bool:
        """重试失败的任务"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        if task['retry_count'] >= self.retry_attempts:
            self.logger.warning(f"任务重试次数已达上限: {task_id}")
            return False
        
        task['retry_count'] += 1
        task['status'] = TaskStatus.PENDING
        task['assigned_agent'] = None
        task['error'] = None
        
        # 重新加入队列
        await self.task_queue.put((task['priority'].value, task_id))
        
        self.stats["tasks_retried"] += 1
        self.logger.info(f"任务已重试: {task_id} (第 {task['retry_count']} 次)")
        
        return True
    
    async def _process_tasks(self):
        """处理任务队列"""
        self.logger.info("任务处理循环已启动")
        
        while self.is_running:
            try:
                # 从优先级队列获取任务
                priority, task_id = await asyncio.wait_for(
                    self.task_queue.get(), 
                    timeout=1.0
                )
                
                task = self.tasks[task_id]
                
                # 检查任务是否已超时
                if task.get('timeout_at') and datetime.now().timestamp() > task['timeout_at']:
                    self.logger.warning(f"任务已超时: {task_id}")
                    await self.update_task_result(task_id, {'error': 'Task timeout'}, False)
                    continue
                
                # 如果任务已分配但未执行，开始执行
                if task['status'] == TaskStatus.ASSIGNED:
                    await self._execute_task(task_id)
                
            except asyncio.TimeoutError:
                # 超时是正常的，继续循环
                continue
            except Exception as e:
                self.logger.error(f"任务处理错误: {e}")
    
    async def _execute_task(self, task_id: str):
        """执行任务"""
        task = self.tasks[task_id]
        task['status'] = TaskStatus.RUNNING
        task['started_at'] = datetime.now()

        agent_id = task['assigned_agent']
        task_type = task['type']
        task_data = task['data']

        self.logger.info(f"开始执行任务: {task_id} (Agent: {agent_id}, 类型: {task_type})")

        try:
            # 通过事件总线发送任务消息，实际执行由目标Agent完成
            from .event_bus import EventBus
            # 这里无法直接获取 EventBus 实例，实际发送由 Coordinator.assign_task 完成
            # TaskManager 在此仅推进状态，等待 Coordinator 侧回写结果
            pass

        except Exception as e:
            self.logger.error(f"任务执行失败: {task_id} - {e}")
            await self.update_task_result(task_id, {'error': str(e)}, False)
    
    async def _simulate_task_execution(self, task_id: str):
        """模拟任务执行（实际实现中应该调用真实的Agent）"""
        task = self.tasks[task_id]
        
        # 模拟任务执行时间
        await asyncio.sleep(1)
        
        # 模拟任务结果
        result = {
            'task_id': task_id,
            'type': task['type'],
            'success': True,
            'message': f"任务 {task['type']} 执行完成",
            'timestamp': datetime.now().isoformat()
        }
        
        await self.update_task_result(task_id, result, True)
    
    async def _monitor_agent_loads(self):
        """监控Agent负载"""
        while self.is_running:
            try:
                # 清理空闲Agent的负载计数
                for agent_id in list(self.agent_loads.keys()):
                    if self.agent_loads[agent_id] <= 0:
                        del self.agent_loads[agent_id]
                
                await asyncio.sleep(10)  # 每10秒监控一次
                
            except Exception as e:
                self.logger.error(f"Agent负载监控错误: {e}")
    
    def _update_average_completion_time(self, completion_time: float):
        """更新平均完成时间"""
        current_avg = self.stats["average_completion_time"]
        completed_count = self.stats["tasks_completed"]
        
        # 计算新的平均值
        new_avg = (current_avg * (completed_count - 1) + completion_time) / completed_count
        self.stats["average_completion_time"] = new_avg
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            "active_tasks": len([t for t in self.tasks.values() 
                               if t['status'] in [TaskStatus.PENDING, TaskStatus.ASSIGNED, TaskStatus.RUNNING]]),
            "queue_size": self.task_queue.qsize(),
            "agent_loads": self.agent_loads.copy()
        }
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        return {
            'task_id': task_id,
            'agent_id': task.get('assigned_agent'),
            'status': task['status'].value,
            'created_at': task['created_at'].isoformat(),
            'started_at': task.get('started_at').isoformat() if task.get('started_at') else None,
            'completed_at': task.get('completed_at').isoformat() if task.get('completed_at') else None,
            'result': task.get('result'),
            'error': task.get('error')
        }

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "is_running": self.is_running,
            "queue_size": self.task_queue.qsize(),
            "active_tasks": len([t for t in self.tasks.values() 
                               if t['status'] in [TaskStatus.PENDING, TaskStatus.ASSIGNED, TaskStatus.RUNNING]]),
            "stats": self.stats
        }
