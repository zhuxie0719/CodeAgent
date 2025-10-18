#!/usr/bin/env python3
"""
快速安装脚本 - 一键安装所有依赖
"""

import subprocess
import sys

def install_all():
    """一键安装所有依赖"""
    print("🚀 快速安装AI Agent系统依赖...")
    
    # 核心依赖
    core_deps = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0", 
        "python-multipart==0.0.6",
        "pydantic>=2.11.0",
        "pydantic-settings>=2.0.0",
        "httpx==0.25.2",
        "aiohttp==3.9.1",
        "psutil==5.9.6"
    ]
    
    # 静态分析工具
    static_deps = [
        "pylint==3.0.3",
        "flake8==6.1.0",
        "bandit==1.7.5", 
        "mypy==1.7.1",
        "black==23.11.0",
        "isort==5.12.0"
    ]
    
    # AI和测试工具
    other_deps = [
        "openai==1.3.7",
        "anthropic==0.7.8",
        "pytest==7.4.3",
        "pytest-asyncio==0.21.1",
        "requests==2.31.0",
        "click==8.1.7",
        "networkx==3.2.1",
        "asttokens==2.4.1",
        "watchdog==3.0.0",
        "loguru==0.7.2",
        "flask==2.0.3",
        "flask-cors==4.0.0",
        "python-magic-bin==0.4.14"
    ]
    
    all_deps = core_deps + static_deps + other_deps
    
    print(f"📦 准备安装 {len(all_deps)} 个依赖包...")
    
    # 批量安装
    cmd = f"pip install {' '.join(all_deps)}"
    print(f"执行命令: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("✅ 所有依赖安装成功！")
        print("\n🎉 安装完成！现在可以运行:")
        print("   python start_api.py")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ 安装失败，尝试逐个安装...")
        
        # 逐个安装
        success_count = 0
        for dep in all_deps:
            try:
                subprocess.run(f"pip install {dep}", shell=True, check=True)
                print(f"✅ {dep}")
                success_count += 1
            except:
                print(f"❌ {dep}")
        
        print(f"\n📊 安装结果: {success_count}/{len(all_deps)} 成功")
        return success_count > len(all_deps) * 0.8  # 80%成功就算通过

if __name__ == "__main__":
    install_all()



