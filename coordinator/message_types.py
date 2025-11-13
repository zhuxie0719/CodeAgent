"""
Agent间通信的消息类型定义
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import json


class MessageType(Enum):
    """消息类型枚举"""
    TASK = "task"           # 任务消息
    RESULT = "result"       # 结果消息
    EVENT = "event"         # 事件消息
    STATUS = "status"       # 状态消息
    ERROR = "error"         # 错误消息


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"     # 等待中
    ASSIGNED = "assigned"   # 已分配
    RUNNING = "running"     # 运行中
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed" # 已完成
    FAILED = "failed"       # 失败
    CANCELLED = "cancelled" # 已取消


class EventType(Enum):
    """事件类型枚举"""
    AGENT_STARTED = "agent_started"
    AGENT_STOPPED = "agent_stopped"
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    DETECTION_COMPLETED = "detection_completed"
    FIX_COMPLETED = "fix_completed"
    VALIDATION_COMPLETED = "validation_completed"
    SYSTEM_ERROR = "system_error"


@dataclass
class BaseMessage:
    """基础消息类"""
    message_id: str
    source_agent: str
    message_type: MessageType = MessageType.TASK
    target_agent: Optional[str] = None
    timestamp: datetime = None
    priority: int = 1
    timeout: int = 300
    retry_count: int = 0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseMessage':
        """从字典创建消息"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class TaskMessage:
    """任务消息"""
    message_id: str
    source_agent: str
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    message_type: MessageType = MessageType.TASK
    target_agent: Optional[str] = None
    timestamp: datetime = None
    priority: int = 1
    timeout: int = 300
    retry_count: int = 0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            'message_id': self.message_id,
            'source_agent': self.source_agent,
            'task_id': self.task_id,
            'task_type': self.task_type,
            'payload': self.payload,
            'message_type': self.message_type.value,
            'target_agent': self.target_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'priority': self.priority,
            'timeout': self.timeout,
            'retry_count': self.retry_count
        }
        return result


@dataclass
class ResultMessage:
    """结果消息"""
    message_id: str
    source_agent: str
    task_id: str
    result: Dict[str, Any]
    status: TaskStatus
    message_type: MessageType = MessageType.RESULT
    target_agent: Optional[str] = None
    timestamp: datetime = None
    priority: int = 1
    timeout: int = 300
    retry_count: int = 0
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class EventMessage:
    """事件消息"""
    message_id: str
    source_agent: str
    event_type: EventType
    payload: Dict[str, Any]
    message_type: MessageType = MessageType.EVENT
    target_agent: Optional[str] = None
    timestamp: datetime = None
    priority: int = 1
    timeout: int = 300
    retry_count: int = 0
    broadcast: bool = False
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class StatusMessage:
    """状态消息"""
    message_id: str
    source_agent: str
    agent_status: str  # running, idle, error, busy
    metrics: Dict[str, Any]
    message_type: MessageType = MessageType.STATUS
    target_agent: Optional[str] = None
    timestamp: datetime = None
    priority: int = 1
    timeout: int = 300
    retry_count: int = 0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ErrorMessage:
    """错误消息"""
    message_id: str
    source_agent: str
    error_code: str
    error_message: str
    message_type: MessageType = MessageType.ERROR
    target_agent: Optional[str] = None
    timestamp: datetime = None
    priority: int = 1
    timeout: int = 300
    retry_count: int = 0
    details: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class MessageFactory:
    """消息工厂类"""
    
    @staticmethod
    def create_task_message(
        source_agent: str,
        target_agent: str,
        task_id: str,
        task_type: str,
        payload: Dict[str, Any],
        priority: int = 1
    ) -> TaskMessage:
        """创建任务消息"""
        import uuid
        return TaskMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.TASK,
            source_agent=source_agent,
            target_agent=target_agent,
            task_id=task_id,
            task_type=task_type,
            payload=payload,
            priority=priority
        )
    
    @staticmethod
    def create_result_message(
        source_agent: str,
        target_agent: str,
        task_id: str,
        result: Dict[str, Any],
        status: TaskStatus,
        error: Optional[str] = None
    ) -> ResultMessage:
        """创建结果消息"""
        import uuid
        return ResultMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.RESULT,
            source_agent=source_agent,
            target_agent=target_agent,
            task_id=task_id,
            result=result,
            status=status,
            error=error
        )
    
    @staticmethod
    def create_event_message(
        source_agent: str,
        event_type: EventType,
        payload: Dict[str, Any],
        target_agent: Optional[str] = None,
        broadcast: bool = False
    ) -> EventMessage:
        """创建事件消息"""
        import uuid
        return EventMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.EVENT,
            source_agent=source_agent,
            target_agent=target_agent,
            event_type=event_type,
            payload=payload,
            broadcast=broadcast
        )
    
    @staticmethod
    def create_status_message(
        source_agent: str,
        agent_status: str,
        metrics: Dict[str, Any],
        target_agent: Optional[str] = None
    ) -> StatusMessage:
        """创建状态消息"""
        import uuid
        return StatusMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.STATUS,
            source_agent=source_agent,
            target_agent=target_agent,
            agent_status=agent_status,
            metrics=metrics
        )
    
    @staticmethod
    def create_error_message(
        source_agent: str,
        target_agent: str,
        error_code: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> ErrorMessage:
        """创建错误消息"""
        import uuid
        return ErrorMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.ERROR,
            source_agent=source_agent,
            target_agent=target_agent,
            error_code=error_code,
            error_message=error_message,
            details=details
        )


# 预定义的缺陷类型（基于Bug检测Agent的规则）
DEFECT_TYPES = {
    # 简单缺陷 - 可以直接自动修复
    "simple": {
        "unused_imports": "未使用的导入",
        "bad_formatting": "代码格式问题", 
        "unused_variables": "未使用的变量",
        "missing_docstrings": "缺少文档字符串"
    },
    
    # 中等缺陷 - 需要AI辅助修复
    "medium": {
        "magic_numbers": "魔法数字",
        "bad_naming": "命名不规范",
        "long_functions": "过长的函数",
        "deep_nesting": "过深的嵌套",
        "bad_formatting": "代码格式问题"
    },
    
    # 复杂缺陷 - 需要人工审查
    "complex": {
        "hardcoded_secrets": "硬编码秘密信息",
        "unsafe_eval": "不安全的eval使用",
        "memory_leaks": "内存泄漏风险",
        "unsafe_file_operations": "不安全的文件操作",
        "missing_input_validation": "缺少输入验证",
        "insecure_random": "不安全的随机数",
        "duplicate_code": "重复代码",
        "bad_exception_handling": "异常处理不当",
        "global_variables": "全局变量使用",
        "unhandled_exceptions": "未处理的异常"
    }
}

# 修复策略映射
FIX_STRATEGIES = {
    "unused_imports": "auto_remove",
    "bad_formatting": "auto_format",
    "unused_variables": "auto_remove", 
    "missing_docstrings": "auto_generate",
    "magic_numbers": "ai_suggest_constants",
    "bad_naming": "ai_rename_suggestions",
    "long_functions": "ai_refactor",
    "deep_nesting": "ai_refactor",
    "hardcoded_secrets": "manual_review",
    "unsafe_eval": "manual_review",
    "memory_leaks": "ai_analysis_required",
    "unsafe_file_operations": "manual_review",
    "missing_input_validation": "ai_analysis_required",
    "insecure_random": "manual_review",
    "duplicate_code": "ai_analysis_required",
    "bad_exception_handling": "ai_analysis_required",
    "global_variables": "ai_analysis_required",
    "unhandled_exceptions": "ai_analysis_required"
}
