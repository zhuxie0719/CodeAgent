"""
模拟AI测试生成器 - 用于演示功能（不需要真实API密钥）
"""
import os
import json
import asyncio
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MockAITestGenerator:
    """模拟AI测试生成器 - 生成示例测试文件"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepseek.com/v1"):
        """
        初始化模拟AI测试生成器
        
        Args:
            api_key: API密钥（模拟模式下忽略）
            base_url: API基础URL（模拟模式下忽略）
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = "deepseek-coder"
        logger.info("使用模拟AI测试生成器（不需要真实API密钥）")
    
    async def generate_test_file(self, source_file_path: str, project_path: str) -> Dict[str, Any]:
        """
        为源代码文件生成测试文件（模拟版本）
        
        Args:
            source_file_path: 源代码文件路径
            project_path: 项目根路径
            
        Returns:
            包含生成结果的字典
        """
        try:
            # 读取源代码文件
            source_content = self._read_file(source_file_path)
            if not source_content:
                return {
                    "success": False,
                    "error": f"无法读取源代码文件: {source_file_path}",
                    "test_file_path": None
                }
            
            # 生成模拟测试文件内容
            test_content = self._generate_mock_test_content(source_content, source_file_path)
            
            # 确定测试文件路径
            test_file_path = self._get_test_file_path(source_file_path, project_path)
            
            # 写入测试文件
            self._write_file(test_file_path, test_content)
            
            return {
                "success": True,
                "test_file_path": test_file_path,
                "test_content": test_content,
                "source_file": source_file_path
            }
            
        except Exception as e:
            logger.error(f"生成测试文件时发生错误: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_file_path": None
            }
    
    def _read_file(self, file_path: str) -> Optional[str]:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            return None
    
    def _write_file(self, file_path: str, content: str) -> bool:
        """写入文件内容"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"写入文件失败 {file_path}: {e}")
            return False
    
    def _get_test_file_path(self, source_file_path: str, project_path: str) -> str:
        """根据源代码文件路径生成测试文件路径"""
        # 获取相对于项目路径的文件名
        rel_path = os.path.relpath(source_file_path, project_path)
        
        # 如果是Python文件，生成对应的测试文件名
        if rel_path.endswith('.py'):
            # 移除.py扩展名，生成不同的测试文件名
            base_name = os.path.basename(rel_path)[:-3]  # 移除.py
            
            # 生成不同的测试文件名：添加ai_generated前缀和_tests后缀
            if base_name.startswith('test_'):
                # 如果原文件已经是测试文件，生成ai_test_前缀
                test_name = f"ai_test_{base_name[5:]}.py"  # 移除test_前缀
            else:
                # 普通文件，生成ai_generated_前缀
                test_name = f"ai_generated_{base_name}_tests.py"
            
            # 构建测试文件路径
            test_dir = os.path.join(project_path, "tests")
            return os.path.join(test_dir, test_name)
        
        # 非Python文件，生成通用测试文件名
        base_name = os.path.basename(rel_path)
        test_name = f"ai_generated_{base_name}_tests.py"
        test_dir = os.path.join(project_path, "tests")
        return os.path.join(test_dir, test_name)
    
    def _generate_mock_test_content(self, source_content: str, source_file_path: str) -> str:
        """生成模拟的测试文件内容"""
        filename = os.path.basename(source_file_path)
        
        # 分析源代码，提取函数名
        functions = self._extract_functions(source_content)
        
        test_content = f'''"""
AI自动生成的测试文件 - 为 {filename} 生成
这是由AI测试生成器自动创建的单元测试文件
测试目标: {filename}
生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import unittest
import sys
import os

# 添加源代码路径到sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.join(os.path.dirname(current_dir), "tests")
sys.path.insert(0, source_dir)

try:
    # 尝试导入被测试的模块
    import {filename[:-3]} as source_module
except ImportError as e:
    print(f"警告: 无法导入模块 {{filename[:-3]}}: {{e}}")
    source_module = None


class AIGeneratedTest{filename[:-3].title()}(unittest.TestCase):
    """AI生成的测试类 - 测试 {filename} 中的函数"""
    
    def setUp(self):
        """测试前的设置"""
        if source_module is None:
            self.skipTest("无法导入源代码模块")
    
    def tearDown(self):
        """测试后的清理"""
        pass
'''
        
        # 为每个函数生成测试方法
        for func_name in functions:
            test_content += f'''
    def test_{func_name}(self):
        """测试函数 {func_name}"""
        if source_module is None:
            self.skipTest("无法导入源代码模块")
        
        # 测试正常情况
        try:
            # 这里需要根据实际函数签名调整参数
            # result = source_module.{func_name}(...)
            # self.assertIsNotNone(result)
            pass
        except Exception as e:
            self.fail(f"函数 {func_name} 执行失败: {{e}}")
        
        # 测试边界情况
        try:
            # 测试边界值
            pass
        except Exception as e:
            # 某些边界情况可能预期会抛出异常
            pass
        
        # 测试异常情况
        try:
            # 测试无效输入
            pass
        except Exception as e:
            # 预期会抛出异常
            pass
'''
        
        test_content += '''
    def test_module_import(self):
        """测试模块导入"""
        self.assertIsNotNone(source_module, "模块导入失败")
    
    def test_module_has_functions(self):
        """测试模块包含预期的函数"""
        if source_module is None:
            self.skipTest("无法导入源代码模块")
        
        # 检查模块是否包含预期的函数
        expected_functions = ['''
        
        for func_name in functions:
            test_content += f'            "{func_name}",\n'
        
        test_content += '''        ]
        
        for func_name in expected_functions:
            self.assertTrue(
                hasattr(source_module, func_name),
                f"模块缺少函数 {{func_name}}"
            )


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
'''
        
        return test_content
    
    def _extract_functions(self, source_content: str) -> list:
        """从源代码中提取函数名"""
        functions = []
        lines = source_content.split('\n')
        
        for line in lines:
            line = line.strip()
            # 匹配函数定义
            if line.startswith('def ') and '(' in line:
                func_name = line.split('def ')[1].split('(')[0].strip()
                if not func_name.startswith('_'):  # 跳过私有函数
                    functions.append(func_name)
        
        return functions

    async def cleanup_test_file(self, test_file_path: str) -> bool:
        """清理生成的测试文件"""
        try:
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
                logger.info(f"已清理测试文件: {test_file_path}")
                return True
        except Exception as e:
            logger.error(f"清理测试文件失败 {test_file_path}: {e}")
        return False
