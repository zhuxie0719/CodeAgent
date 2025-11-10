"""
C/C++测试生成器
使用LLM和Google Test模板生成C/C++测试文件
"""

import os
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import httpx

logger = logging.getLogger(__name__)


class CppTestGenerator:
    """C/C++测试生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.use_llm = config.get("use_llm", True)
        self.test_framework = config.get("test_framework", "google_test")  # google_test 或 catch2
        
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
        生成C/C++测试
        
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
                    project_path, issues, issue_description, tests_dir
                )
                if reproduction_test:
                    generated_tests.append(reproduction_test)
                    logger.info(f"✅ 生成重现测试: {reproduction_test}")
            except Exception as e:
                error_msg = f"生成重现测试失败: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # 2. 使用LLM生成覆盖性测试
        if self.use_llm and self.ai_analyzer:
            try:
                llm_result = await self._generate_with_llm(project_path, tests_dir, issues)
                if llm_result.get("success"):
                    generated_tests.extend(llm_result.get("test_files", []))
                    logger.info(f"✅ LLM生成 {len(llm_result.get('test_files', []))} 个测试文件")
            except Exception as e:
                error_msg = f"LLM生成失败: {e}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # 3. 生成或更新CMakeLists.txt
        try:
            self._ensure_cmake_config(project_path, tests_dir)
        except Exception as e:
            error_msg = f"更新CMake配置失败: {e}"
            logger.warning(error_msg)
            errors.append(error_msg)
        
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
        issue_description: str,
        tests_dir: Path
    ) -> Optional[str]:
        """生成重现问题的Google Test测试"""
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
        
        framework_template = self._get_test_framework_template()
        
        prompt = f"""
根据以下信息，生成一个能重现问题的{self.test_framework}测试：

{chr(10).join(prompt_parts)}

要求：
1. 生成{self.test_framework}格式的测试
2. 测试应该能够重现问题
3. 包含必要的断言
4. 测试文件应该命名为test_reproduction.cpp
5. 只返回C++代码，不要包含markdown标记
6. 包含必要的头文件

测试框架模板：
{framework_template}
"""
        
        # 调用LLM生成测试代码
        try:
            test_code = await self._call_llm_for_cpp_test(prompt)
            
            if test_code:
                test_file_path = tests_dir / "test_reproduction.cpp"
                test_file_path.write_text(test_code, encoding="utf-8")
                return str(test_file_path)
        
        except Exception as e:
            logger.error(f"生成重现测试时出错: {e}")
        
        return None
    
    def _get_test_framework_template(self) -> str:
        """获取测试框架模板"""
        if self.test_framework == "google_test":
            return """
// Google Test示例
#include <gtest/gtest.h>
#include "../src/your_header.h"

TEST(YourTestSuite, TestName) {
    // 测试代码
    EXPECT_EQ(expected, actual);
}
"""
        else:  # catch2
            return """
// Catch2示例
#define CATCH_CONFIG_MAIN
#include "catch2/catch.hpp"
#include "../src/your_header.h"

TEST_CASE("Test description", "[tag]") {
    REQUIRE(condition);
}
"""
    
    async def _call_llm_for_cpp_test(self, prompt: str) -> Optional[str]:
        """调用LLM生成C/C++测试代码"""
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
                        "content": f"你是一个专业的C/C++测试工程师，擅长编写高质量的{self.test_framework}测试。请根据提供的信息生成完整的测试文件。"
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
            logger.error(f"调用LLM生成C/C++测试失败: {e}")
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
    
    async def _generate_with_llm(
        self, 
        project_path: str, 
        tests_dir: Path,
        issues: List[Dict] = None
    ) -> Dict[str, Any]:
        """使用LLM生成覆盖性测试"""
        if not self.ai_analyzer:
            return {"success": False, "error": "AI分析器不可用", "test_files": []}
        
        try:
            # 查找主要的C/C++源文件
            project = Path(project_path)
            cpp_files = list(project.rglob("*.cpp")) + list(project.rglob("*.c"))
            cpp_files = [
                f for f in cpp_files 
                if "test" not in str(f).lower()
                and "main" not in str(f).lower()
            ][:3]  # 最多为3个文件生成测试
            
            generated_files = []
            
            for cpp_file in cpp_files:
                try:
                    # 读取源文件
                    with open(cpp_file, 'r', encoding='utf-8') as f:
                        source_content = f.read(2000)  # 限制长度
                    
                    # 构建提示词
                    file_name = cpp_file.stem
                    framework_template = self._get_test_framework_template()
                    
                    prompt = f"""
为以下C/C++文件生成{self.test_framework}测试：

文件名：{file_name}

源代码：
{source_content}

要求：
1. 生成完整的{self.test_framework}测试文件
2. 测试所有公共函数
3. 包含正常和异常情况
4. 只返回C++代码，不要包含markdown标记
5. 包含必要的头文件

测试框架模板：
{framework_template}
"""
                    
                    test_code = await self._call_llm_for_cpp_test(prompt)
                    
                    if test_code:
                        test_file_path = tests_dir / f"test_{file_name}.cpp"
                        test_file_path.write_text(test_code, encoding="utf-8")
                        generated_files.append(str(test_file_path))
                
                except Exception as e:
                    logger.warning(f"为 {cpp_file} 生成测试失败: {e}")
                    continue
            
            return {
                "success": len(generated_files) > 0,
                "test_files": generated_files
            }
        
        except Exception as e:
            return {"success": False, "error": str(e), "test_files": []}
    
    def _ensure_cmake_config(self, project_path: str, tests_dir: Path):
        """确保CMakeLists.txt中有Google Test配置"""
        project = Path(project_path)
        cmake_path = project / "CMakeLists.txt"
        
        # 如果CMakeLists.txt不存在，创建一个简单的
        if not cmake_path.exists():
            cmake_content = """cmake_minimum_required(VERSION 3.14)
project(YourProject)

# 添加Google Test
include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/03597a01ee50ed33e9fd7189c2e0e3b1e3c0e1c6.zip
)
FetchContent_MakeAvailable(googletest)

# 添加测试可执行文件
enable_testing()

add_executable(test_reproduction tests/test_reproduction.cpp)
target_link_libraries(test_reproduction GTest::gtest GTest::gtest_main GTest::gmock)

add_test(NAME ReproductionTest COMMAND test_reproduction)
"""
            cmake_path.write_text(cmake_content, encoding="utf-8")
            logger.info(f"✅ 创建CMakeLists.txt: {cmake_path}")
        else:
            # 检查是否已有Google Test配置
            with open(cmake_path, 'r', encoding='utf-8') as f:
                cmake_content = f.read()
            
            if "googletest" not in cmake_content.lower() and "gtest" not in cmake_content.lower():
                logger.warning("CMakeLists.txt中可能缺少Google Test配置，请手动添加")

