"""
基础Agent抽象类
定义所有Agent的标准接口和行为
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import logging
from enum import Enum


class AgentStatus(Enum):
    """Agent状态枚举"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BaseAgent(ABC):
    """基础Agent抽象类"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.status = AgentStatus.STOPPED
        self.logger = logging.getLogger(f"agent.{agent_id}")
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_processing_time": 0.0,
            "last_activity": None
        }
        self._running = False
        self._task_queue = asyncio.Queue()
        self._worker_tasks: List[asyncio.Task] = []
    
    @abstractmethod
    async def initialize(self) -> bool:
        """初始化Agent"""
        pass
    
    @abstractmethod
    async def process_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理任务"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """获取Agent能力列表"""
        pass
    
    async def start(self) -> bool:
        """启动Agent"""
        try:
            self.status = AgentStatus.STARTING
            self.logger.info(f"启动Agent: {self.agent_id}")
            
            # 初始化Agent
            if not await self.initialize():
                self.status = AgentStatus.ERROR
                return False
            
            # 启动工作线程
            self._running = True
            worker_count = self.config.get("max_workers", 1)
            
            for i in range(worker_count):
                worker_task = asyncio.create_task(self._worker(f"worker-{i}"))
                self._worker_tasks.append(worker_task)
            
            self.status = AgentStatus.RUNNING
            self.logger.info(f"Agent {self.agent_id} 启动成功")
            return True
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error(f"启动Agent失败: {e}")
            return False
    
    async def stop(self) -> bool:
        """停止Agent"""
        try:
            self.status = AgentStatus.STOPPING
            self.logger.info(f"停止Agent: {self.agent_id}")
            
            # 停止接收新任务
            self._running = False
            
            # 等待所有工作线程完成（添加超时保护）
            if self._worker_tasks:
                try:
                    # 取消所有未完成的任务
                    for task in self._worker_tasks:
                        if not task.done():
                            task.cancel()
                    
                    # 等待任务完成或取消（最多等待3秒）
                    await asyncio.wait_for(
                        asyncio.gather(*self._worker_tasks, return_exceptions=True),
                        timeout=3.0
                    )
                except asyncio.TimeoutError:
                    self.logger.warning(f"Agent {self.agent_id} 工作线程停止超时，强制取消")
                except Exception as e:
                    self.logger.warning(f"Agent {self.agent_id} 停止工作线程时异常: {e}")
                finally:
                    self._worker_tasks.clear()
            
            self.status = AgentStatus.STOPPED
            self.logger.info(f"Agent {self.agent_id} 已停止")
            return True
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error(f"停止Agent失败: {e}")
            return False
    
    async def submit_task(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """提交任务"""
        try:
            task_info = {
                "task_id": task_id,
                "data": task_data,
                "status": TaskStatus.PENDING,
                "created_at": datetime.now(),
                "started_at": None,
                "completed_at": None,
                "result": None,
                "error": None
            }
            
            self.tasks[task_id] = task_info
            await self._task_queue.put(task_id)
            
            self.logger.info(f"任务已提交: {task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"提交任务失败: {e}")
            return False
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        return {
            "task_id": task_id,
            "status": task["status"].value,
            "created_at": task["created_at"].isoformat(),
            "started_at": task["started_at"].isoformat() if task["started_at"] else None,
            "completed_at": task["completed_at"].isoformat() if task["completed_at"] else None,
            "result": task["result"],
            "error": task["error"]
        }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """获取Agent指标"""
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "tasks_completed": self.metrics["tasks_completed"],
            "tasks_failed": self.metrics["tasks_failed"],
            "total_processing_time": self.metrics["total_processing_time"],
            "average_processing_time": (
                self.metrics["total_processing_time"] / max(1, self.metrics["tasks_completed"])
            ),
            "last_activity": self.metrics["last_activity"].isoformat() if self.metrics["last_activity"] else None,
            "active_tasks": len([t for t in self.tasks.values() if t["status"] == TaskStatus.PROCESSING]),
            "pending_tasks": len([t for t in self.tasks.values() if t["status"] == TaskStatus.PENDING])
        }
    
    async def _worker(self, worker_name: str):
        """工作线程"""
        self.logger.info(f"工作线程启动: {worker_name}")
        
        while self._running:
            try:
                # 获取任务
                task_id = await asyncio.wait_for(self._task_queue.get(), timeout=1.0)
                
                # 处理任务
                await self._process_task_internal(task_id)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"工作线程错误: {e}")
        
        self.logger.info(f"工作线程停止: {worker_name}")
    
    async def _process_task_internal(self, task_id: str):
        """内部任务处理"""
        task = self.tasks.get(task_id)
        if not task:
            return
        
        try:
            # 更新任务状态
            task["status"] = TaskStatus.PROCESSING
            task["started_at"] = datetime.now()
            
            # 处理任务
            start_time = datetime.now()
            result = await self.process_task(task_id, task["data"])
            end_time = datetime.now()
            
            # 更新任务结果
            task["status"] = TaskStatus.COMPLETED
            task["completed_at"] = end_time
            task["result"] = result
            
            # 更新指标
            processing_time = (end_time - start_time).total_seconds()
            self.metrics["tasks_completed"] += 1
            self.metrics["total_processing_time"] += processing_time
            self.metrics["last_activity"] = end_time
            
            self.logger.info(f"任务完成: {task_id}, 耗时: {processing_time:.2f}秒")
            
        except Exception as e:
            # 更新任务错误状态
            task["status"] = TaskStatus.FAILED
            task["completed_at"] = datetime.now()
            task["error"] = str(e)
            
            # 更新指标
            self.metrics["tasks_failed"] += 1
            self.metrics["last_activity"] = datetime.now()
            
            self.logger.error(f"任务失败: {task_id}, 错误: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取Agent状态"""
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "capabilities": self.get_capabilities(),
            "config": self.config,
            "metrics": self.metrics
        }
