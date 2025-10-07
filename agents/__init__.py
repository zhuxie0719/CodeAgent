"""
AI Agent系统包
包含所有Agent的实现和基类定义
"""

# 导入基类（总是可用的）
from .base_agent import BaseAgent, AgentStatus, TaskStatus

# 基础导出
__all__ = [
    'BaseAgent',
    'AgentStatus',
    'TaskStatus',
]

# 针对各Agent进行容错导入，避免某些可选依赖缺失导致包导入失败
try:
    from .bug_detection_agent import BugDetectionAgent  # 需要安装依赖
    __all__.append('BugDetectionAgent')
except Exception:  # noqa: S110 - 兼容启动时的可选模块缺失
    BugDetectionAgent = None  # type: ignore

try:
    from .fix_execution_agent import FixExecutionAgent
    __all__.append('FixExecutionAgent')
except Exception:  # noqa: S110
    FixExecutionAgent = None  # type: ignore

try:
    from .test_validation_agent import TestValidationAgent
    __all__.append('TestValidationAgent')
except Exception:  # noqa: S110
    TestValidationAgent = None  # type: ignore

try:
    from .code_analysis_agent import CodeAnalysisAgent
    __all__.append('CodeAnalysisAgent')
except Exception:  # noqa: S110
    CodeAnalysisAgent = None  # type: ignore

try:
    from .code_quality_agent import CodeQualityAgent
    __all__.append('CodeQualityAgent')
except Exception:  # noqa: S110
    CodeQualityAgent = None  # type: ignore

try:
    from .performance_optimization_agent import PerformanceOptimizationAgent
    __all__.append('PerformanceOptimizationAgent')
except Exception:  # noqa: S110
    PerformanceOptimizationAgent = None  # type: ignore

# 包信息
__version__ = "1.0.0"
__author__ = "AI Agent Team"
__description__ = "AI Agent系统 - 智能代码缺陷检测和修复"
