#!/usr/bin/env python3
"""
AI Agent 系统 API 启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        print("✅ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r api/requirements.txt")
        return False

def start_api_server():
    """启动API服务器"""
    print("🚀 启动AI Agent API服务器...")
    print("📍 API文档地址: http://localhost:8001/docs")
    print("📍 前端界面地址: file://" + str(Path("frontend/index.html").absolute()))
    print("📍 健康检查: http://localhost:8001/health")
    print("按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        # 切换到API目录
        api_dir = Path(__file__).parent / "api"
        os.chdir(api_dir)
        print(f"当前工作目录: {os.getcwd()}")
        
        # 检查bug_detection_api.py文件是否存在
        if not Path("bug_detection_api.py").exists():
            print("❌ bug_detection_api.py 文件不存在")
            return
        
        # 启动服务器
        print("正在启动uvicorn服务器...")
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "bug_detection_api:app", 
            "--host", "0.0.0.0", 
            "--port", "8001", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("请检查:")
        print("1. 是否安装了所有依赖: pip install -r api/requirements.txt")
        print("2. 端口8001是否被占用")
        print("3. 防火墙是否阻止了连接")

def main():
    """主函数"""
    print("🤖 AI Agent 代码检测系统")
    print("=" * 50)
    
    if not check_dependencies():
        return
    
    start_api_server()

if __name__ == "__main__":
    main()
