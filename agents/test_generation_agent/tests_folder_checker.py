"""
测试文件夹检查器
检查项目是否已有tests文件夹，是否符合标准结构
"""

from pathlib import Path
from typing import Dict, List, Optional
from .language_detector import Language


class TestsFolderChecker:
    """测试文件夹存在性检查器"""
    
    def has_tests_folder(self, project_path: str, languages: List[Language]) -> bool:
        """
        检查项目是否已有tests文件夹
        
        Args:
            project_path: 项目根路径
            languages: 检测到的语言列表
            
        Returns:
            如果已有符合标准的tests文件夹，返回True
        """
        for language in languages:
            tests_dir = self.get_tests_dir(project_path, language)
            if tests_dir.exists() and self._has_test_files(tests_dir, language):
                return True
        return False
    
    def get_tests_dir(self, project_path: str, language: Language) -> Path:
        """
        获取指定语言的tests目录路径
        
        Args:
            project_path: 项目根路径
            language: 编程语言
            
        Returns:
            tests目录路径
        """
        project = Path(project_path)
        
        if language == Language.JAVA:
            # Java: Maven/Gradle标准目录结构
            return project / "src" / "test" / "java"
        else:
            # Python, C/C++, Go, JavaScript: 标准tests目录
            return project / "tests"
    
    def _has_test_files(self, tests_dir: Path, language: Language) -> bool:
        """
        检查tests目录是否有测试文件
        
        Args:
            tests_dir: tests目录路径
            language: 编程语言
            
        Returns:
            如果有测试文件，返回True
        """
        if not tests_dir.exists():
            return False
        
        # 根据语言检查相应的测试文件模式
        if language == Language.PYTHON:
            # Python: test_*.py
            return any(tests_dir.glob("test_*.py")) or any(tests_dir.rglob("test_*.py"))
        elif language == Language.JAVA:
            # Java: *Test.java
            return any(tests_dir.glob("**/*Test.java")) or any(tests_dir.rglob("*Test.java"))
        elif language in [Language.CPP, Language.C]:
            # C/C++: test_*.cpp, test_*.c
            return (any(tests_dir.glob("test_*.cpp")) or 
                   any(tests_dir.glob("test_*.c")) or
                   any(tests_dir.rglob("test_*.cpp")) or
                   any(tests_dir.rglob("test_*.c")))
        elif language == Language.GO:
            # Go: *_test.go（与源文件同目录）
            return any(tests_dir.parent.rglob("*_test.go"))
        elif language in [Language.JAVASCRIPT, Language.TYPESCRIPT]:
            # JavaScript: *.test.js, *.spec.js
            return (any(tests_dir.glob("*.test.js")) or
                   any(tests_dir.glob("*.spec.js")) or
                   any(tests_dir.rglob("*.test.js")) or
                   any(tests_dir.rglob("*.spec.js")))
        
        return False
    
    def check_tests_structure(self, project_path: str, language: Language) -> Dict[str, any]:
        """
        检查tests文件夹结构是否符合标准
        
        Args:
            project_path: 项目根路径
            language: 编程语言
            
        Returns:
            检查结果字典
        """
        tests_dir = self.get_tests_dir(project_path, language)
        
        result = {
            "has_tests_dir": tests_dir.exists(),
            "has_test_files": False,
            "has_config_file": False,
            "tests_dir": str(tests_dir),
            "language": language.value
        }
        
        if tests_dir.exists():
            result["has_test_files"] = self._has_test_files(tests_dir, language)
            result["has_config_file"] = self._check_config_file(project_path, language)
        
        return result
    
    def _check_config_file(self, project_path: str, language: Language) -> bool:
        """
        检查是否有测试框架配置文件
        
        Args:
            project_path: 项目根路径
            language: 编程语言
            
        Returns:
            如果有配置文件，返回True
        """
        project = Path(project_path)
        
        if language == Language.PYTHON:
            # Python: conftest.py, pytest.ini
            tests_dir = project / "tests"
            return ((tests_dir / "conftest.py").exists() or
                   (project / "pytest.ini").exists() or
                   (project / "setup.cfg").exists())
        elif language == Language.JAVA:
            # Java: pom.xml或build.gradle中有JUnit依赖
            pom_path = project / "pom.xml"
            gradle_path = project / "build.gradle"
            if pom_path.exists() or gradle_path.exists():
                # 简单检查，实际应该解析XML/Gradle文件
                return True
        elif language in [Language.CPP, Language.C]:
            # C/C++: CMakeLists.txt中有Google Test配置
            cmake_path = project / "CMakeLists.txt"
            if cmake_path.exists():
                # 简单检查，实际应该解析CMake文件
                return True
        elif language == Language.GO:
            # Go: go.mod
            return (project / "go.mod").exists()
        elif language in [Language.JAVASCRIPT, Language.TYPESCRIPT]:
            # JavaScript: package.json中有测试框架配置
            package_json = project / "package.json"
            if package_json.exists():
                # 简单检查，实际应该解析JSON文件
                return True
        
        return False

