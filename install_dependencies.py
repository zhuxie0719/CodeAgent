#!/usr/bin/env python3
"""
AI Agent 代码检测系统 - 依赖安装脚本
自动安装所有必需的Python库和工具
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(cmd, description=""):
    """执行命令并处理错误"""
    print(f"🔧 {description}")
    print(f"执行命令: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - 成功")
        if result.stdout:
            print(f"输出: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - 失败")
        print(f"错误: {e.stderr}")
        return False

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"🐍 Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    print("✅ Python版本符合要求")
    return True

def install_core_dependencies():
    """安装核心依赖"""
    print("\n" + "="*60)
    print("📦 安装核心依赖")
    print("="*60)
    
    core_packages = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "python-multipart==0.0.6",
        "pydantic>=2.11.0",
        "pydantic-settings>=2.0.0",
        "httpx==0.25.2",
        "aiohttp==3.9.1",
        "psutil==5.9.6"
    ]
    
    for package in core_packages:
        success = run_command(f"pip install {package}", f"安装 {package}")
        if not success:
            print(f"⚠️  {package} 安装失败，尝试继续...")

def install_static_analysis_tools():
    """安装静态分析工具"""
    print("\n" + "="*60)
    print("🔍 安装静态分析工具")
    print("="*60)
    
    static_tools = [
        "pylint==3.0.3",
        "flake8==6.1.0", 
        "bandit==1.7.5",
        "mypy==1.7.1",
        "black==23.11.0",
        "isort==5.12.0"
    ]
    
    for tool in static_tools:
        success = run_command(f"pip install {tool}", f"安装 {tool}")
        if not success:
            print(f"⚠️  {tool} 安装失败，尝试继续...")

def install_ai_dependencies():
    """安装AI相关依赖"""
    print("\n" + "="*60)
    print("🤖 安装AI相关依赖")
    print("="*60)
    
    ai_packages = [
        "openai==1.3.7",
        "anthropic==0.7.8",
        "transformers==4.36.0",
        "torch==2.2.0",
        "numpy>=1.24.0",
        "scikit-learn>=1.3.0"
    ]
    
    for package in ai_packages:
        success = run_command(f"pip install {package}", f"安装 {package}")
        if not success:
            print(f"⚠️  {package} 安装失败，尝试继续...")

def install_testing_tools():
    """安装测试工具"""
    print("\n" + "="*60)
    print("🧪 安装测试工具")
    print("="*60)
    
    test_packages = [
        "pytest==7.4.3",
        "pytest-cov==4.1.0",
        "pytest-asyncio==0.21.1",
        "pytest-json-report==1.5.0",
        "coverage==7.3.2"
    ]
    
    for package in test_packages:
        success = run_command(f"pip install {package}", f"安装 {package}")
        if not success:
            print(f"⚠️  {package} 安装失败，尝试继续...")

def install_utility_tools():
    """安装实用工具"""
    print("\n" + "="*60)
    print("🛠️ 安装实用工具")
    print("="*60)
    
    utility_packages = [
        "requests==2.31.0",
        "click==8.1.7",
        "networkx==3.2.1",
        "asttokens==2.4.1",
        "watchdog==3.0.0",
        "loguru==0.7.2",
        "python-magic-bin==0.4.14" if platform.system() == "Windows" else "python-magic==0.4.27"
    ]
    
    for package in utility_packages:
        success = run_command(f"pip install {package}", f"安装 {package}")
        if not success:
            print(f"⚠️  {package} 安装失败，尝试继续...")

def install_flask_dependencies():
    """安装Flask相关依赖"""
    print("\n" + "="*60)
    print("🌐 安装Flask相关依赖")
    print("="*60)
    
    flask_packages = [
        "flask==2.0.3",
        "flask-cors==4.0.0",
        "werkzeug==2.0.3",
        "jinja2==3.1.2",
        "markupsafe==2.1.3"
    ]
    
    for package in flask_packages:
        success = run_command(f"pip install {package}", f"安装 {package}")
        if not success:
            print(f"⚠️  {package} 安装失败，尝试继续...")

def verify_installation():
    """验证安装"""
    print("\n" + "="*60)
    print("✅ 验证安装")
    print("="*60)
    
    test_imports = [
        ("fastapi", "FastAPI框架"),
        ("uvicorn", "ASGI服务器"),
        ("pylint", "Pylint静态分析"),
        ("flake8", "Flake8代码检查"),
        ("bandit", "Bandit安全扫描"),
        ("mypy", "MyPy类型检查"),
        ("flask", "Flask Web框架"),
        ("httpx", "HTTP客户端"),
        ("psutil", "系统监控")
    ]
    
    success_count = 0
    for module, description in test_imports:
        try:
            __import__(module)
            print(f"✅ {description} ({module}) - 可用")
            success_count += 1
        except ImportError as e:
            print(f"❌ {description} ({module}) - 不可用: {e}")
    
    print(f"\n📊 安装验证结果: {success_count}/{len(test_imports)} 个模块可用")
    return success_count == len(test_imports)

def create_requirements_file():
    """创建requirements.txt文件"""
    print("\n" + "="*60)
    print("📝 创建requirements.txt文件")
    print("="*60)
    
    requirements_content = """# AI Agent 代码检测系统依赖包

# 核心框架
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic>=2.11.0
pydantic-settings>=2.0.0
httpx==0.25.2

# 静态分析工具
pylint==3.0.3
flake8==6.1.0
bandit==1.7.5
mypy==1.7.1
black==23.11.0
isort==5.12.0

# AI相关
openai==1.3.7
anthropic==0.7.8
transformers==4.36.0
torch==2.2.0
numpy>=1.24.0
scikit-learn>=1.3.0

# 测试工具
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
pytest-json-report==1.5.0
coverage==7.3.2

# 实用工具
requests==2.31.0
aiohttp==3.9.1
click==8.1.7
networkx==3.2.1
asttokens==2.4.1
watchdog==3.0.0
loguru==0.7.2
psutil==5.9.6

# Flask相关
flask==2.0.3
flask-cors==4.0.0
werkzeug==2.0.3
jinja2==3.1.2
markupsafe==2.1.3

# 文件类型检测（Windows）
python-magic-bin==0.4.14

# 开发工具
pre-commit==3.6.0
"""
    
    try:
        with open("requirements.txt", "w", encoding="utf-8") as f:
            f.write(requirements_content)
        print("✅ requirements.txt 文件创建成功")
        return True
    except Exception as e:
        print(f"❌ 创建requirements.txt失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 AI Agent 代码检测系统 - 依赖安装脚本")
    print("="*60)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 升级pip
    print("\n🔧 升级pip...")
    run_command("python -m pip install --upgrade pip", "升级pip")
    
    # 安装各个模块
    install_core_dependencies()
    install_static_analysis_tools()
    install_ai_dependencies()
    install_testing_tools()
    install_utility_tools()
    install_flask_dependencies()
    
    # 创建requirements.txt
    create_requirements_file()
    
    # 验证安装
    if verify_installation():
        print("\n🎉 所有依赖安装完成！")
        print("📋 可以运行以下命令启动系统:")
        print("   python start_api.py")
    else:
        print("\n⚠️  部分依赖安装失败，请检查错误信息")
        print("💡 可以尝试手动安装失败的包:")
        print("   pip install <package_name>")

if __name__ == "__main__":
    main()



