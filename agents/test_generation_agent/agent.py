"""
测试生成Agent主类
在修复前为没有tests文件夹的项目自动生成标准的测试文件夹
支持多语言：Python, Java, C/C++
"""

import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

from agents.base_agent import BaseAgent
from .language_detector import LanguageDetector, Language
from .tests_folder_checker import TestsFolderChecker
from .multi_language_generator import MultiLanguageTestGenerator

logger = logging.getLogger(__name__)


class TestGenerationAgent(BaseAgent):
    """测试生成Agent：在修复前生成标准的tests文件夹"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("test_generation_agent", config)
        
        # 语言检测器
        self.language_detector = LanguageDetector()
        
        # 测试文件夹检查器
        self.tests_folder_checker = TestsFolderChecker()
        
        # 多语言测试生成协调器
        self.test_generator = MultiLanguageTestGenerator(config)
    
    async def initialize(self) -> bool:
        """初始化Agent"""
        try:
            self.logger.info("初始化测试生成Agent...")
            # 这里可以添加初始化逻辑，如检查工具是否可用
            self.logger.info("测试生成Agent初始化完成")
            return True
        except Exception as e:
            self.logger.error(f"测试生成Agent初始化失败: {e}")
            return False
    
    def get_capabilities(self) -> List[str]:
        """获取Agent能力列表"""
        return [
            "generate_tests",
            "detect_language",
            "check_tests_folder",
            "generate_python_tests",
            "generate_java_tests",
            "generate_cpp_tests"
        ]
    
    async def process_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理测试生成任务
        
        Args:
            task_id: 任务ID
            task_data: 任务数据，包含：
                - project_path: 项目根路径（必需）
                - issues: 检测到的问题列表（可选）
                - issue_description: 问题描述（可选）
        
        Returns:
            生成结果字典
        """
        try:
            self.logger.info(f"开始处理测试生成任务: {task_id}")
            
            # 获取任务参数
            project_path = task_data.get("project_path")
            issues = task_data.get("issues", [])
            issue_description = task_data.get("issue_description")
            
            if not project_path:
                return {
                    "success": False,
                    "error": "缺少project_path参数",
                    "task_id": task_id
                }
            
            project_path = Path(project_path)
            if not project_path.exists():
                return {
                    "success": False,
                    "error": f"项目路径不存在: {project_path}",
                    "task_id": task_id
                }
            
            # 1. 检测项目语言
            languages = self.language_detector.detect_languages(str(project_path))
            
            if not languages or languages == [Language.UNKNOWN]:
                return {
                    "success": False,
                    "error": "无法检测项目语言",
                    "task_id": task_id,
                    "languages": []
                }
            
            self.logger.info(f"检测到语言: {[lang.value for lang in languages]}")
            
            # 2. 检查是否已有tests文件夹
            if self.tests_folder_checker.has_tests_folder(str(project_path), languages):
                primary_lang = self.language_detector.get_primary_language(str(project_path))
                tests_dir = self.tests_folder_checker.get_tests_dir(str(project_path), primary_lang)
                
                return {
                    "success": True,
                    "message": "tests文件夹已存在",
                    "task_id": task_id,
                    "languages": [lang.value for lang in languages],
                    "tests_dir": str(tests_dir),
                    "skipped": True
                }
            
            # 3. 为每种语言生成tests文件夹
            results = {}
            for language in languages:
                if language == Language.UNKNOWN:
                    continue
                
                self.logger.info(f"为语言 {language.value} 生成测试...")
                result = await self.test_generator.generate_tests(
                    project_path=str(project_path),
                    language=language,
                    issues=issues,
                    issue_description=issue_description
                )
                results[language.value] = result
            
            # 4. 汇总结果
            total_tests = sum(r.get("total_tests", 0) for r in results.values())
            all_errors = []
            for r in results.values():
                all_errors.extend(r.get("errors", []))
            
            # 获取主要语言的tests目录
            primary_lang = self.language_detector.get_primary_language(str(project_path))
            tests_dir = self.tests_folder_checker.get_tests_dir(str(project_path), primary_lang)
            
            success = total_tests > 0 or len(all_errors) == 0
            
            self.logger.info(f"测试生成任务完成: {task_id}, 生成 {total_tests} 个测试文件")
            
            return {
                "success": success,
                "task_id": task_id,
                "languages": [lang.value for lang in languages if lang != Language.UNKNOWN],
                "results": results,
                "tests_dir": str(tests_dir),
                "total_tests": total_tests,
                "errors": all_errors
            }
            
        except Exception as e:
            self.logger.error(f"处理测试生成任务失败: {task_id}, 错误: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id
            }

