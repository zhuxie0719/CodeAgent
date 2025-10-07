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
    
    # 工具配置
    TOOLS: Dict[str, Dict[str, Any]] = {
        "pylint": {
            "enabled": True,
            "args": ["--disable=C0114,C0116"]
        },
        "flake8": {
            "enabled": True,
            "args": ["--max-line-length=88"]
        },
        "bandit": {
            "enabled": True,
            "args": ["-r", "-f", "json"]
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
