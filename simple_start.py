#!/usr/bin/env python3
"""
简化的API启动脚本
"""

import uvicorn
import sys
import os
from pathlib import Path

# 切换到API目录
api_dir = Path(__file__).parent / "api"
os.chdir(api_dir)
print(f"当前工作目录: {os.getcwd()}")

# 启动服务器
print("🚀 启动API服务器...")
print("📍 API文档地址: http://localhost:8001/docs")
print("📍 健康检查: http://localhost:8001/health")
print("按 Ctrl+C 停止服务器")

try:
    uvicorn.run(
        "agent_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
except KeyboardInterrupt:
    print("\n👋 服务器已停止")
except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback
    traceback.print_exc()

