#!/usr/bin/env python3
"""
清理空白字符工具
用于清理代码文件中的多余空白字符
"""

import os
import re
import argparse
from pathlib import Path
from typing import List, Optional

class WhitespaceCleaner:
    """空白字符清理器"""
    
    def __init__(self):
        self.cleaned_files = []
        self.errors = []
    
    def clean_file(self, file_path: str) -> bool:
        """清理单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 清理行尾空白
            content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
            
            # 清理文件末尾多余的空行
            content = content.rstrip() + '\n'
            
            # 清理连续的空行（最多保留2个）
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            # 如果内容有变化，写回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.cleaned_files.append(file_path)
                return True
            
            return False
            
        except Exception as e:
            self.errors.append(f"{file_path}: {e}")
            return False
    
    def clean_directory(self, directory_path: str, extensions: List[str] = None) -> int:
        """清理目录中的文件"""
        if extensions is None:
            extensions = ['.py', '.js', '.html', '.css', '.md', '.txt']
        
        cleaned_count = 0
        path = Path(directory_path)
        
        if path.is_file():
            if path.suffix in extensions:
                if self.clean_file(str(path)):
                    cleaned_count += 1
        elif path.is_dir():
            for file_path in path.rglob('*'):
                if file_path.is_file() and file_path.suffix in extensions:
                    if self.clean_file(str(file_path)):
                        cleaned_count += 1
        
        return cleaned_count
    
    def get_summary(self) -> dict:
        """获取清理总结"""
        return {
            "cleaned_files": len(self.cleaned_files),
            "errors": len(self.errors),
            "files": self.cleaned_files,
            "error_details": self.errors
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='清理空白字符工具')
    parser.add_argument('path', help='要清理的文件或目录路径')
    parser.add_argument('--extensions', nargs='+', 
                       default=['.py', '.js', '.html', '.css', '.md', '.txt'],
                       help='要清理的文件扩展名')
    parser.add_argument('--dry-run', action='store_true',
                       help='只显示会清理的文件，不实际修改')
    
    args = parser.parse_args()
    
    cleaner = WhitespaceCleaner()
    
    print(f"🧹 清理空白字符: {args.path}")
    print(f"📁 文件类型: {', '.join(args.extensions)}")
    
    if args.dry_run:
        print("🔍 预览模式 - 不会实际修改文件")
        # 这里可以添加预览逻辑
        return
    
    cleaned_count = cleaner.clean_directory(args.path, args.extensions)
    
    summary = cleaner.get_summary()
    
    print(f"✅ 清理完成!")
    print(f"📊 清理了 {cleaned_count} 个文件")
    
    if summary["errors"]:
        print(f"❌ 遇到 {summary['errors']} 个错误:")
        for error in summary["error_details"]:
            print(f"  - {error}")
    
    if summary["cleaned_files"]:
        print(f"📝 已清理的文件:")
        for file in summary["files"]:
            print(f"  - {file}")


if __name__ == "__main__":
    main()
