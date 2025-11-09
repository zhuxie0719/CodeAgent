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
        self.use_docker = config.get("use_docker", False)
        self.docker_runner = config.get("docker_runner")
        
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
                logger.info(f"开始使用Pynguin生成测试，项目路径: {project_path}")
                pynguin_result = await self._generate_with_pynguin(project_path, tests_dir)
                if pynguin_result.get("success"):
                    pynguin_files = pynguin_result.get("test_files", [])
                    generated_tests.extend(pynguin_files)
                    logger.info(f"✅ Pynguin生成 {len(pynguin_files)} 个测试文件: {pynguin_files}")
                else:
                    error_msg = pynguin_result.get("error", "Pynguin生成失败")
                    logger.warning(f"⚠️ Pynguin生成失败: {error_msg}")
                    if pynguin_result.get("output"):
                        logger.debug(f"Pynguin输出: {pynguin_result.get('output')[:500]}")
            except Exception as e:
                error_msg = f"Pynguin生成异常: {e}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)
        
        # 3. 使用LLM生成覆盖性测试（如果没有生成重现测试，至少生成覆盖性测试）
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
        
        # 如果没有任何测试文件生成，尝试生成基本的覆盖性测试
        if len(generated_tests) == 0 and self.use_llm and self.ai_generator:
            try:
                logger.info("未生成任何测试文件，尝试生成基本覆盖性测试...")
                basic_test = await self._generate_basic_coverage_test(project_path, tests_dir)
                if basic_test:
                    test_path = tests_dir / "test_basic.py"
                    test_path.write_text(basic_test, encoding="utf-8")
                    generated_tests.append(str(test_path))
                    logger.info(f"✅ 生成基本覆盖性测试: {test_path}")
            except Exception as e:
                error_msg = f"生成基本覆盖性测试失败: {e}"
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
        
        # 最终统计：确保包含所有生成的测试文件
        final_test_files = list(tests_dir.glob("test_*.py"))
        final_count = len(final_test_files)
        
        logger.info(f"测试生成完成: 统计={len(generated_tests)}, 实际文件数={final_count}")
        
        return {
            "success": len(generated_tests) > 0 or final_count > 0,
            "tests_dir": str(tests_dir),
            "generated_tests": generated_tests,
            "total_tests": len(generated_tests) if len(generated_tests) > 0 else final_count,
            "actual_file_count": final_count,  # 实际文件数
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
        
        # 查找项目中的主要Python源文件
        project = Path(project_path).resolve()  # 使用绝对路径
        if not project.exists():
            logger.warning(f"项目路径不存在: {project_path}, 绝对路径: {project}")
            return None
        
        # 先尝试直接查找项目根目录下的.py文件
        source_files = []
        # 1. 查找项目根目录下的.py文件
        root_py_files = [f for f in project.glob("*.py") if f.is_file()]
        source_files.extend(root_py_files)
        
        # 2. 递归查找子目录中的.py文件（排除tests目录）
        for py_file in project.rglob("*.py"):
            if (py_file.is_file() and 
                "test" not in str(py_file).lower() and 
                "__pycache__" not in str(py_file) and
                "__init__.py" != py_file.name and
                "temp" not in py_file.name.lower() and
                py_file not in source_files):  # 避免重复
                source_files.append(py_file)
        
        # 过滤：确保文件存在且不是测试文件
        source_files = [f for f in source_files if f.exists() and f.is_file()]
        
        if not source_files:
            # 列出项目目录内容以便调试
            try:
                all_items = list(project.iterdir())
                print(f"[DEBUG] 项目目录内容: {[item.name for item in all_items]}")
                # 列出所有.py文件
                all_py = list(project.rglob("*.py"))
                print(f"[DEBUG] 所有Python文件: {[str(f) for f in all_py]}")
                # 列出根目录的.py文件
                root_py = list(project.glob("*.py"))
                print(f"[DEBUG] 根目录Python文件: {[str(f) for f in root_py]}")
            except Exception as e:
                print(f"[DEBUG] 无法列出项目目录: {e}")
            logger.warning(f"未找到Python源文件，无法生成重现测试。项目路径: {project_path}, 绝对路径: {project}")
            return None
        
        # 使用第一个源文件（通常是主文件）
        main_source_file = source_files[0]
        source_content = main_source_file.read_text(encoding="utf-8")
        module_name = main_source_file.stem  # 文件名（不含扩展名）
        
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
        
        # 限制源代码长度
        if len(source_content) > 2000:
            source_content = source_content[:2000] + "\n# ... (代码已截断)"
        
        prompt = f"""为以下Python文件生成pytest重现测试：

文件：{main_source_file.name}
模块名：{module_name}

源代码：
{source_content}

问题信息：
{chr(10).join(prompt_parts)}

要求：
1. 生成pytest格式的测试（使用pytest，不是unittest）
2. 测试应该能够重现问题
3. 包含必要的断言
4. 测试文件应该命名为test_reproduction.py
5. 只返回Python代码，不要包含markdown标记（如```python或```）
6. 确保代码语法正确，可以直接运行

重要：模块导入设置
- 测试文件位于 tests/ 目录下
- 被测试文件位于项目根目录
- 必须在文件开头添加以下导入路径设置：
```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import {module_name}
```

7. 确保所有函数调用语法正确
8. 使用pytest的断言方式（assert语句），不要使用unittest的断言方法

只返回Python代码，不要其他内容。"""
        
        # 直接调用LLM API生成测试
        try:
            # 使用aiohttp（已在requirements.txt中）
            import aiohttp
            from api.deepseek_config import deepseek_config
            
            if not deepseek_config or not deepseek_config.is_configured():
                logger.warning("DeepSeek配置不可用，无法生成重现测试")
                return None
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {deepseek_config.api_key}"
            }
            
            data = {
                "model": deepseek_config.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": deepseek_config.temperature,
                "max_tokens": deepseek_config.max_tokens
            }
            
            timeout = aiohttp.ClientTimeout(total=60.0)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{deepseek_config.base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        test_code = result["choices"][0]["message"]["content"]
                        
                        # 清理markdown标记
                        test_code = self._clean_markdown(test_code)
                        
                        return test_code
                    else:
                        error_text = await response.text()
                        logger.error(f"LLM API调用失败: {response.status} - {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"生成重现测试时出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return None
    
    def _clean_markdown(self, content: str) -> str:
        """清理markdown标记"""
        if not content:
            return content
        
        lines = content.split('\n')
        cleaned_lines = []
        skip_start = False
        
        for line in lines:
            if line.strip().startswith('```'):
                if not skip_start:
                    skip_start = True
                    continue
                else:
                    break
            
            if skip_start:
                cleaned_lines.append(line)
        
        # 移除末尾的markdown标记
        while cleaned_lines and cleaned_lines[-1].strip().startswith('```'):
            cleaned_lines.pop()
        
        # 移除末尾空行
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    async def _generate_basic_coverage_test(
        self, 
        project_path: str, 
        tests_dir: Path
    ) -> Optional[str]:
        """生成基本的覆盖性测试（当重现测试生成失败时使用）"""
        # 查找项目中的主要Python源文件
        project = Path(project_path).resolve()
        if not project.exists():
            logger.warning(f"项目路径不存在: {project}")
            return None
        
        # 先尝试直接查找项目根目录下的.py文件
        source_files = []
        root_py_files = [f for f in project.glob("*.py") if f.is_file()]
        source_files.extend(root_py_files)
        
        # 递归查找子目录中的.py文件（排除tests目录）
        for py_file in project.rglob("*.py"):
            if (py_file.is_file() and 
                "test" not in str(py_file).lower() and 
                "__pycache__" not in str(py_file) and
                "__init__.py" != py_file.name and
                "temp" not in py_file.name.lower() and
                py_file not in source_files):
                source_files.append(py_file)
        
        # 过滤：确保文件存在且不是测试文件
        source_files = [f for f in source_files if f.exists() and f.is_file()]
        
        if not source_files:
            logger.warning(f"未找到Python源文件。项目路径: {project}")
            # 列出项目目录内容以便调试
            try:
                all_items = list(project.iterdir())
                logger.info(f"项目目录内容: {[item.name for item in all_items]}")
                all_py = list(project.rglob("*.py"))
                logger.info(f"所有Python文件: {[str(f) for f in all_py]}")
            except Exception as e:
                logger.info(f"无法列出项目目录: {e}")
            return None
        
        # 使用第一个源文件
        main_source_file = source_files[0]
        source_content = main_source_file.read_text(encoding="utf-8")
        module_name = main_source_file.stem
        
        # 限制源代码长度
        if len(source_content) > 2000:
            source_content = source_content[:2000] + "\n# ... (代码已截断)"
        
        prompt = f"""为以下Python文件生成pytest测试：

文件：{main_source_file.name}
模块名：{module_name}

源代码：
{source_content}

要求：
1. 生成pytest格式的测试（使用pytest，不是unittest）
2. 测试所有公共函数
3. 包含正常和异常情况
4. 只返回Python代码，不要包含markdown标记

重要：模块导入设置
- 测试文件位于 tests/ 目录下
- 被测试文件位于项目根目录
- 必须在文件开头添加以下导入路径设置：
```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import {module_name}
```

5. 使用pytest的断言方式（assert语句）
6. 确保代码语法正确，可以直接运行

只返回Python代码，不要其他内容。"""
        
        # 调用LLM API生成测试
        try:
            import aiohttp
            from api.deepseek_config import deepseek_config
            
            if not deepseek_config or not deepseek_config.is_configured():
                logger.warning("DeepSeek配置不可用")
                return None
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {deepseek_config.api_key}"
            }
            
            data = {
                "model": deepseek_config.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": deepseek_config.temperature,
                "max_tokens": deepseek_config.max_tokens
            }
            
            timeout = aiohttp.ClientTimeout(total=60.0)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{deepseek_config.base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        test_code = result["choices"][0]["message"]["content"]
                        test_code = self._clean_markdown(test_code)
                        return test_code
                    else:
                        error_text = await response.text()
                        logger.error(f"LLM API调用失败: {response.status} - {error_text}")
                        return None
        
        except Exception as e:
            logger.error(f"生成基本覆盖性测试时出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    async def _generate_with_pynguin(self, project_path: str, tests_dir: Path) -> Dict[str, Any]:
        """使用Pynguin生成测试（支持Docker）"""
        # 如果启用Docker，在Docker内执行
        if self.use_docker and self.docker_runner:
            return await self._generate_with_pynguin_docker(project_path, tests_dir)
        else:
            return await self._generate_with_pynguin_local(project_path, tests_dir)
    
    async def _generate_with_pynguin_docker(self, project_path: str, tests_dir: Path) -> Dict[str, Any]:
        """在Docker容器内使用Pynguin生成测试"""
        try:
            project = Path(project_path).absolute()
            
            # 1. 在Docker内安装项目依赖和Pynguin
            install_cmd = [
                "sh", "-c",
                f"cd /app/test_project && "
                f"(pip install -r requirements.txt 2>&1 || echo '依赖安装完成') && "
                f"(pip install pynguin 2>&1 || echo 'Pynguin已安装')"
            ]
            
            install_result = await self.docker_runner.run_command(
                project_path=project,
                command=install_cmd,
                timeout=300,
                read_only=False  # 可写挂载，允许安装依赖
            )
            
            if not install_result.get("success"):
                logger.warning(f"依赖安装失败，但继续执行: {install_result.get('error', '')}")
            
            # 2. 查找Python源文件
            source_files = list(project.rglob("*.py"))
            source_files = [f for f in source_files if "test" not in str(f) and "__pycache__" not in str(f)]
            
            if not source_files:
                return {"success": False, "error": "未找到Python源文件", "test_files": []}
            
            # 3. 在Docker内执行Pynguin
            module_path = source_files[0].relative_to(project)
            module_name = str(module_path).replace("/", ".").replace("\\", ".").replace(".py", "")
            
            pynguin_cmd = [
                "sh", "-c",
                f"cd /app/test_project && "
                f"pynguin --project-path /app/test_project "
                f"--output-path /app/test_project/tests "
                f"--module {module_name} "
                f"--test-type pytest 2>&1"
            ]
            
            logger.info(f"执行Pynguin命令: {' '.join(pynguin_cmd)}")
            result = await self.docker_runner.run_command(
                project_path=project,
                command=pynguin_cmd,
                timeout=120,
                read_only=False  # 可写挂载，允许生成测试文件
            )
            
            logger.info(f"Pynguin执行结果: success={result.get('success')}, error={result.get('error', 'None')}")
            if result.get("stdout"):
                logger.debug(f"Pynguin stdout: {result.get('stdout')[:500]}")
            if result.get("stderr"):
                logger.debug(f"Pynguin stderr: {result.get('stderr')[:500]}")
            
            if result.get("success"):
                # 查找生成的测试文件（通过volume自动同步回本地）
                test_files = list(tests_dir.glob("test_*.py"))
                logger.info(f"找到 {len(test_files)} 个Pynguin生成的测试文件")
                return {
                    "success": len(test_files) > 0,
                    "test_files": [str(f) for f in test_files],
                    "output": result.get("stdout", ""),
                    "docker_executed": True
                }
            else:
                error_msg = result.get("error", "Pynguin执行失败")
                logger.warning(f"Pynguin执行失败: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "test_files": [],
                    "output": result.get("stdout", ""),
                    "stderr": result.get("stderr", "")
                }
        
        except Exception as e:
            logger.error(f"Docker内执行Pynguin失败: {e}")
            return {"success": False, "error": str(e), "test_files": []}
    
    async def _generate_with_pynguin_local(self, project_path: str, tests_dir: Path) -> Dict[str, Any]:
        """在本地使用Pynguin生成测试"""
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

