"""
AI AGENT系统配置文件
"""

import os
from typing import Dict, Any, List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """系统设置"""
    
    # 基础配置
    APP_NAME: str = "AI AGENT System"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://user:password@localhost/ai_agent_db"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/ai_agent.log"
    
    # AGENT配置
    AGENTS: Dict[str, Dict[str, Any]] = {
        "code_analysis_agent": {
            "enabled": True,
            "interval": 60,  # 秒
            "max_workers": 2
        },
        "bug_detection_agent": {
            "enabled": True,
            "interval": 300,  # 秒
            "max_workers": 2
        },
        "fix_execution_agent": {
            "enabled": True,
            "interval": 0,  # 按需执行
            "max_workers": 1
        },
        "test_validation_agent": {
            "enabled": True,
            "interval": 0,  # 按需执行
            "max_workers": 2
        },
        "performance_optimization_agent": {
            "enabled": True,
            "interval": 600,  # 秒
            "max_workers": 1
        },
        "code_quality_agent": {
            "enabled": True,
            "interval": 1800,  # 秒
            "max_workers": 1
        }
    }
    
    # 工具配置（方案B标准方案）
    TOOLS: Dict[str, Dict[str, Any]] = {
        "pylint": {
            "enabled": True,
            "pylint_args": ["--disable=C0114,C0116", "--load-plugins=pylint_flask"]
        },
        "bandit": {
            "enabled": True,
            "args": ["-r", "-f", "json"]
        },
        "mypy": {
            "enabled": True,
            "strict_mode": False,  # 关闭严格模式，减少不必要的类型检查问题（Flask框架代码本身类型注解较少）
            "mypy_args": [
                "--ignore-missing-imports",  # 忽略缺失的导入（第三方库）
                "--no-strict-optional",  # 不强制可选类型检查
                "--allow-untyped-calls",  # 允许未注解的函数调用
                "--allow-untyped-defs",  # 允许未注解的函数定义
                "--allow-incomplete-defs",  # 允许不完整的类型定义
            ]  # 减少误报的参数
        },
        "semgrep": {
            "enabled": True,  # 方案B必需
            "rules_configs": [],  # 不使用默认规则集，只使用自定义规则（避免配置错误）
            "semgrep_args": ["--quiet"],
            "custom_rules": [
                "tools/static_analysis/semgrep_rules/flask_2_0_0_issues.yml"  # Flask特定规则
            ]
        },
        "ruff": {
            "enabled": True,  # 方案B推荐，替代flake8（更快且功能更强）
            "ruff_args": ["--output-format=json"],
            "select": ["E", "F", "W", "I"],  # 选择规则组：错误、pyflakes、警告、isort
            "ignore": []  # 忽略特定规则
        },
        "black": {
            "enabled": True,
            "args": ["--line-length=88"]
        },
        "isort": {
            "enabled": True,
            "args": ["--profile", "black"]
        }
    }
    
    # AI模型配置
    AI_MODELS: Dict[str, Dict[str, Any]] = {
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "model": "gpt-4",
            "max_tokens": 4000,
            "temperature": 0.1
        },
        "anthropic": {
            "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 4000,
            "temperature": 0.1
        }
    }
    
    # LLM误报过滤器配置
    LLM_FILTER: Dict[str, Any] = {
        "enabled": True,  # 是否启用智能误报过滤
        "confidence_threshold": 0.7,  # 置信度阈值（0.0-1.0）
        "batch_size": 20,  # 批量处理大小（减少API调用次数）
        "model": "deepseek-chat",  # 使用的模型
        "cache_enabled": True,  # 是否启用缓存（避免重复判断）
        "max_issues_to_filter": 100  # 最多过滤的问题数（控制成本）
    }
    
    # 监控配置
    MONITORING: Dict[str, Any] = {
        "enabled": True,
        "metrics_port": 8000,
        "health_check_interval": 30
    }
    
    # 安全配置
    SECURITY: Dict[str, Any] = {
        "secret_key": os.getenv("SECRET_KEY", "your-secret-key-here"),
        "allowed_hosts": ["localhost", "127.0.0.1"],
        "cors_origins": ["*"]
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局设置实例
settings = Settings()
