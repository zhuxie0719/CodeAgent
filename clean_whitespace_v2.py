#!/usr/bin/env python3
"""
清理空白字符工具 v2
增强版本，支持更多功能和配置
"""

import os
import re
import argparse
import json
from pathlib import Path
from typing import List, Optional, Dict, Any

class WhitespaceCleanerV2:
    """空白字符清理器 v2"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.cleaned_files = []
        self.errors = []
        self.stats = {
            "files_processed": 0,
            "files_cleaned": 0,
            "lines_removed": 0,
            "bytes_saved": 0
        }
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            "extensions": ['.py', '.js', '.html', '.css', '.md', '.txt', '.json'],
            "remove_trailing_whitespace": True,
            "remove_trailing_tabs": True,
            "normalize_line_endings": True,
            "max_consecutive_empty_lines": 2,
            "remove_final_empty_lines": True,
            "preserve_indentation": True,
            "backup_files": False
        }
    
    def clean_file(self, file_path: str) -> Dict[str, Any]:
        """清理单个文件"""
        result = {
            "file": file_path,
            "cleaned": False,
            "lines_removed": 0,
            "bytes_saved": 0,
            "error": None
        }
        
        try:
            self.stats["files_processed"] += 1
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            original_lines = len(content.split('\n'))
            original_size = len(content.encode('utf-8'))
            
            # 清理行尾空白
            if self.config["remove_trailing_whitespace"]:
                content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
            
            # 清理行尾制表符
            if self.config["remove_trailing_tabs"]:
                content = re.sub(r'\t+$', '', content, flags=re.MULTILINE)
            
            # 标准化行结束符
            if self.config["normalize_line_endings"]:
                content = content.replace('\r\n', '\n').replace('\r', '\n')
            
            # 清理连续的空行
            if self.config["max_consecutive_empty_lines"] > 0:
                max_empty = self.config["max_consecutive_empty_lines"]
                pattern = r'\n{' + str(max_empty + 1) + ',}'
                content = re.sub(pattern, '\n' * max_empty, content)
            
            # 清理文件末尾的空行
            if self.config["remove_final_empty_lines"]:
                content = content.rstrip() + '\n'
            
            # 如果内容有变化，写回文件
            if content != original_content:
                # 备份文件
                if self.config["backup_files"]:
                    backup_path = file_path + '.backup'
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                new_lines = len(content.split('\n'))
                new_size = len(content.encode('utf-8'))
                
                result["cleaned"] = True
                result["lines_removed"] = original_lines - new_lines
                result["bytes_saved"] = original_size - new_size
                
                self.stats["files_cleaned"] += 1
                self.stats["lines_removed"] += result["lines_removed"]
                self.stats["bytes_saved"] += result["bytes_saved"]
                
                self.cleaned_files.append(file_path)
            
        except Exception as e:
            result["error"] = str(e)
            self.errors.append(f"{file_path}: {e}")
        
        return result
    
    def clean_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """清理目录中的文件"""
        results = []
        path = Path(directory_path)
        
        if path.is_file():
            if path.suffix in self.config["extensions"]:
                result = self.clean_file(str(path))
                results.append(result)
        elif path.is_dir():
            for file_path in path.rglob('*'):
                if file_path.is_file() and file_path.suffix in self.config["extensions"]:
                    result = self.clean_file(str(file_path))
                    results.append(result)
        
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """获取清理总结"""
        return {
            "stats": self.stats,
            "cleaned_files": len(self.cleaned_files),
            "errors": len(self.errors),
            "files": self.cleaned_files,
            "error_details": self.errors,
            "config": self.config
        }
    
    def save_report(self, output_file: str):
        """保存清理报告"""
        report = {
            "timestamp": os.path.getmtime(output_file) if os.path.exists(output_file) else None,
            "summary": self.get_summary(),
            "details": self.cleaned_files
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='清理空白字符工具 v2')
    parser.add_argument('path', help='要清理的文件或目录路径')
    parser.add_argument('--extensions', nargs='+', 
                       default=['.py', '.js', '.html', '.css', '.md', '.txt', '.json'],
                       help='要清理的文件扩展名')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--report', help='保存清理报告到指定文件')
    parser.add_argument('--dry-run', action='store_true',
                       help='只显示会清理的文件，不实际修改')
    parser.add_argument('--backup', action='store_true',
                       help='清理前备份文件')
    parser.add_argument('--max-empty-lines', type=int, default=2,
                       help='最大连续空行数')
    
    args = parser.parse_args()
    
    # 加载配置
    config = None
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    # 创建清理器
    cleaner = WhitespaceCleanerV2(config)
    
    # 应用命令行参数
    cleaner.config["extensions"] = args.extensions
    cleaner.config["backup_files"] = args.backup
    cleaner.config["max_consecutive_empty_lines"] = args.max_empty_lines
    
    print(f"🧹 清理空白字符 v2: {args.path}")
    print(f"📁 文件类型: {', '.join(args.extensions)}")
    print(f"📊 最大连续空行: {args.max_empty_lines}")
    
    if args.dry_run:
        print("🔍 预览模式 - 不会实际修改文件")
        # 这里可以添加预览逻辑
        return
    
    results = cleaner.clean_directory(args.path)
    
    summary = cleaner.get_summary()
    
    print(f"✅ 清理完成!")
    print(f"📊 处理了 {summary['stats']['files_processed']} 个文件")
    print(f"🧹 清理了 {summary['stats']['files_cleaned']} 个文件")
    print(f"📝 移除了 {summary['stats']['lines_removed']} 行")
    print(f"💾 节省了 {summary['stats']['bytes_saved']} 字节")
    
    if summary["errors"]:
        print(f"❌ 遇到 {summary['errors']} 个错误:")
        for error in summary["error_details"]:
            print(f"  - {error}")
    
    if args.report:
        cleaner.save_report(args.report)
        print(f"📄 清理报告已保存到: {args.report}")


if __name__ == "__main__":
    main()
