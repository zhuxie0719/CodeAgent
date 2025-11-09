"""
Python测试生成器
使用Pynguin和LLM生成Python测试文件
"""

import os
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PythonTestGenerator:
    """Python测试生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.use_pynguin = config.get("use_pynguin", True)
        self.use_llm = config.get("use_llm", True)
        
        # 复用AI测试生成器
        try:
            from agents.test_validation_agent.ai_test_generator import AITestGenerator
            self.ai_generator = AITestGenerator() if self.use_llm else None
        except Exception as e:
            logger.warning(f"无法导入AITestGenerator: {e}")
            self.ai_generator = None
            self.use_llm = False
    
    async def generate(
        self, 
        project_path: str, 
        issues: List[Dict] = None,
        issue_description: str = None
    ) -> Dict[str, Any]:
        """
        生成Python测试
        
        Args:
            project_path: 项目根路径
            issues: 检测到的问题列表
            issue_description: 问题描述
            
        Returns:
            生成结果字典
        """
        tests_dir = Path(project_path) / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        generated_tests = []
        errors = []
        
        # 1. 如果有问题描述，生成重现测试
        if issue_description or issues:
            try:
                reproduction_test = await self._generate_reproduction_test(
                    project_path, issues, issue_description
                )
                if reproduction_test:
                    test_path = tests_dir / "test_reproduction.py"
                    test_path.write_text(reproduction_test, encoding="utf-8")
                    generated_tests.append(str(test_path))
                    logger.info(f"✅ 生成重现测试: {test_path}")
            except Exception as e:
                error_msg = f"生成重现测试失败: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # 2. 使用Pynguin生成覆盖性测试（如果可用）
        if self.use_pynguin:
            try:
                pynguin_result = await self._generate_with_pynguin(project_path, tests_dir)
                if pynguin_result.get("success"):
                    generated_tests.extend(pynguin_result.get("test_files", []))
                    logger.info(f"✅ Pynguin生成 {len(pynguin_result.get('test_files', []))} 个测试文件")
            except Exception as e:
                error_msg = f"Pynguin生成失败: {e}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # 3. 使用LLM生成覆盖性测试
        if self.use_llm and self.ai_generator:
            try:
                llm_result = await self._generate_with_llm(project_path, tests_dir, issues)
                if llm_result.get("success"):
                    generated_tests.extend(llm_result.get("test_files", []))
                    logger.info(f"✅ LLM生成 {len(llm_result.get('test_files', []))} 个测试文件")
            except Exception as e:
                error_msg = f"LLM生成失败: {e}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # 4. 创建conftest.py（如果不存在）
        conftest_path = tests_dir / "conftest.py"
        if not conftest_path.exists():
            try:
                conftest_content = self._generate_conftest(project_path)
                conftest_path.write_text(conftest_content, encoding="utf-8")
                logger.info(f"✅ 生成conftest.py: {conftest_path}")
            except Exception as e:
                error_msg = f"生成conftest.py失败: {e}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # 5. 创建__init__.py（如果不存在）
        init_path = tests_dir / "__init__.py"
        if not init_path.exists():
            init_path.write_text("# Tests package\n", encoding="utf-8")
        
        return {
            "success": len(generated_tests) > 0 or len(errors) == 0,
            "tests_dir": str(tests_dir),
            "generated_tests": generated_tests,
            "total_tests": len(generated_tests),
            "errors": errors
        }
    
    async def _generate_reproduction_test(
        self, 
        project_path: str, 
        issues: List[Dict],
        issue_description: str
    ) -> Optional[str]:
        """生成重现问题的测试"""
        if not self.ai_generator:
            return None
        
        # 构建提示词
        prompt_parts = []
        if issue_description:
            prompt_parts.append(f"问题描述：{issue_description}")
        if issues:
            issues_text = "\n".join([
                f"- {issue.get('message', '')} (文件: {issue.get('file_path', '')}, 行: {issue.get('line', '')})"
                for issue in issues[:5]  # 最多5个问题
            ])
            prompt_parts.append(f"检测到的问题：\n{issues_text}")
        
        if not prompt_parts:
            return None
        
        prompt = f"""
根据以下信息，生成一个能重现问题的pytest测试：

{chr(10).join(prompt_parts)}

要求：
1. 生成pytest格式的测试
2. 测试应该能够重现问题
3. 包含必要的断言
4. 测试文件应该命名为test_reproduction.py
5. 只返回Python代码，不要包含markdown标记
"""
        
        # 使用AI生成器生成测试
        try:
            # 创建一个临时源文件用于生成测试
            temp_source = Path(project_path) / "temp_reproduction_source.py"
            temp_source.write_text("# Temporary file for reproduction test generation\n", encoding="utf-8")
            
            result = await self.ai_generator.generate_test_file(
                str(temp_source),
                project_path
            )
            
            # 清理临时文件
            if temp_source.exists():
                temp_source.unlink()
            
            if result.get("success"):
                # 读取生成的测试文件内容
                test_file_path = result.get("test_file_path")
                if test_file_path and os.path.exists(test_file_path):
                    with open(test_file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 修改内容以适应重现测试
                    content = content.replace("unittest", "pytest")
                    content = content.replace("import unittest", "import pytest")
                    # 移除unittest.TestCase继承
                    content = content.replace("(unittest.TestCase)", "")
                    
                    return content
            
        except Exception as e:
            logger.error(f"生成重现测试时出错: {e}")
        
        return None
    
    async def _generate_with_pynguin(self, project_path: str, tests_dir: Path) -> Dict[str, Any]:
        """使用Pynguin生成测试"""
        try:
            # 检查Pynguin是否可用
            result = subprocess.run(
                ["pynguin", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                return {"success": False, "error": "Pynguin未安装或不可用", "test_files": []}
        except FileNotFoundError:
            return {"success": False, "error": "Pynguin未安装", "test_files": []}
        except Exception as e:
            return {"success": False, "error": f"检查Pynguin失败: {e}", "test_files": []}
        
        try:
            # 查找Python源文件
            source_files = list(Path(project_path).rglob("*.py"))
            source_files = [f for f in source_files if "test" not in str(f) and "__pycache__" not in str(f)]
            
            if not source_files:
                return {"success": False, "error": "未找到Python源文件", "test_files": []}
            
            # 使用Pynguin生成测试（为第一个模块生成）
            # 注意：Pynguin需要项目可以导入，可能需要先安装项目
            module_path = source_files[0].relative_to(project_path)
            module_name = str(module_path).replace("/", ".").replace("\\", ".").replace(".py", "")
            
            result = subprocess.run(
                [
                    "pynguin",
                    "--project-path", str(project_path),
                    "--output-path", str(tests_dir),
                    "--module", module_name,
                    "--test-type", "pytest"
                ],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=project_path
            )
            
            if result.returncode == 0:
                # 查找生成的测试文件
                test_files = list(tests_dir.glob("test_*.py"))
                return {
                    "success": True,
                    "test_files": [str(f) for f in test_files],
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "test_files": []
                }
        
        except subprocess.TimeoutError:
            return {"success": False, "error": "Pynguin执行超时", "test_files": []}
        except Exception as e:
            return {"success": False, "error": str(e), "test_files": []}
    
    async def _generate_with_llm(
        self, 
        project_path: str, 
        tests_dir: Path,
        issues: List[Dict] = None
    ) -> Dict[str, Any]:
        """使用LLM生成覆盖性测试"""
        if not self.ai_generator:
            return {"success": False, "error": "AI生成器不可用", "test_files": []}
        
        try:
            # 查找主要的Python源文件
            source_files = list(Path(project_path).rglob("*.py"))
            source_files = [
                f for f in source_files 
                if "test" not in str(f) 
                and "__pycache__" not in str(f)
                and "__init__.py" != f.name
            ][:5]  # 最多为5个文件生成测试
            
            generated_files = []
            
            for source_file in source_files:
                try:
                    result = await self.ai_generator.generate_test_file(
                        str(source_file),
                        project_path
                    )
                    
                    if result.get("success"):
                        test_file_path = result.get("test_file_path")
                        if test_file_path and os.path.exists(test_file_path):
                            generated_files.append(test_file_path)
                
                except Exception as e:
                    logger.warning(f"为 {source_file} 生成测试失败: {e}")
                    continue
            
            return {
                "success": len(generated_files) > 0,
                "test_files": generated_files
            }
        
        except Exception as e:
            return {"success": False, "error": str(e), "test_files": []}
    
    def _generate_conftest(self, project_path: str) -> str:
        """生成conftest.py"""
        project = Path(project_path)
        
        # 检查项目结构，确定导入路径
        src_dirs = []
        if (project / "src").exists():
            src_dirs.append("src")
        if (project / "lib").exists():
            src_dirs.append("lib")
        
        conftest_content = """\"\"\"
pytest配置文件
定义共享的测试fixtures和配置
\"\"\"

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

"""
        
        # 如果有src目录，添加src到路径
        if src_dirs:
            for src_dir in src_dirs:
                conftest_content += f"sys.path.insert(0, str(project_root / '{src_dir}'))\n"
        
        conftest_content += """
import pytest


@pytest.fixture
def sample_data():
    \"\"\"提供测试数据\"\"\"
    return {"key": "value"}


@pytest.fixture
def temp_file(tmp_path):
    \"\"\"创建临时文件\"\"\"
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")
    return file_path
"""
        
        return conftest_content

