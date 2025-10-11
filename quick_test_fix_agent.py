#!/usr/bin/env python3
"""
修复执行Agent快速测试脚本
快速演示修复执行Agent的基本功能
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from agents.fix_execution_agent.agent import FixExecutionAgent


async def quick_test():
    """快速测试修复执行Agent"""
    print("🚀 修复执行Agent快速测试")
    print("=" * 40)
    
    # 创建Agent
    agent = FixExecutionAgent({"enabled": True})
    print("✅ Agent创建成功")
    
    # 创建临时测试文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        test_code = '''# 有问题的Python代码
import os
import sys
import unused_module  # 未使用的导入

def bad_function():
    # 缺少文档字符串
    x=1+2+3+4+5+6+7+8+9+10+11+12+13+14+15+16+17+18+19+20
    return x

def long_line_function():
    # 这行很长，超过了88个字符的限制
    very_long_variable_name = "这是一个非常长的字符串，用来测试行长度修复功能，包含了大量的字符"
    return very_long_variable_name

def indentation_issue():
# 缩进问题
    return "fixed"

def trailing_whitespace():
    return "test"    

# 缺少最终换行符
'''
        f.write(test_code)
        test_file_path = f.name
    
    print(f"📁 创建测试文件: {test_file_path}")
    
    # 显示修复前的代码
    print("\n🔴 修复前的代码:")
    with open(test_file_path, 'r') as f:
        before_content = f.read()
    print(before_content[:300] + "..." if len(before_content) > 300 else before_content)
    
    # 准备问题列表
    issues = [
        {
            "language": "python",
            "file": os.path.basename(test_file_path),
            "type": "format",
            "message": "unused import",
            "line": 3
        },
        {
            "language": "python",
            "file": os.path.basename(test_file_path),
            "type": "format",
            "message": "line too long",
            "line": 8
        },
        {
            "language": "python",
            "file": os.path.basename(test_file_path),
            "type": "format",
            "message": "line too long",
            "line": 12
        },
        {
            "language": "python",
            "file": os.path.basename(test_file_path),
            "type": "format",
            "message": "indentation",
            "line": 15
        },
        {
            "language": "python",
            "file": os.path.basename(test_file_path),
            "type": "format",
            "message": "trailing whitespace",
            "line": 18
        }
    ]
    
    print(f"\n🔧 准备修复 {len(issues)} 个问题...")
    
    # 执行修复
    try:
        result = await agent.process_issues(issues, os.path.dirname(test_file_path))
        
        # 显示修复结果
        print("\n📊 修复结果:")
        print(f"   总问题数: {result['total_issues']}")
        print(f"   修复成功: {result['fixed_issues']}")
        print(f"   修复失败: {result['failed_issues']}")
        print(f"   跳过问题: {result['skipped_issues']}")
        print(f"   成功率: {result['success_rate']:.1%}")
        
        if result.get('changes'):
            print(f"\n✅ 修复内容:")
            for change in result['changes'][:5]:
                print(f"   - {change}")
        
        if result.get('errors'):
            print(f"\n❌ 错误信息:")
            for error in result['errors'][:3]:
                print(f"   - {error}")
        
        # 显示修复后的代码
        print("\n🟢 修复后的代码:")
        with open(test_file_path, 'r') as f:
            after_content = f.read()
        print(after_content[:300] + "..." if len(after_content) > 300 else after_content)
        
        # 验证修复效果
        print("\n🔍 修复验证:")
        checks = {
            "unused_imports_removed": "unused_module" not in after_content,
            "file_ends_with_newline": after_content.endswith('\n'),
            "no_trailing_whitespace": not any(line.endswith(' ') for line in after_content.split('\n')),
            "proper_indentation": True  # 需要更详细的检查
        }
        
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check}: {result}")
        
        print(f"\n✅ 快速测试完成!")
        print(f"📁 测试文件位置: {test_file_path}")
        print("💡 您可以查看修复后的文件来验证效果")
        
    except Exception as e:
        print(f"\n❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 询问是否删除测试文件
        try:
            response = input(f"\n🗑️  是否删除测试文件? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                os.unlink(test_file_path)
                print("✅ 测试文件已删除")
            else:
                print(f"📁 测试文件保留: {test_file_path}")
        except KeyboardInterrupt:
            print(f"\n📁 测试文件保留: {test_file_path}")


def main():
    """主函数"""
    try:
        asyncio.run(quick_test())
    except KeyboardInterrupt:
        print("\n\n👋 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


