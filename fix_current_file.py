#!/usr/bin/env python3
"""
修复当前文件的简单脚本
"""

import asyncio
import os
import sys
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from agents.fix_execution_agent.agent import FixExecutionAgent


async def fix_current_file():
    """修复当前文件"""
    # 您当前打开的文件路径
    file_path = r"c:\Users\Ding\AppData\Local\Temp\tmpahknkt2i.py"
    
    print(f"🔧 开始修复文件: {file_path}")
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    # 创建备份
    backup_path = f"{file_path}.backup"
    shutil.copy2(file_path, backup_path)
    print(f"✅ 已创建备份: {backup_path}")
    
    # 显示修复前的内容
    print("\n🔴 修复前的内容:")
    with open(file_path, 'r', encoding='utf-8') as f:
        before_content = f.read()
    print(before_content)
    
    # 创建Agent
    agent = FixExecutionAgent({"enabled": True})
    
    # 定义要修复的问题
    issues = [
        {
            "language": "python",
            "file": "tmpahknkt2i.py",
            "type": "format",
            "message": "unused import",
            "line": 4
        },
        {
            "language": "python",
            "file": "tmpahknkt2i.py",
            "type": "format",
            "message": "line too long",
            "line": 8
        },
        {
            "language": "python",
            "file": "tmpahknkt2i.py",
            "type": "format",
            "message": "line too long",
            "line": 13
        },
        {
            "language": "python",
            "file": "tmpahknkt2i.py",
            "type": "format",
            "message": "indentation",
            "line": 17
        },
        {
            "language": "python",
            "file": "tmpahknkt2i.py",
            "type": "format",
            "message": "trailing whitespace",
            "line": 21
        },
        {
            "language": "python",
            "file": "tmpahknkt2i.py",
            "type": "format",
            "message": "missing final newline",
            "line": 24
        }
    ]
    
    print(f"\n🚀 开始修复 {len(issues)} 个问题...")
    
    try:
        # 执行修复
        result = await agent.process_issues(issues, os.path.dirname(file_path))
        
        # 显示修复结果
        print(f"\n📊 修复结果:")
        print(f"   总问题数: {result['total_issues']}")
        print(f"   修复成功: {result['fixed_issues']}")
        print(f"   修复失败: {result['failed_issues']}")
        print(f"   跳过问题: {result['skipped_issues']}")
        print(f"   成功率: {result['success_rate']:.1%}")
        
        if result.get('changes'):
            print(f"\n✅ 修复内容:")
            for change in result['changes']:
                print(f"   - {change}")
        
        if result.get('errors'):
            print(f"\n❌ 错误信息:")
            for error in result['errors']:
                print(f"   - {error}")
        
        # 显示修复后的内容
        print("\n🟢 修复后的内容:")
        with open(file_path, 'r', encoding='utf-8') as f:
            after_content = f.read()
        print(after_content)
        
        # 验证修复效果
        print("\n🔍 修复验证:")
        checks = {
            "unused_imports_removed": "unused_module" not in after_content,
            "file_ends_with_newline": after_content.endswith('\n'),
            "no_trailing_whitespace": not any(line.endswith(' ') for line in after_content.split('\n')),
            "no_long_lines": all(len(line) <= 88 for line in after_content.split('\n'))
        }
        
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check}: {result}")
        
        print(f"\n✅ 文件修复完成!")
        print(f"📁 备份文件: {backup_path}")
        print(f"📁 修复文件: {file_path}")
        
    except Exception as e:
        print(f"\n❌ 修复失败: {e}")
        
        # 恢复备份
        response = input("是否恢复备份? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            shutil.copy2(backup_path, file_path)
            print("✅ 已恢复备份文件")


if __name__ == "__main__":
    asyncio.run(fix_current_file())


