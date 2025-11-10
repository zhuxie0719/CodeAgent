"""
Java测试生成器
使用EvoSuite和LLM生成JUnit测试文件
"""

import os
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import json
import httpx

logger = logging.getLogger(__name__)


class JavaTestGenerator:
    """Java测试生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.use_evosuite = config.get("use_evosuite", True)
        self.use_llm = config.get("use_llm", True)
        self.evosuite_jar = config.get("evosuite_jar", None)
        self.use_docker = config.get("use_docker", False)
        self.docker_runner = config.get("docker_runner")
        
        # 复用AI分析器
        try:
            from tools.ai_static_analyzer import AIMultiLanguageAnalyzer
            self.ai_analyzer = AIMultiLanguageAnalyzer() if self.use_llm else None
        except Exception as e:
            logger.warning(f"无法导入AIMultiLanguageAnalyzer: {e}")
            self.ai_analyzer = None
            self.use_llm = False
    
    async def generate(
        self, 
        project_path: str, 
        issues: List[Dict] = None,
        issue_description: str = None
    ) -> Dict[str, Any]:
        """
        生成Java测试
        
        Args:
            project_path: 项目根路径
            issues: 检测到的问题列表
            issue_description: 问题描述
            
        Returns:
            生成结果字典
        """
        # Java标准目录结构：src/test/java
        project = Path(project_path)
        test_dir = project / "src" / "test" / "java"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        generated_tests = []
        errors = []
        
        # 1. 如果有问题描述，生成重现测试
        if issue_description or issues:
            try:
                reproduction_test = await self._generate_reproduction_test(
                    project_path, issues, issue_description, test_dir
                )
                if reproduction_test:
                    generated_tests.append(reproduction_test)
                    logger.info(f"✅ 生成重现测试: {reproduction_test}")
            except Exception as e:
                error_msg = f"生成重现测试失败: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # 2. 使用EvoSuite生成覆盖性测试（如果可用）
        if self.use_evosuite:
            try:
                evosuite_result = await self._generate_with_evosuite(project_path, test_dir)
                if evosuite_result.get("success"):
                    generated_tests.extend(evosuite_result.get("test_files", []))
                    logger.info(f"✅ EvoSuite生成 {len(evosuite_result.get('test_files', []))} 个测试文件")
            except Exception as e:
                error_msg = f"EvoSuite生成失败: {e}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # 3. 使用LLM生成覆盖性测试
        if self.use_llm and self.ai_analyzer:
            try:
                llm_result = await self._generate_with_llm(project_path, test_dir, issues)
                if llm_result.get("success"):
                    generated_tests.extend(llm_result.get("test_files", []))
                    logger.info(f"✅ LLM生成 {len(llm_result.get('test_files', []))} 个测试文件")
            except Exception as e:
                error_msg = f"LLM生成失败: {e}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # 4. 检查并更新pom.xml或build.gradle（添加JUnit依赖）
        try:
            self._ensure_junit_dependency(project_path)
        except Exception as e:
            error_msg = f"更新依赖配置失败: {e}"
            logger.warning(error_msg)
            errors.append(error_msg)
        
        return {
            "success": len(generated_tests) > 0 or len(errors) == 0,
            "tests_dir": str(test_dir),
            "generated_tests": generated_tests,
            "total_tests": len(generated_tests),
            "errors": errors
        }
    
    async def _generate_reproduction_test(
        self, 
        project_path: str, 
        issues: List[Dict],
        issue_description: str,
        test_dir: Path
    ) -> Optional[str]:
        """生成重现问题的JUnit测试"""
        if not self.ai_analyzer:
            return None
        
        # 构建提示词
        prompt_parts = []
        if issue_description:
            prompt_parts.append(f"问题描述：{issue_description}")
        if issues:
            issues_text = "\n".join([
                f"- {issue.get('message', '')} (文件: {issue.get('file_path', '')}, 行: {issue.get('line', '')})"
                for issue in issues[:5]
            ])
            prompt_parts.append(f"检测到的问题：\n{issues_text}")
        
        if not prompt_parts:
            return None
        
        prompt = f"""
根据以下信息，生成一个能重现问题的JUnit 5测试：

{chr(10).join(prompt_parts)}

要求：
1. 生成JUnit 5格式的测试（使用org.junit.jupiter.api）
2. 测试应该能够重现问题
3. 包含必要的断言（使用Assertions类）
4. 测试类应该命名为ReproductionTest
5. 只返回Java代码，不要包含markdown标记
6. 包含必要的import语句
"""
        
        # 使用AI分析器生成测试代码
        try:
            # 调用LLM生成测试代码
            test_code = await self._call_llm_for_java_test(prompt)
            
            if test_code:
                # 确定测试文件路径
                test_file_path = test_dir / "ReproductionTest.java"
                test_file_path.write_text(test_code, encoding="utf-8")
                return str(test_file_path)
        
        except Exception as e:
            logger.error(f"生成重现测试时出错: {e}")
        
        return None
    
    async def _call_llm_for_java_test(self, prompt: str) -> Optional[str]:
        """调用LLM生成Java测试代码"""
        try:
            from api.deepseek_config import deepseek_config
            
            if not deepseek_config.is_configured():
                return None
            
            headers = {
                "Authorization": f"Bearer {deepseek_config.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": deepseek_config.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的Java测试工程师，擅长编写高质量的JUnit测试。请根据提供的信息生成完整的JUnit 5测试类。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 4000
            }
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{deepseek_config.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    test_code = result["choices"][0]["message"]["content"]
                    
                    # 清理markdown标记
                    test_code = self._clean_markdown(test_code)
                    
                    return test_code
                else:
                    logger.error(f"LLM API调用失败: {response.status_code} - {response.text}")
                    return None
        
        except Exception as e:
            logger.error(f"调用LLM生成Java测试失败: {e}")
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
        
        while cleaned_lines and cleaned_lines[-1].strip().startswith('```'):
            cleaned_lines.pop()
        
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    async def _generate_with_evosuite(self, project_path: str, test_dir: Path) -> Dict[str, Any]:
        """使用EvoSuite生成测试（支持Docker）"""
        # 如果启用Docker，在Docker内执行
        if self.use_docker and self.docker_runner:
            return await self._generate_with_evosuite_docker(project_path, test_dir)
        else:
            return await self._generate_with_evosuite_local(project_path, test_dir)
    
    async def _generate_with_evosuite_docker(self, project_path: str, test_dir: Path) -> Dict[str, Any]:
        """在Docker容器内使用EvoSuite生成测试"""
        try:
            project = Path(project_path).absolute()
            
            # 1. 在Docker内编译项目
            compile_cmd = [
                "sh", "-c",
                f"cd /app/test_project && "
                f"(mvn compile 2>&1 || echo '编译完成')"
            ]
            
            compile_result = await self.docker_runner.run_command(
                project_path=project,
                command=compile_cmd,
                timeout=300,
                read_only=False
            )
            
            if not compile_result.get("success"):
                logger.warning(f"项目编译失败，但继续执行: {compile_result.get('error', '')}")
            
            # 2. 在Docker内下载/使用EvoSuite
            evosuite_cmd = [
                "sh", "-c",
                f"cd /app/test_project && "
                f"(wget -q https://github.com/EvoSuite/evosuite/releases/download/v1.2.0/evosuite-1.2.0.jar -O evosuite.jar 2>&1 || echo 'EvoSuite已存在') && "
                f"java -jar evosuite.jar -target target/classes -projectCP target/classes -Dtest_dir=src/test/java 2>&1"
            ]
            
            result = await self.docker_runner.run_command(
                project_path=project,
                command=evosuite_cmd,
                timeout=300,
                read_only=False
            )
            
            if result.get("success"):
                # 查找生成的测试文件
                test_files = list(test_dir.rglob("*Test.java"))
                return {
                    "success": len(test_files) > 0,
                    "test_files": [str(f) for f in test_files],
                    "output": result.get("stdout", ""),
                    "docker_executed": True
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "EvoSuite执行失败"),
                    "test_files": []
                }
        
        except Exception as e:
            logger.error(f"Docker内执行EvoSuite失败: {e}")
            return {"success": False, "error": str(e), "test_files": []}
    
    async def _generate_with_evosuite_local(self, project_path: str, test_dir: Path) -> Dict[str, Any]:
        """在本地使用EvoSuite生成测试"""
        # 检查EvoSuite JAR是否存在
        if not self.evosuite_jar or not os.path.exists(self.evosuite_jar):
            # 尝试在项目根目录查找
            project = Path(project_path)
            possible_paths = [
                project / "evosuite.jar",
                project.parent / "evosuite.jar",
                Path.cwd() / "evosuite.jar"
            ]
            
            for path in possible_paths:
                if path.exists():
                    self.evosuite_jar = str(path)
                    break
            else:
                return {
                    "success": False,
                    "error": "EvoSuite JAR文件未找到，请下载并配置evosuite_jar路径",
                    "test_files": []
                }
        
        try:
            # 检查项目是否已编译（需要target/classes）
            project = Path(project_path)
            classes_dir = project / "target" / "classes"
            
            if not classes_dir.exists():
                # 尝试编译项目
                logger.info("尝试编译Java项目...")
                compile_result = subprocess.run(
                    ["mvn", "compile"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if compile_result.returncode != 0:
                    return {
                        "success": False,
                        "error": f"项目编译失败: {compile_result.stderr}",
                        "test_files": []
                    }
            
            # 查找Java源文件
            java_files = list(project.rglob("*.java"))
            java_files = [f for f in java_files if "test" not in str(f).lower()]
            
            if not java_files:
                return {"success": False, "error": "未找到Java源文件", "test_files": []}
            
            # 使用EvoSuite生成测试（为第一个类生成）
            target_class = java_files[0].relative_to(project / "src" / "main" / "java")
            class_name = str(target_class).replace("/", ".").replace("\\", ".").replace(".java", "")
            
            result = subprocess.run(
                [
                    "java",
                    "-jar", self.evosuite_jar,
                    "-target", str(classes_dir),
                    "-projectCP", str(classes_dir),
                    "-class", class_name,
                    "-Dtest_dir", str(test_dir)
                ],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=project_path
            )
            
            if result.returncode == 0:
                # 查找生成的测试文件
                test_files = list(test_dir.rglob("*Test.java"))
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
            return {"success": False, "error": "EvoSuite执行超时", "test_files": []}
        except Exception as e:
            return {"success": False, "error": str(e), "test_files": []}
    
    async def _generate_with_llm(
        self, 
        project_path: str, 
        test_dir: Path,
        issues: List[Dict] = None
    ) -> Dict[str, Any]:
        """使用LLM生成覆盖性测试"""
        if not self.ai_analyzer:
            return {"success": False, "error": "AI分析器不可用", "test_files": []}
        
        try:
            # 查找主要的Java源文件
            project = Path(project_path)
            source_dir = project / "src" / "main" / "java"
            
            if not source_dir.exists():
                return {"success": False, "error": "未找到src/main/java目录", "test_files": []}
            
            java_files = list(source_dir.rglob("*.java"))
            java_files = [
                f for f in java_files 
                if "test" not in str(f).lower()
                and "__" not in str(f)
            ][:3]  # 最多为3个文件生成测试
            
            generated_files = []
            
            for java_file in java_files:
                try:
                    # 读取Java源文件
                    with open(java_file, 'r', encoding='utf-8') as f:
                        source_content = f.read(2000)  # 限制长度
                    
                    # 构建提示词
                    class_name = java_file.stem
                    package_path = java_file.relative_to(source_dir).parent
                    package_name = str(package_path).replace("/", ".").replace("\\", ".")
                    
                    prompt = f"""
为以下Java类生成JUnit 5测试：

包名：{package_name}
类名：{class_name}

源代码：
{source_content}

要求：
1. 生成完整的JUnit 5测试类
2. 测试所有公共方法
3. 包含正常和异常情况
4. 使用org.junit.jupiter.api
5. 只返回Java代码，不要包含markdown标记
"""
                    
                    test_code = await self._call_llm_for_java_test(prompt)
                    
                    if test_code:
                        # 确定测试文件路径（保持包结构）
                        test_package_dir = test_dir / package_path
                        test_package_dir.mkdir(parents=True, exist_ok=True)
                        test_file_path = test_package_dir / f"{class_name}Test.java"
                        test_file_path.write_text(test_code, encoding="utf-8")
                        generated_files.append(str(test_file_path))
                
                except Exception as e:
                    logger.warning(f"为 {java_file} 生成测试失败: {e}")
                    continue
            
            return {
                "success": len(generated_files) > 0,
                "test_files": generated_files
            }
        
        except Exception as e:
            return {"success": False, "error": str(e), "test_files": []}
    
    def _ensure_junit_dependency(self, project_path: str):
        """确保pom.xml或build.gradle中有JUnit依赖"""
        project = Path(project_path)
        
        # 检查pom.xml
        pom_path = project / "pom.xml"
        if pom_path.exists():
            try:
                with open(pom_path, 'r', encoding='utf-8') as f:
                    pom_content = f.read()
                
                # 简单检查是否有JUnit依赖
                if "junit-jupiter" not in pom_content and "junit" not in pom_content.lower():
                    logger.warning("pom.xml中可能缺少JUnit依赖，请手动添加")
            except Exception:
                pass
        
        # 检查build.gradle
        gradle_path = project / "build.gradle"
        if gradle_path.exists():
            try:
                with open(gradle_path, 'r', encoding='utf-8') as f:
                    gradle_content = f.read()
                
                # 简单检查是否有JUnit依赖
                if "junit-jupiter" not in gradle_content and "junit" not in gradle_content.lower():
                    logger.warning("build.gradle中可能缺少JUnit依赖，请手动添加")
            except Exception:
                pass

