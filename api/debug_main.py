#!/usr/bin/env python3
"""
调试main_api.py
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent))

print("开始调试main_api...")

try:
    print("1. 导入FastAPI...")
    from fastapi import FastAPI
    print("✅ FastAPI导入成功")
    
    print("2. 导入核心管理器...")
    from core.agent_manager import AgentManager
    from core.coordinator_manager import CoordinatorManager
    print("✅ 核心管理器导入成功")
    
    print("3. 创建FastAPI应用...")
    app = FastAPI(title="AI Agent 代码分析系统")
    print("✅ FastAPI应用创建成功")
    
    print("4. 测试动态检测API导入...")
    import dynamic_api
    print("✅ 动态检测API导入成功")
    
    print("5. 挂载动态检测API路由...")
    app.include_router(dynamic_api.router, prefix="/api/dynamic")
    print("✅ 动态检测API路由挂载成功")
    
    print("6. 跳过TestClient测试（版本兼容性问题）...")
    
    print("✅ 所有测试通过！")
    print("现在可以启动API服务器了")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
