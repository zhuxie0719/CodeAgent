"""
多语言测试生成协调器
根据检测到的语言选择相应的生成器并协调生成任务
"""

from typing import Dict, List, Any
from pathlib import Path
import logging

from .language_detector import Language
from .generators.python_generator import PythonTestGenerator
from .generators.java_generator import JavaTestGenerator
from .generators.cpp_generator import CppTestGenerator

logger = logging.getLogger(__name__)


class MultiLanguageTestGenerator:
    """多语言测试生成协调器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.docker_runner = config.get("docker_runner")
        self.use_docker = config.get("use_docker", False)
        
        # 初始化各语言生成器（传递docker_runner）
        generator_config = {
            **config,
            "docker_runner": self.docker_runner,
            "use_docker": self.use_docker
        }
        self.generators = {
            Language.PYTHON: PythonTestGenerator(generator_config),
            Language.JAVA: JavaTestGenerator(generator_config),
            Language.CPP: CppTestGenerator(generator_config),
            Language.C: CppTestGenerator(generator_config),  # C和C++使用相同的生成器
        }
    
    async def generate_tests(
        self, 
        project_path: str, 
        language: Language,
        issues: List[Dict] = None,
        issue_description: str = None
    ) -> Dict[str, Any]:
        """
        为指定语言生成测试
        
        Args:
            project_path: 项目根路径
            language: 编程语言
            issues: 检测到的问题列表
            issue_description: 问题描述
            
        Returns:
            生成结果字典
        """
        generator = self.generators.get(language)
        if not generator:
            return {
                "success": False,
                "error": f"不支持的语言: {language.value}",
                "tests_dir": None,
                "generated_tests": []
            }
        
        try:
            result = await generator.generate(
                project_path=project_path,
                issues=issues,
                issue_description=issue_description
            )
            return result
        except Exception as e:
            logger.error(f"为语言 {language.value} 生成测试失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "tests_dir": None,
                "generated_tests": []
            }
    
    async def generate_tests_for_all_languages(
        self,
        project_path: str,
        languages: List[Language],
        issues: List[Dict] = None,
        issue_description: str = None
    ) -> Dict[str, Any]:
        """
        为所有检测到的语言生成测试
        
        Args:
            project_path: 项目根路径
            languages: 检测到的语言列表
            issues: 检测到的问题列表
            issue_description: 问题描述
            
        Returns:
            所有语言的生成结果
        """
        results = {}
        
        for language in languages:
            if language == Language.UNKNOWN:
                continue
            
            logger.info(f"为语言 {language.value} 生成测试...")
            result = await self.generate_tests(
                project_path=project_path,
                language=language,
                issues=issues,
                issue_description=issue_description
            )
            results[language.value] = result
        
        # 汇总结果
        total_tests = sum(r.get("total_tests", 0) for r in results.values())
        all_errors = []
        for r in results.values():
            all_errors.extend(r.get("errors", []))
        
        return {
            "success": total_tests > 0 or len(all_errors) == 0,
            "languages": list(results.keys()),
            "results": results,
            "total_tests": total_tests,
            "errors": all_errors
        }

