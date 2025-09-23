"""
DeepSeek API 配置
用于生成AI自然语言报告
"""

import os
from typing import Optional

class DeepSeekConfig:
    """DeepSeek API 配置类"""
    
    def __init__(self):
        # 优先使用环境变量，如果没有则使用默认密钥
        self.api_key: Optional[str] = os.getenv("DEEPSEEK_API_KEY") or "sk-75db9bf464d44ee78b5d45a655431710"
        self.base_url: str = "https://api.deepseek.com/v1"
        self.model: str = "deepseek-chat"
        self.max_tokens: int = 2000
        self.temperature: float = 0.7
    
    def is_configured(self) -> bool:
        """检查是否已配置API密钥"""
        return self.api_key is not None
    
    def get_headers(self) -> dict:
        """获取API请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

# 全局配置实例
deepseek_config = DeepSeekConfig()
