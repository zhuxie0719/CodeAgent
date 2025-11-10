"""
TestGenerationAgent主类测试
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil

from agents.test_generation_agent.agent import TestGenerationAgent


@pytest.fixture
def test_agent():
    """创建测试Agent实例"""
    return TestGenerationAgent(config={"use_llm": True, "use_pynguin": False})


@pytest.fixture
def temp_project():
    """创建临时项目目录"""
    project_dir = tempfile.mkdtemp()
    yield project_dir
    shutil.rmtree(project_dir)


@pytest.mark.asyncio
async def test_agent_initialization(test_agent):
    """测试Agent初始化"""
    result = await test_agent.initialize()
    assert result is True
    assert test_agent.agent_id == "test_generation_agent"


@pytest.mark.asyncio
async def test_generate_tests_python(temp_project, test_agent):
    """测试Python项目测试生成"""
    # 创建Python项目
    project_path = Path(temp_project)
    (project_path / "calculator.py").write_text("""
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
""")
    
    # 生成测试
    result = await test_agent.process_task("test_task", {
        "project_path": str(project_path)
    })
    
    assert result["success"] is True
    assert "python" in result["languages"]
    assert result["total_tests"] > 0
    
    # 验证测试文件已生成
    tests_dir = project_path / "tests"
    assert tests_dir.exists()
    assert any(tests_dir.glob("test_*.py"))


@pytest.mark.asyncio
async def test_skip_if_tests_exist(temp_project, test_agent):
    """测试如果已有tests文件夹则跳过"""
    project_path = Path(temp_project)
    
    # 创建已有tests文件夹
    tests_dir = project_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_existing.py").write_text("import pytest")
    
    # 生成测试
    result = await test_agent.process_task("test_task", {
        "project_path": str(project_path)
    })
    
    assert result["success"] is True
    assert result.get("skipped") is True
    assert "tests文件夹已存在" in result["message"]


@pytest.mark.asyncio
async def test_missing_project_path(test_agent):
    """测试缺少project_path参数"""
    result = await test_agent.process_task("test_task", {})
    
    assert result["success"] is False
    assert "缺少project_path参数" in result["error"]


@pytest.mark.asyncio
async def test_invalid_project_path(test_agent):
    """测试无效的项目路径"""
    result = await test_agent.process_task("test_task", {
        "project_path": "/nonexistent/path"
    })
    
    assert result["success"] is False
    assert "项目路径不存在" in result["error"]

