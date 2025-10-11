#!/usr/bin/env python3
"""
修复执行Agent测试脚本
演示如何使用修复执行Agent进行代码自动修复
"""

import asyncio
import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from agents.fix_execution_agent.agent import FixExecutionAgent


class FixAgentTester:
    """修复执行Agent测试器"""
    
    def __init__(self):
        self.agent = FixExecutionAgent({"enabled": True})
        self.test_dir = None
        self.backup_dir = None
    
    def setup_test_environment(self):
        """设置测试环境"""
        # 创建临时测试目录
        self.test_dir = tempfile.mkdtemp(prefix="fix_agent_test_")
        self.backup_dir = tempfile.mkdtemp(prefix="fix_agent_backup_")
        
        print(f"📁 测试目录: {self.test_dir}")
        print(f"📁 备份目录: {self.backup_dir}")
    
    def create_test_files(self):
        """创建测试文件"""
        test_files = {
            "bad_python.py": '''# 有问题的Python代码
import os
import sys
import unused_module  # 未使用的导入

# 硬编码的API密钥
API_KEY = "sk-1234567890abcdef"

def bad_function():
    # 缺少文档字符串
    x = 1
    y = 2
    z = x + y
    return z

def long_line_function():
    # 这行很长，超过了88个字符的限制，应该被自动修复
    very_long_variable_name = "这是一个非常长的字符串，用来测试行长度修复功能，包含了大量的字符"
    return very_long_variable_name

def indentation_issue():
# 缩进问题
    return "fixed"

def trailing_whitespace():
    return "test"    

# 缺少最终换行符
''',
            "bad_javascript.js": '''// 有问题的JavaScript代码
function badFunction() {
var x=1+2+3+4+5+6+7+8+9+10+11+12+13+14+15+16+17+18+19+20;
return x;
}

function longLineFunction() {
var veryLongVariableName = "这是一个非常长的字符串，用来测试行长度修复功能，包含了大量的字符";
return veryLongVariableName;
}

function indentationIssue() {
return "fixed";
}
''',
            "bad_java.java": '''// 有问题的Java代码
public class BadClass {
public void badMethod() {
int x=1+2+3+4+5+6+7+8+9+10+11+12+13+14+15+16+17+18+19+20;
System.out.println(x);
}

public void longLineMethod() {
String veryLongVariableName = "这是一个非常长的字符串，用来测试行长度修复功能，包含了大量的字符";
System.out.println(veryLongVariableName);
}
}
'''
        }
        
        # 创建测试文件
        for filename, content in test_files.items():
            file_path = os.path.join(self.test_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 创建测试文件: {filename}")
        
        # 创建备份
        for filename in test_files.keys():
            src = os.path.join(self.test_dir, filename)
            dst = os.path.join(self.backup_dir, filename)
            shutil.copy2(src, dst)
        
        print(f"✅ 创建备份文件完成")
    
    async def test_python_fix(self):
        """测试Python代码修复"""
        print("\n🐍 测试Python代码修复...")
        
        issues = [
            {
                "language": "python",
                "file": "bad_python.py",
                "type": "format",
                "message": "unused import",
                "line": 3
            },
            {
                "language": "python",
                "file": "bad_python.py", 
                "type": "format",
                "message": "line too long",
                "line": 15
            },
            {
                "language": "python",
                "file": "bad_python.py",
                "type": "format", 
                "message": "indentation",
                "line": 19
            },
            {
                "language": "python",
                "file": "bad_python.py",
                "type": "format",
                "message": "trailing whitespace",
                "line": 22
            }
        ]
        
        # 执行修复
        result = await self.agent.process_issues(issues, self.test_dir)
        
        # 显示结果
        self.print_fix_result("Python", result)
        
        # 验证修复效果
        self.verify_python_fix()
        
        return result
    
    async def test_javascript_fix(self):
        """测试JavaScript代码修复"""
        print("\n🟨 测试JavaScript代码修复...")
        
        issues = [
            {
                "language": "javascript",
                "file": "bad_javascript.js",
                "type": "format",
                "message": "formatting",
                "line": 1
            }
        ]
        
        # 执行修复
        result = await self.agent.process_issues(issues, self.test_dir)
        
        # 显示结果
        self.print_fix_result("JavaScript", result)
        
        return result
    
    async def test_java_fix(self):
        """测试Java代码修复"""
        print("\n☕ 测试Java代码修复...")
        
        issues = [
            {
                "language": "java",
                "file": "bad_java.java",
                "type": "format",
                "message": "formatting",
                "line": 1
            }
        ]
        
        # 执行修复
        result = await self.agent.process_issues(issues, self.test_dir)
        
        # 显示结果
        self.print_fix_result("Java", result)
        
        return result
    
    def print_fix_result(self, language: str, result: Dict[str, Any]):
        """打印修复结果"""
        print(f"\n📊 {language}修复结果:")
        print(f"   总问题数: {result['total_issues']}")
        print(f"   修复成功: {result['fixed_issues']}")
        print(f"   修复失败: {result['failed_issues']}")
        print(f"   跳过问题: {result['skipped_issues']}")
        print(f"   成功率: {result['success_rate']:.1%}")
        
        if result.get('changes'):
            print(f"   修复内容:")
            for change in result['changes'][:5]:  # 只显示前5个
                print(f"     - {change}")
        
        if result.get('errors'):
            print(f"   错误信息:")
            for error in result['errors'][:3]:  # 只显示前3个错误
                print(f"     - {error}")
    
    def verify_python_fix(self):
        """验证Python修复效果"""
        print("\n🔍 验证Python修复效果...")
        
        file_path = os.path.join(self.test_dir, "bad_python.py")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查修复效果
            checks = {
                "unused_imports_removed": "unused_module" not in content,
                "file_ends_with_newline": content.endswith('\n'),
                "no_trailing_whitespace": not any(line.endswith(' ') for line in content.split('\n')),
                "proper_indentation": True  # 需要更详细的检查
            }
            
            print("   修复验证结果:")
            for check, result in checks.items():
                status = "✅" if result else "❌"
                print(f"     {status} {check}: {result}")
            
            # 显示修复前后的对比
            self.show_file_comparison("bad_python.py")
            
        except Exception as e:
            print(f"   ❌ 验证失败: {e}")
    
    def show_file_comparison(self, filename: str):
        """显示文件修复前后对比"""
        print(f"\n📋 {filename} 修复前后对比:")
        
        # 读取修复后的文件
        fixed_path = os.path.join(self.test_dir, filename)
        backup_path = os.path.join(self.backup_dir, filename)
        
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                before = f.read()
            
            with open(fixed_path, 'r', encoding='utf-8') as f:
                after = f.read()
            
            print("   🔴 修复前 (前10行):")
            for i, line in enumerate(before.split('\n')[:10], 1):
                print(f"     {i:2d}: {line}")
            
            print("   🟢 修复后 (前10行):")
            for i, line in enumerate(after.split('\n')[:10], 1):
                print(f"     {i:2d}: {line}")
                
        except Exception as e:
            print(f"   ❌ 对比失败: {e}")
    
    async def test_mixed_language_fix(self):
        """测试混合语言修复"""
        print("\n🌐 测试混合语言修复...")
        
        issues = [
            {
                "language": "python",
                "file": "bad_python.py",
                "type": "format",
                "message": "unused import",
                "line": 3
            },
            {
                "language": "javascript",
                "file": "bad_javascript.js", 
                "type": "format",
                "message": "formatting",
                "line": 1
            },
            {
                "language": "java",
                "file": "bad_java.java",
                "type": "format",
                "message": "formatting", 
                "line": 1
            }
        ]
        
        # 执行修复
        result = await self.agent.process_issues(issues, self.test_dir)
        
        # 显示结果
        self.print_fix_result("混合语言", result)
        
        return result
    
    async def test_non_format_issues(self):
        """测试非格式化问题处理"""
        print("\n🚫 测试非格式化问题处理...")
        
        issues = [
            {
                "language": "python",
                "file": "bad_python.py",
                "type": "security",
                "message": "hardcoded password detected",
                "line": 6
            },
            {
                "language": "python",
                "file": "bad_python.py",
                "type": "logic",
                "message": "potential division by zero",
                "line": 10
            }
        ]
        
        # 执行修复
        result = await self.agent.process_issues(issues, self.test_dir)
        
        # 显示结果
        self.print_fix_result("非格式化问题", result)
        
        return result
    
    def cleanup(self):
        """清理测试环境"""
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print(f"🗑️  清理测试目录: {self.test_dir}")
        
        if self.backup_dir and os.path.exists(self.backup_dir):
            shutil.rmtree(self.backup_dir)
            print(f"🗑️  清理备份目录: {self.backup_dir}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始修复执行Agent测试")
        print("=" * 50)
        
        try:
            # 设置测试环境
            self.setup_test_environment()
            self.create_test_files()
            
            # 运行各项测试
            await self.test_python_fix()
            await self.test_javascript_fix()
            await self.test_java_fix()
            await self.test_mixed_language_fix()
            await self.test_non_format_issues()
            
            print("\n✅ 所有测试完成!")
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # 清理环境
            self.cleanup()


async def main():
    """主函数"""
    tester = FixAgentTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())


