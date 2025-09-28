"""
AI Agent系统包
包含所有Agent的实现和基类定义
"""

# 导入基类（总是可用的）
from .base_agent import BaseAgent, AgentStatus, TaskStatus

# 导入所有Agent类（它们都存在，但需要继承BaseAgent才能与协调中心通信）
from .bug_detection_agent import BugDetectionAgent  # 需要安装依赖
from .fix_execution_agent import FixExecutionAgent
from .test_validation_agent import TestValidationAgent
from .code_analysis_agent import CodeAnalysisAgent
from .code_quality_agent import CodeQualityAgent
from .performance_optimization_agent import PerformanceOptimizationAgent

# 定义包级别的导出
__all__ = [
    # 基类（总是可用）
    'BaseAgent',
    'AgentStatus', 
    'TaskStatus',
    
    # 所有Agent（都存在，但需要继承BaseAgent才能与协调中心通信）
    'BugDetectionAgent',  # 需要安装依赖
    'FixExecutionAgent',
    'TestValidationAgent',
    'CodeAnalysisAgent',
    'CodeQualityAgent',
    'PerformanceOptimizationAgent'
]

# 包信息
__version__ = "1.0.0"
__author__ = "AI Agent Team"
__description__ = "AI Agent系统 - 智能代码缺陷检测和修复"
