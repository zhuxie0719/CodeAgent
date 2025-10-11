#!/usr/bin/env python3
"""
测试修复后的工作流程
验证测试验证代理现在能正确测试修复后的文件
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.test_validation_agent.agent import TestValidationAgent

async def test_fixed_workflow():
    """测试修复后的工作流程"""
    print("🧪 测试修复后的工作流程")
    print("=" * 50)
    
    # 配置
    config = {
        "min_coverage": 70,
        "ai_api_key": None  # 使用Mock生成器
    }
    
    # 创建测试验证代理
    test_agent = TestValidationAgent(config=config)
    await test_agent.start()
    
    # 测试数据 - 使用修复后的文件
    test_data = {
        "project_path": str(PROJECT_ROOT),
        "file_path": str(PROJECT_ROOT / "tests" / "output" / "test_python_bad_after.py"),
        "fix_result": {
            "success": True,
            "fix_results": [{
                "file": "test_python_bad.py",
                "before": "test_python_bad_before.py", 
                "after": "test_python_bad_after.py",
                "issues_fixed": 10
            }]
        },
        "test_options": {
            "generate_with_ai": True,
            "min_coverage": 70
        }
    }
    
    print(f"📄 测试文件: {test_data['file_path']}")
    print(f"📁 项目路径: {test_data['project_path']}")
    
    # 检查文件是否存在
    if not os.path.exists(test_data['file_path']):
        print(f"❌ 修复后的文件不存在: {test_data['file_path']}")
        return False
    
    print("✅ 修复后的文件存在")
    
    # 执行测试验证
    try:
        print("\n🚀 开始执行测试验证...")
        result = await test_agent.process_task("test_task", test_data)
        
        print("\n📊 测试验证结果:")
        print(f"   通过: {result.get('passed', False)}")
        print(f"   状态: {result.get('validation_status', 'unknown')}")
        print(f"   覆盖率: {result.get('coverage', 0)}%")
        
        # 显示单元测试结果
        unit_results = result.get('test_results', {}).get('unit', {})
        print(f"   单元测试: {'通过' if unit_results.get('passed', False) else '失败'}")
        if unit_results.get('stdout'):
            print(f"   输出: {unit_results['stdout'][:200]}...")
        if unit_results.get('stderr'):
            print(f"   错误: {unit_results['stderr'][:200]}...")
        
        # 显示AI生成的测试文件
        if 'ai_generated_test_file' in result:
            print(f"   AI测试文件: {result['ai_generated_test_file']}")
        
        return result.get('passed', False)
        
    except Exception as e:
        print(f"❌ 测试验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await test_agent.stop()

async def test_original_vs_fixed():
    """对比测试原始文件和修复后的文件"""
    print("\n🔄 对比测试: 原始文件 vs 修复后的文件")
    print("=" * 50)
    
    config = {"min_coverage": 70, "ai_api_key": None}
    test_agent = TestValidationAgent(config=config)
    await test_agent.start()
    
    # 测试原始文件
    original_data = {
        "project_path": str(PROJECT_ROOT),
        "file_path": str(PROJECT_ROOT / "tests" / "test_python_bad.py"),
        "test_options": {"generate_with_ai": True, "min_coverage": 70}
    }
    
    # 测试修复后的文件
    fixed_data = {
        "project_path": str(PROJECT_ROOT),
        "file_path": str(PROJECT_ROOT / "tests" / "output" / "test_python_bad_after.py"),
        "test_options": {"generate_with_ai": True, "min_coverage": 70}
    }
    
    try:
        print("📄 测试原始文件...")
        original_result = await test_agent.process_task("original_test", original_data)
        print(f"   结果: {'通过' if original_result.get('passed', False) else '失败'}")
        
        print("\n📄 测试修复后的文件...")
        fixed_result = await test_agent.process_task("fixed_test", fixed_data)
        print(f"   结果: {'通过' if fixed_result.get('passed', False) else '失败'}")
        
        print(f"\n📊 对比结果:")
        print(f"   原始文件: {'✅ 通过' if original_result.get('passed', False) else '❌ 失败'}")
        print(f"   修复文件: {'✅ 通过' if fixed_result.get('passed', False) else '❌ 失败'}")
        
        return fixed_result.get('passed', False)
        
    except Exception as e:
        print(f"❌ 对比测试失败: {e}")
        return False
    
    finally:
        await test_agent.stop()

if __name__ == "__main__":
    async def main():
        print("🎯 测试修复后的工作流程")
        
        # 测试1: 修复后的工作流程
        success1 = await test_fixed_workflow()
        
        # 测试2: 对比测试
        success2 = await test_original_vs_fixed()
        
        print(f"\n🏁 测试总结:")
        print(f"   修复后工作流程: {'✅ 成功' if success1 else '❌ 失败'}")
        print(f"   对比测试: {'✅ 成功' if success2 else '❌ 失败'}")
        
        if success1 and success2:
            print("\n🎉 所有测试通过！修复后的工作流程正常工作。")
        else:
            print("\n⚠️ 部分测试失败，需要进一步调试。")
    
    asyncio.run(main())
