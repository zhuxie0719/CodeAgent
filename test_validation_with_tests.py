#!/usr/bin/env python3
"""
使用tests目录中的测试文件进行验证Agent测试
"""

import asyncio
import sys
import os
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from agents.test_validation_agent.agent import TestValidationAgent
from config.settings import settings

async def test_with_actual_tests():
    """使用实际的测试文件进行测试"""
    print("🚀 开始使用实际测试文件进行验证...")
    
    # 创建Agent实例
    config = settings.AGENTS.get('test_validation_agent', {})
    agent = TestValidationAgent(config)
    await agent.start()
    
    # 创建一个临时测试目录
    test_dir = Path("temp_test_project")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    # 复制测试文件到临时目录
    tests_dir = Path("tests")
    for test_file in tests_dir.glob("test_*.py"):
        shutil.copy2(test_file, test_dir)
        print(f"📋 复制测试文件: {test_file.name}")
    
    # 创建一个简单的测试文件
    simple_test = test_dir / "test_simple.py"
    simple_test.write_text('''
import unittest

class TestSimple(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(1 + 1, 2)
    
    def test_string(self):
        self.assertEqual("hello", "hello")
    
    def test_fail(self):
        # 故意失败的测试
        self.assertEqual(1, 2, "This should fail")

if __name__ == '__main__':
    unittest.main()
''')
    
    print(f"📁 临时测试目录: {test_dir.absolute()}")
    
    # 测试1: 单元测试（应该部分通过）
    print("\n🧪 测试1: 单元测试")
    try:
        task_data = {
            "action": "unit",
            "project_path": str(test_dir.absolute()),
            "options": {
                "generate_with_ai": False,
                "min_coverage": 10
            }
        }
        
        result = await agent.process_task("test_unit_002", task_data)
        print(f"✅ 单元测试结果:")
        print(f"   - 通过: {result['results']['passed']}")
        print(f"   - 返回码: {result['results']['returncode']}")
        print(f"   - 覆盖率: {result['coverage']}%")
        if result['results']['stdout']:
            print(f"   - 输出: {result['results']['stdout'][:200]}...")
        if result['results']['stderr']:
            print(f"   - 错误: {result['results']['stderr'][:200]}...")
        
    except Exception as e:
        print(f"❌ 单元测试失败: {e}")
    
    # 测试2: 完整验证
    print("\n🎯 测试2: 完整验证")
    try:
        task_data = {
            "action": "validate",
            "project_path": str(test_dir.absolute()),
            "options": {
                "generate_with_ai": True,
                "min_coverage": 5  # 降低要求
            },
            "fix_result": {
                "summary": "修复了测试用例",
                "files_changed": ["test_simple.py"]
            }
        }
        
        result = await agent.process_task("test_validate_002", task_data)
        print(f"✅ 完整验证结果:")
        print(f"   - 整体通过: {result['passed']}")
        print(f"   - 单元测试通过: {result['test_results']['unit']['passed']}")
        print(f"   - 集成测试通过: {result['test_results']['integration']['passed']}")
        print(f"   - 性能测试通过: {result['performance_metrics']['passed']}")
        print(f"   - 覆盖率: {result['coverage']}%")
        
    except Exception as e:
        print(f"❌ 完整验证失败: {e}")
    
    # 检查AI生成的文件
    ai_tests_dir = test_dir / "ai_tests"
    if ai_tests_dir.exists():
        print(f"\n📝 AI测试文件:")
        for file in ai_tests_dir.glob("*"):
            print(f"   - {file.name}")
            if file.suffix == '.json':
                content = file.read_text(encoding='utf-8')
                print(f"     内容: {content[:100]}...")
    
    # 清理临时目录
    shutil.rmtree(test_dir)
    print(f"\n🧹 清理临时目录: {test_dir}")
    
    await agent.stop()
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    asyncio.run(test_with_actual_tests())

