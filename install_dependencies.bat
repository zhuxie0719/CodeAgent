@echo off
chcp 65001 >nul
echo 🚀 AI Agent 代码检测系统 - 依赖安装脚本
echo ================================================

echo.
echo 🔧 升级pip...
python -m pip install --upgrade pip

echo.
echo 📦 安装核心依赖...
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install python-multipart==0.0.6
pip install "pydantic>=2.11.0"
pip install "pydantic-settings>=2.0.0"
pip install httpx==0.25.2
pip install aiohttp==3.9.1
pip install psutil==5.9.6

echo.
echo 🔍 安装静态分析工具...
pip install pylint==3.0.3
pip install flake8==6.1.0
pip install bandit==1.7.5
pip install mypy==1.7.1
pip install black==23.11.0
pip install isort==5.12.0

echo.
echo 🤖 安装AI相关依赖...
pip install openai==1.3.7
pip install anthropic==0.7.8
pip install "numpy>=1.24.0"
pip install "scikit-learn>=1.3.0"

echo.
echo 🧪 安装测试工具...
pip install pytest==7.4.3
pip install pytest-cov==4.1.0
pip install pytest-asyncio==0.21.1
pip install pytest-json-report==1.5.0
pip install coverage==7.3.2

echo.
echo 🛠️ 安装实用工具...
pip install requests==2.31.0
pip install click==8.1.7
pip install networkx==3.2.1
pip install asttokens==2.4.1
pip install watchdog==3.0.0
pip install loguru==0.7.2
pip install python-magic-bin==0.4.14

echo.
echo 🌐 安装Flask相关依赖...
pip install flask==2.0.3
pip install flask-cors==4.0.0
pip install werkzeug==2.0.3
pip install jinja2==3.1.2
pip install markupsafe==2.1.3

echo.
echo ✅ 安装完成！
echo.
echo 🎉 现在可以运行以下命令启动系统:
echo    python start_api.py
echo.
pause



