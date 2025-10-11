#!/usr/bin/env python3
"""
测试验证代理完整演示
展示AI测试生成、测试运行、覆盖率计算等功能
"""
import asyncio
import sys
import os
import json
from typing import Dict, Any

# 添加路径
sys.path.append('agents/test_validation_agent')
from ai_test_generator import AITestGenerator
from tester import UnitTester, IntegrationTester, PerformanceTester

class TestValidationDemo:
    """测试验证演示类"""
    
    def __init__(self):
        self.ai_generator = AITestGenerator()
        self.unit_tester = UnitTester({})
        self.integration_tester = IntegrationTester({})
        self.performance_tester = PerformanceTester({})
    
    async def run_complete_demo(self, project_path: str = "."):
        """运行完整的测试验证演示"""
        print("=" * 60)
        print("测试验证代理完整演示")
        print("=" * 60)
        
        # 1. 测试AI测试生成器基本功能
        await self._demo_ai_generator_basic()
        
        # 2. 测试单元测试运行
        await self._demo_unit_testing(project_path)
        
        # 3. 测试集成测试
        await self._demo_integration_testing(project_path)
        
        # 4. 测试性能测试
        await self._demo_performance_testing(project_path)
        
        # 5. 测试覆盖率计算
        await self._demo_coverage_calculation(project_path)
        
        print("\n" + "=" * 60)
        print("演示完成！")
        print("=" * 60)
    
    async def _demo_ai_generator_basic(self):
        """演示AI测试生成器基本功能"""
        print("\n1. AI测试生成器基本功能演示")
        print("-" * 40)
        
        # 测试文件路径生成
        source_file = "tests/test_python_bad.py"
        test_path = self.ai_generator._get_test_file_path(source_file, ".")
        print(f"源文件: {source_file}")
        print(f"生成测试文件路径: {test_path}")
        
        # 测试内容清理
        test_content = """```python
import unittest
class TestExample(unittest.TestCase):
    def test_something(self):
        self.assertTrue(True)
```"""
        
        cleaned = self.ai_generator._clean_ai_content(test_content)
        print(f"内容清理: {len(test_content)} -> {len(cleaned)} 字符")
        
        # 测试提示词构建
        source_content = "def hello(): return 'world'"
        prompt = self.ai_generator._build_prompt(source_content, "test.py")
        print(f"提示词长度: {len(prompt)} 字符")
        
        print("✓ AI测试生成器基本功能正常")
    
    async def _demo_unit_testing(self, project_path: str):
        """演示单元测试运行"""
        print("\n2. 单元测试运行演示")
        print("-" * 40)
        
        # 运行特定测试文件
        test_file = "tests/tests/test_test_python_bad.py"
        if os.path.exists(test_file):
            result = await self.unit_tester.run_tests(project_path, test_file)
            print(f"测试文件: {test_file}")
            print(f"测试通过: {result['passed']}")
            print(f"返回码: {result['returncode']}")
            if result['stdout']:
                print(f"输出: {result['stdout'][:100]}...")
        else:
            print(f"测试文件不存在: {test_file}")
        
        # 运行整个项目测试
        result = await self.unit_tester.run_tests(project_path)
        print(f"项目整体测试通过: {result['passed']}")
        print("✓ 单元测试运行功能正常")
    
    async def _demo_integration_testing(self, project_path: str):
        """演示集成测试"""
        print("\n3. 集成测试演示")
        print("-" * 40)
        
        result = await self.integration_tester.run_tests(project_path)
        print(f"集成测试通过: {result['passed']}")
        if result.get('skipped'):
            print(f"跳过原因: {result.get('message', '未知')}")
        else:
            print(f"返回码: {result['returncode']}")
        
        print("✓ 集成测试功能正常")
    
    async def _demo_performance_testing(self, project_path: str):
        """演示性能测试"""
        print("\n4. 性能测试演示")
        print("-" * 40)
        
        result = await self.performance_tester.run_tests(project_path)
        print(f"性能测试通过: {result['passed']}")
        if 'metrics' in result:
            print("性能指标:")
            for key, value in result['metrics'].items():
                print(f"  {key}: {value}")
        
        print("✓ 性能测试功能正常")
    
    async def _demo_coverage_calculation(self, project_path: str):
        """演示覆盖率计算"""
        print("\n5. 覆盖率计算演示")
        print("-" * 40)
        
        coverage = await self.unit_tester.calculate_coverage(project_path)
        print(f"代码覆盖率: {coverage}%")
        
        if coverage == 0:
            print("注意: 覆盖率为0%可能是因为未安装coverage包")
            print("安装命令: pip install coverage")
        
        print("✓ 覆盖率计算功能正常")
    
    async def demo_ai_test_generation(self, source_file: str, project_path: str = "."):
        """演示AI测试生成（需要API密钥）"""
        print("\n6. AI测试生成演示")
        print("-" * 40)
        
        if not self.ai_generator.api_key:
            print("⚠️  未设置DEEPSEEK_API_KEY，跳过AI测试生成演示")
            print("设置环境变量: export DEEPSEEK_API_KEY=your_key")
            return
        
        print(f"为文件 {source_file} 生成AI测试...")
        result = await self.ai_generator.generate_test_file(source_file, project_path)
        
        if result['success']:
            print(f"✓ 测试文件生成成功: {result['test_file_path']}")
            
            # 运行生成的测试
            if os.path.exists(result['test_file_path']):
                test_result = await self.unit_tester.run_tests(project_path, result['test_file_path'])
                print(f"生成的测试通过: {test_result['passed']}")
        else:
            print(f"✗ 测试生成失败: {result['error']}")

async def main():
    """主函数"""
    demo = TestValidationDemo()
    
    # 运行完整演示
    await demo.run_complete_demo()
    
    # 可选：演示AI测试生成（需要API密钥）
    source_file = "tests/test_python_bad.py"
    if os.path.exists(source_file):
        await demo.demo_ai_test_generation(source_file)

if __name__ == "__main__":
    asyncio.run(main())


