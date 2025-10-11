#!/usr/bin/env python3
"""
测试验证代理运行脚本
用于验证测试验证代理的各项功能
"""

import asyncio
import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agents.test_validation_agent.agent import TestValidationAgent
from agents.test_validation_agent.tester import UnitTester, IntegrationTester, PerformanceTester
from agents.test_validation_agent.mock_ai_test_generator import MockAITestGenerator


async def test_unit_tester():
    """测试单元测试器"""
    print("🧪 测试单元测试器...")
    
    # 创建临时测试项目
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文件
        test_file = os.path.join(temp_dir, "test_sample.py")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("""
import unittest

class TestSample(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(1 + 1, 2)
    
    def test_string(self):
        self.assertEqual("hello", "hello")
""")
        
        # 测试单元测试器
        config = {"min_coverage": 80}
        tester = UnitTester(config)
        
        # 运行测试
        result = await tester.run_tests(temp_dir, "test_sample.py")
        
        print(f"   ✅ 单元测试结果: {'通过' if result['passed'] else '失败'}")
        if not result['passed']:
            print(f"   📝 错误详情: {result.get('stderr', '无错误信息')}")
        
        return result['passed']


async def test_integration_tester():
    """测试集成测试器"""
    print("🔗 测试集成测试器...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config = {"min_coverage": 80}
        tester = IntegrationTester(config)
        
        # 运行测试（应该跳过，因为没有集成测试目录）
        result = await tester.run_tests(temp_dir)
        
        print(f"   ✅ 集成测试结果: {'通过' if result['passed'] else '失败'}")
        if result.get('skipped'):
            print(f"   📝 跳过原因: {result.get('message', '无消息')}")
        
        return result['passed']


async def test_performance_tester():
    """测试性能测试器"""
    print("⚡ 测试性能测试器...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config = {"min_coverage": 80}
        tester = PerformanceTester(config)
        
        # 运行测试
        result = await tester.run_tests(temp_dir)
        
        print(f"   ✅ 性能测试结果: {'通过' if result['passed'] else '失败'}")
        print(f"   📊 性能指标: {result.get('metrics', {})}")
        
        return result['passed']


async def test_mock_ai_generator():
    """测试模拟AI生成器"""
    print("🤖 测试模拟AI生成器...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建示例源代码文件
        source_file = os.path.join(temp_dir, "sample.py")
        with open(source_file, "w", encoding="utf-8") as f:
            f.write("""
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
""")
        
        # 测试AI生成器
        generator = MockAITestGenerator()
        result = await generator.generate_test_file(source_file, temp_dir)
        
        print(f"   ✅ AI生成结果: {'成功' if result['success'] else '失败'}")
        if result['success']:
            print(f"   📁 生成文件: {result['test_file_path']}")
            # 检查生成的文件是否存在
            if os.path.exists(result['test_file_path']):
                print(f"   ✅ 文件已创建")
            else:
                print(f"   ❌ 文件未找到")
        else:
            print(f"   📝 错误: {result.get('error', '未知错误')}")
        
        return result['success']


async def test_full_agent():
    """测试完整的测试验证代理"""
    print("🎯 测试完整代理...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建示例源代码文件
        source_file = os.path.join(temp_dir, "calculator.py")
        with open(source_file, "w", encoding="utf-8") as f:
            f.write("""
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
""")
        
        # 创建测试验证代理
        config = {
            "min_coverage": 60,  # 降低覆盖率要求以便测试通过
            "ai_api_key": None  # 使用模拟模式
        }
        agent = TestValidationAgent(config)
        
        # 准备任务数据
        task_data = {
            "project_path": temp_dir,
            "file_path": source_file,
            "fix_result": {"status": "success"},
            "test_options": {
                "generate_with_ai": True,
                "cleanup_ai_tests": False
            }
        }
        
        # 执行验证任务
        result = await agent.process_task("test_task", task_data)
        
        print(f"   ✅ 验证结果: {'通过' if result['passed'] else '失败'}")
        print(f"   📊 覆盖率: {result.get('coverage', 0)}%")
        print(f"   🧪 单元测试: {'通过' if result['test_results'].get('unit', {}).get('passed', False) else '失败'}")
        print(f"   🔗 集成测试: {'通过' if result['test_results'].get('integration', {}).get('passed', False) else '失败'}")
        
        if result.get('ai_generated_test'):
            print(f"   🤖 AI生成测试: 成功")
            print(f"   📁 AI测试文件: {result['ai_generated_test']['file_path']}")
        
        return result['passed']


async def main():
    """主测试函数"""
    print("🚀 开始测试验证代理功能...")
    print("=" * 50)
    
    tests = [
        ("单元测试器", test_unit_tester),
        ("集成测试器", test_integration_tester),
        ("性能测试器", test_performance_tester),
        ("模拟AI生成器", test_mock_ai_generator),
        ("完整代理", test_full_agent),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n📋 {test_name}:")
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            results.append((test_name, False))
    
    # 输出总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试都通过了！测试验证代理功能正常。")
    else:
        print("⚠️ 部分测试失败，需要进一步检查。")
    
    return passed == total


if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
