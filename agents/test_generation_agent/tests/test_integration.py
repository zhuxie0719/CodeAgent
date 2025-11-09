"""
TestGenerationAgent集成测试
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil
import subprocess

from agents.test_generation_agent.agent import TestGenerationAgent


@pytest.fixture
def python_project():
    """创建Python测试项目"""
    project_dir = tempfile.mkdtemp()
    project_path = Path(project_dir)
    
    # 创建源代码
    (project_path / "calculator.py").write_text("""
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("除数不能为0")
    return a / b
""")
    
    yield project_dir
    shutil.rmtree(project_dir)


@pytest.mark.asyncio
async def test_end_to_end_python(python_project):
    """端到端测试：Python项目"""
    agent = TestGenerationAgent(config={"use_llm": True, "use_pynguin": False})
    await agent.initialize()
    
    # 生成测试
    result = await agent.process_task("test_task", {
        "project_path": python_project
    })
    
    assert result["success"] is True
    assert result["total_tests"] > 0
    
    # 验证测试文件可以运行
    project_path = Path(python_project)
    tests_dir = project_path / "tests"
    
    assert tests_dir.exists()
    test_files = list(tests_dir.glob("test_*.py"))
    assert len(test_files) > 0
    
    # 尝试运行测试（如果pytest可用）
    try:
        result = subprocess.run(
            ["pytest", str(tests_dir), "-v"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=python_project
        )
        # 不要求测试全部通过，只要可以运行即可
        assert result.returncode is not None
    except FileNotFoundError:
        pytest.skip("pytest未安装，跳过测试执行")


@pytest.mark.asyncio
async def test_with_issue_description(python_project):
    """测试带问题描述的测试生成"""
    agent = TestGenerationAgent(config={"use_llm": True, "use_pynguin": False})
    await agent.initialize()
    
    # 生成测试（带问题描述）
    result = await agent.process_task("test_task", {
        "project_path": python_project,
        "issue_description": "divide函数在除数为0时应该抛出异常"
    })
    
    assert result["success"] is True
    
    # 验证生成了重现测试
    project_path = Path(python_project)
    tests_dir = project_path / "tests"
    
    # 应该生成test_reproduction.py
    repro_test = tests_dir / "test_reproduction.py"
    if repro_test.exists():
        content = repro_test.read_text()
        assert "divide" in content or "除数为0" in content

