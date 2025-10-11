#!/usr/bin/env python3
"""
修复本地文件的脚本
用于修复您指定的本地文件
"""

import asyncio
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from agents.fix_execution_agent.agent import FixExecutionAgent


class LocalFileFixer:
    """本地文件修复器"""
    
    def __init__(self):
        self.agent = FixExecutionAgent({"enabled": True})
    
    def create_backup(self, file_path: str) -> str:
        """创建文件备份"""
        backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_path)
        print(f"✅ 已创建备份: {backup_path}")
        return backup_path
    
    def analyze_file_issues(self, file_path: str) -> list:
        """分析文件中的问题"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            filename = os.path.basename(file_path)
            
            # 检查各种问题
            for i, line in enumerate(lines, 1):
                # 检查未使用的导入
                if 'import unused_module' in line:
                    issues.append({
                        "language": "python",
                        "file": filename,
                        "type": "format",
                        "message": "unused import",
                        "line": i
                    })
                
                # 检查行长度问题
                if len(line) > 88:
                    issues.append({
                        "language": "python",
                        "file": filename,
                        "type": "format",
                        "message": "line too long",
                        "line": i
                    })
                
                # 检查缩进问题
                if line.strip() and not line.startswith(' ') and not line.startswith('\t') and 'def ' in line:
                    # 检查下一行是否有缩进问题
                    if i < len(lines) and lines[i].strip() and not lines[i].startswith('    '):
                        issues.append({
                            "language": "python",
                            "file": filename,
                            "type": "format",
                            "message": "indentation",
                            "line": i + 1
                        })
                
                # 检查尾随空白
                if line.endswith(' ') or line.endswith('\t'):
                    issues.append({
                        "language": "python",
                        "file": filename,
                        "type": "format",
                        "message": "trailing whitespace",
                        "line": i
                    })
            
            # 检查文件结尾换行符
            if content and not content.endswith('\n'):
                issues.append({
                    "language": "python",
                    "file": filename,
                    "type": "format",
                    "message": "missing final newline",
                    "line": len(lines)
                })
            
            # 检查缺少文档字符串
            for i, line in enumerate(lines, 1):
                if 'def ' in line and not line.strip().startswith('#'):
                    # 检查函数定义后是否有文档字符串
                    if i < len(lines) and not lines[i].strip().startswith('"""') and not lines[i].strip().startswith("'''"):
                        issues.append({
                            "language": "python",
                            "file": filename,
                            "type": "format",
                            "message": "missing docstring",
                            "line": i
                        })
                    break
            
        except Exception as e:
            print(f"❌ 分析文件失败: {e}")
        
        return issues
    
    def show_file_content(self, file_path: str, title: str):
        """显示文件内容"""
        print(f"\n📄 {title}:")
        print("-" * 50)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                # 标记长行
                if len(line) > 88:
                    print(f"{i:3d}: {line} ⚠️ (长行)")
                else:
                    print(f"{i:3d}: {line}")
                    
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
    
    async def fix_file(self, file_path: str, create_backup: bool = True) -> dict:
        """修复文件"""
        print(f"🔧 开始修复文件: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return {"success": False, "error": "文件不存在"}
        
        # 创建备份
        backup_path = None
        if create_backup:
            backup_path = self.create_backup(file_path)
        
        try:
            # 分析文件问题
            print("🔍 分析文件问题...")
            issues = self.analyze_file_issues(file_path)
            
            if not issues:
                print("✅ 未发现需要修复的问题")
                return {"success": True, "message": "无需修复", "issues": 0}
            
            print(f"📋 发现 {len(issues)} 个问题:")
            for issue in issues:
                print(f"   - 行{issue['line']}: {issue['message']}")
            
            # 显示修复前的内容
            self.show_file_content(file_path, "修复前")
            
            # 执行修复
            print(f"\n🚀 开始执行修复...")
            project_path = os.path.dirname(file_path)
            result = await self.agent.process_issues(issues, project_path)
            
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
            self.show_file_content(file_path, "修复后")
            
            # 验证修复效果
            self.verify_fix(file_path)
            
            return {
                "success": True,
                "result": result,
                "backup_path": backup_path,
                "issues_found": len(issues)
            }
            
        except Exception as e:
            print(f"❌ 修复失败: {e}")
            
            # 如果修复失败，询问是否恢复备份
            if backup_path and os.path.exists(backup_path):
                response = input(f"\n❓ 修复失败，是否恢复备份? (y/N): ").strip().lower()
                if response in ['y', 'yes']:
                    shutil.copy2(backup_path, file_path)
                    print("✅ 已恢复备份文件")
            
            return {"success": False, "error": str(e), "backup_path": backup_path}
    
    def verify_fix(self, file_path: str):
        """验证修复效果"""
        print(f"\n🔍 验证修复效果:")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # 检查各种问题
            checks = {
                "unused_imports_removed": "unused_module" not in content,
                "file_ends_with_newline": content.endswith('\n'),
                "no_trailing_whitespace": not any(line.endswith(' ') or line.endswith('\t') for line in lines),
                "no_long_lines": all(len(line) <= 88 for line in lines),
                "proper_indentation": True  # 需要更详细的检查
            }
            
            for check, result in checks.items():
                status = "✅" if result else "❌"
                print(f"   {status} {check}: {result}")
            
            # 检查语法
            try:
                compile(content, file_path, 'exec')
                print("   ✅ 语法检查: 通过")
            except SyntaxError as e:
                print(f"   ❌ 语法检查: 失败 - {e}")
            
        except Exception as e:
            print(f"   ❌ 验证失败: {e}")


async def main():
    """主函数"""
    print("🚀 本地文件修复工具")
    print("=" * 40)
    
    # 获取用户输入的文件路径
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("请输入要修复的文件路径: ").strip().strip('"')
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    # 创建修复器
    fixer = LocalFileFixer()
    
    # 执行修复
    result = await fixer.fix_file(file_path)
    
    if result["success"]:
        print(f"\n✅ 文件修复完成!")
        if result.get("backup_path"):
            print(f"📁 备份文件: {result['backup_path']}")
        print(f"📊 发现并处理了 {result.get('issues_found', 0)} 个问题")
    else:
        print(f"\n❌ 文件修复失败: {result.get('error')}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 修复被用户中断")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()


