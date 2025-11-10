"""
语言检测器测试
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from agents.test_generation_agent.language_detector import LanguageDetector, Language


@pytest.fixture
def detector():
    return LanguageDetector()


@pytest.fixture
def temp_project():
    project_dir = tempfile.mkdtemp()
    yield project_dir
    shutil.rmtree(project_dir)


def test_detect_python_project(temp_project, detector):
    """测试检测Python项目"""
    project_path = Path(temp_project)
    (project_path / "main.py").write_text("print('hello')")
    (project_path / "requirements.txt").write_text("flask==2.0.0")
    
    languages = detector.detect_languages(temp_project)
    
    assert Language.PYTHON in languages


def test_detect_java_project(temp_project, detector):
    """测试检测Java项目"""
    project_path = Path(temp_project)
    (project_path / "pom.xml").write_text("""<?xml version="1.0"?>
<project>
    <groupId>com.example</groupId>
    <artifactId>test</artifactId>
</project>""")
    
    languages = detector.detect_languages(temp_project)
    
    assert Language.JAVA in languages


def test_detect_cpp_project(temp_project, detector):
    """测试检测C++项目"""
    project_path = Path(temp_project)
    (project_path / "CMakeLists.txt").write_text("cmake_minimum_required(VERSION 3.14)")
    (project_path / "main.cpp").write_text("#include <iostream>")
    
    languages = detector.detect_languages(temp_project)
    
    assert Language.CPP in languages


def test_detect_unknown_project(temp_project, detector):
    """测试检测未知项目"""
    project_path = Path(temp_project)
    (project_path / "unknown.txt").write_text("some content")
    
    languages = detector.detect_languages(temp_project)
    
    # 应该返回UNKNOWN或空列表
    assert len(languages) == 0 or Language.UNKNOWN in languages


def test_get_primary_language(temp_project, detector):
    """测试获取主要语言"""
    project_path = Path(temp_project)
    (project_path / "main.py").write_text("print('hello')")
    (project_path / "main.java").write_text("public class Main {}")
    
    primary = detector.get_primary_language(temp_project)
    
    # 应该返回文件数量最多的语言
    assert primary in [Language.PYTHON, Language.JAVA]

