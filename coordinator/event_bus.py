"""
事件总线实现
负责Agent间的异步通信和事件分发
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime
from collections import defaultdict
import json

from .message_types import (
    BaseMessage, EventMessage, EventType, MessageType,
    MessageFactory, TaskMessage, ResultMessage, StatusMessage, ErrorMessage
)


class EventBus:
    """事件总线 - Agent间通信的核心组件"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.subscribers: Dict[str, Set[str]] = defaultdict(set)  # event_type -> agent_ids
        self.message_queue = asyncio.Queue(maxsize=config.get("max_queue_size", 10000))
        self.agent_handlers: Dict[str, Callable] = {}  # agent_id -> handler_function
        self.is_running = False
        self.logger = logging.getLogger(__name__)
        
        # 重试配置
        self.retry_policy = config.get("retry_policy", {
            "max_retries": 3,
            "base_delay": 1.0,
            "max_delay": 60.0
        })
        
        # 消息超时配置
        self.message_timeout = config.get("message_timeout", 300)
        
        # 统计信息
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_failed": 0,
            "events_published": 0
        }
    
    async def start(self):
        """启动事件总线"""
        self.is_running = True
        self.logger.info("事件总线启动中...")
        
        # 启动消息处理循环
        asyncio.create_task(self._message_processing_loop())
        
        self.logger.info("事件总线已启动")
    
    async def stop(self):
        """停止事件总线"""
        self.is_running = False
        self.logger.info("事件总线已停止")
    
    async def subscribe(self, event_type: str, agent_id: str, handler: Callable):
        """订阅事件"""
        self.subscribers[event_type].add(agent_id)
        self.agent_handlers[agent_id] = handler
        self.logger.info(f"Agent {agent_id} 已订阅事件类型: {event_type}")
    
    async def unsubscribe(self, event_type: str, agent_id: str):
        """取消订阅事件"""
        if event_type in self.subscribers:
            self.subscribers[event_type].discard(agent_id)
        self.logger.info(f"Agent {agent_id} 已取消订阅事件类型: {event_type}")
    
    async def publish(self, event_type: str, data: Dict[str, Any], source_agent: str, 
                     target_agent: Optional[str] = None, broadcast: bool = False):
        """发布事件"""
        try:
            event_message = MessageFactory.create_event_message(
                source_agent=source_agent,
                event_type=EventType(event_type),
                payload=data,
                target_agent=target_agent,
                broadcast=broadcast
            )
            
            await self.message_queue.put(event_message)
            self.stats["events_published"] += 1
            
            self.logger.debug(f"事件已发布: {event_type} from {source_agent}")
            
        except Exception as e:
            self.logger.error(f"发布事件失败: {e}")
            self.stats["messages_failed"] += 1
    
    async def send_message(self, message: BaseMessage):
        """发送消息"""
        try:
            await self.message_queue.put(message)
            self.stats["messages_sent"] += 1
            
            self.logger.debug(f"消息已发送: {message.message_type.value} from {message.source_agent}")
            
        except Exception as e:
            self.logger.error(f"发送消息失败: {e}")
            self.stats["messages_failed"] += 1
    
    async def send_task_message(self, source_agent: str, target_agent: str, 
                              task_id: str, task_type: str, payload: Dict[str, Any]):
        """发送任务消息"""
        task_message = MessageFactory.create_task_message(
            source_agent=source_agent,
            target_agent=target_agent,
            task_id=task_id,
            task_type=task_type,
            payload=payload
        )
        await self.send_message(task_message)
    
    async def send_result_message(self, source_agent: str, target_agent: str,
                                task_id: str, result: Dict[str, Any], 
                                success: bool, error: Optional[str] = None):
        """发送结果消息"""
        from .message_types import TaskStatus
        
        status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        result_message = MessageFactory.create_result_message(
            source_agent=source_agent,
            target_agent=target_agent,
            task_id=task_id,
            result=result,
            status=status,
            error=error
        )
        await self.send_message(result_message)
    
    async def _message_processing_loop(self):
        """消息处理循环"""
        self.logger.info("消息处理循环已启动")
        
        while self.is_running:
            try:
                # 等待消息，超时1秒
                message = await asyncio.wait_for(
                    self.message_queue.get(), 
                    timeout=1.0
                )
                
                await self._process_message(message)
                self.stats["messages_received"] += 1
                
            except asyncio.TimeoutError:
                # 超时是正常的，继续循环
                continue
            except Exception as e:
                self.logger.error(f"消息处理错误: {e}")
                self.stats["messages_failed"] += 1
    
    async def _process_message(self, message: BaseMessage):
        """处理单个消息"""
        try:
            if isinstance(message, EventMessage):
                await self._handle_event_message(message)
            elif isinstance(message, TaskMessage):
                await self._handle_task_message(message)
            elif isinstance(message, ResultMessage):
                await self._handle_result_message(message)
            elif isinstance(message, StatusMessage):
                await self._handle_status_message(message)
            elif isinstance(message, ErrorMessage):
                await self._handle_error_message(message)
            else:
                self.logger.warning(f"未知消息类型: {type(message)}")
                
        except Exception as e:
            self.logger.error(f"处理消息失败: {e}")
            # 发送错误消息
            error_message = MessageFactory.create_error_message(
                source_agent="event_bus",
                target_agent=message.source_agent,
                error_code="MESSAGE_PROCESSING_ERROR",
                error_message=str(e)
            )
            await self.send_message(error_message)
    
    async def _handle_event_message(self, message: EventMessage):
        """处理事件消息"""
        event_type = message.event_type.value
        
        # 如果是广播消息，发送给所有订阅者
        if message.broadcast:
            for agent_id in self.subscribers.get(event_type, set()):
                if agent_id in self.agent_handlers:
                    await self._deliver_message_to_agent(agent_id, message)
        else:
            # 发送给特定目标Agent
            if message.target_agent and message.target_agent in self.agent_handlers:
                await self._deliver_message_to_agent(message.target_agent, message)
            else:
                # 发送给所有订阅者
                for agent_id in self.subscribers.get(event_type, set()):
                    if agent_id in self.agent_handlers:
                        await self._deliver_message_to_agent(agent_id, message)
    
    async def _handle_task_message(self, message: TaskMessage):
        """处理任务消息"""
        if message.target_agent and message.target_agent in self.agent_handlers:
            await self._deliver_message_to_agent(message.target_agent, message)
        else:
            self.logger.warning(f"目标Agent不存在: {message.target_agent}")
    
    async def _handle_result_message(self, message: ResultMessage):
        """处理结果消息"""
        if message.target_agent and message.target_agent in self.agent_handlers:
            await self._deliver_message_to_agent(message.target_agent, message)
    
    async def _handle_status_message(self, message: StatusMessage):
        """处理状态消息"""
        # 状态消息通常广播给所有相关Agent
        for agent_id in self.agent_handlers.keys():
            if agent_id != message.source_agent:  # 不发送给自己
                await self._deliver_message_to_agent(agent_id, message)
    
    async def _handle_error_message(self, message: ErrorMessage):
        """处理错误消息"""
        if message.target_agent and message.target_agent in self.agent_handlers:
            await self._deliver_message_to_agent(message.target_agent, message)
    
    async def _deliver_message_to_agent(self, agent_id: str, message: BaseMessage):
        """将消息传递给Agent"""
        try:
            handler = self.agent_handlers.get(agent_id)
            if handler:
                # 异步调用Agent的处理函数
                await handler(message)
            else:
                self.logger.warning(f"Agent {agent_id} 没有注册处理函数")
                
        except Exception as e:
            self.logger.error(f"向Agent {agent_id} 传递消息失败: {e}")
            
            # 重试机制
            await self._retry_message_delivery(agent_id, message)
    
    async def _retry_message_delivery(self, agent_id: str, message: BaseMessage):
        """重试消息传递"""
        max_retries = self.retry_policy["max_retries"]
        base_delay = self.retry_policy["base_delay"]
        max_delay = self.retry_policy["max_delay"]
        
        for attempt in range(max_retries):
            try:
                # 指数退避延迟
                delay = min(base_delay * (2 ** attempt), max_delay)
                await asyncio.sleep(delay)
                
                handler = self.agent_handlers.get(agent_id)
                if handler:
                    await handler(message)
                    self.logger.info(f"消息重试成功: Agent {agent_id}")
                    return
                    
            except Exception as e:
                self.logger.warning(f"消息重试失败 (尝试 {attempt + 1}/{max_retries}): {e}")
        
        # 所有重试都失败
        self.logger.error(f"消息传递最终失败: Agent {agent_id}")
        self.stats["messages_failed"] += 1
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            "subscribers_count": sum(len(agents) for agents in self.subscribers.values()),
            "queue_size": self.message_queue.qsize(),
            "registered_agents": list(self.agent_handlers.keys())
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "is_running": self.is_running,
            "queue_size": self.message_queue.qsize(),
            "subscribers": dict(self.subscribers),
            "registered_agents": len(self.agent_handlers),
            "stats": self.stats
        }
