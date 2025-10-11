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
    print("📍 动态检测界面: file://" + str(Path("frontend/dynamic_detection.html").absolute()))
    print("📍 健康检查: http://localhost:8001/health")
    print("按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        # 切换到API目录
        api_dir = Path(__file__).parent / "api"
        os.chdir(api_dir)
        print(f"当前工作目录: {os.getcwd()}")
        
        # 检查main_api.py文件是否存在
        if not Path("main_api.py").exists():
            print("❌ main_api.py 文件不存在")
            print("提示: 确保 main_api.py 在 api/ 目录下")
            return
        
        # 启动服务器 - 使用新的模块化架构
        print("正在启动uvicorn服务器...")
        print("注意: 使用新的模块化 API 架构（main_api）")
        print("架构: Coordinator + Agent Manager + 模块化路由")
        print("包含功能: 真实静态分析 + Pylint/Flake8/Bandit + AI分析 + Coordinator协调 + 动态检测")
        print("支持: 单文件检测 + 项目压缩包检测 + 代码质量分析 + 深度代码分析 + 动态缺陷检测")
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main_api:app", 
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
