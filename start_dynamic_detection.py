#!/usr/bin/env python3
"""
启动动态检测服务
简化版启动脚本，确保3周内能完成
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
        import psutil
        print("✅ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install fastapi uvicorn psutil")
        return False

def start_dynamic_detection_api():
    """启动动态检测API服务"""
    print("🚀 启动动态检测API服务器...")
    print("📍 API文档地址: http://localhost:8003/docs")
    print("📍 前端界面地址: file://" + str(Path("frontend/dynamic_detection.html").absolute()))
    print("📍 健康检查: http://localhost:8003/health")
    print("按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        # 检查API文件是否存在
        api_file = Path("api/simple_dynamic_api.py")
        if not api_file.exists():
            print("❌ simple_dynamic_api.py 文件不存在")
            return
        
        # 启动服务器
        print("正在启动uvicorn服务器...")
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api.simple_dynamic_api:app", 
            "--host", "0.0.0.0", 
            "--port", "8003", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("请检查:")
        print("1. 是否安装了所有依赖: pip install fastapi uvicorn psutil")
        print("2. 端口8003是否被占用")
        print("3. 防火墙是否阻止了连接")

def test_components():
    """测试各个组件"""
    print("🧪 测试组件...")
    
    try:
        # 测试监控Agent
        from agents.simple_monitor_agent import SimpleMonitorAgent
        monitor = SimpleMonitorAgent()
        print("✅ 监控Agent导入成功")
        
        # 测试项目运行器
        from utils.project_runner import ProjectRunner
        runner = ProjectRunner()
        print("✅ 项目运行器导入成功")
        
        # 测试集成检测器
        from agents.integrated_detector import IntegratedDetector
        detector = IntegratedDetector()
        print("✅ 集成检测器导入成功")
        
        print("✅ 所有组件测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 组件测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🔍 动态缺陷检测系统")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 测试组件
    if not test_components():
        return
    
    # 启动API服务
    start_dynamic_detection_api()

if __name__ == "__main__":
    main()
