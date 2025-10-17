#!/usr/bin/env python3
"""
清理空白字符工具 最终版本
支持多种清理模式、配置文件、详细报告
"""

import os
import re
import argparse
import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

class WhitespaceCleanerFinal:
    """空白字符清理器 最终版本"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.cleaned_files = []
        self.errors = []
        self.warnings = []
        self.stats = {
            "start_time": time.time(),
            "end_time": None,
            "files_processed": 0,
            "files_cleaned": 0,
            "files_skipped": 0,
            "lines_removed": 0,
            "bytes_saved": 0,
            "backup_files_created": 0
        }
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            "extensions": ['.py', '.js', '.html', '.css', '.md', '.txt', '.json', '.xml', '.yaml', '.yml'],
            "exclude_patterns": [
                r'\.git/',
                r'node_modules/',
                r'__pycache__/',
                r'\.pyc$',
                r'\.backup$'
            ],
            "cleaning_rules": {
                "remove_trailing_whitespace": True,
                "remove_trailing_tabs": True,
                "normalize_line_endings": True,
                "max_consecutive_empty_lines": 2,
                "remove_final_empty_lines": True,
                "preserve_indentation": True,
                "remove_bom": True
            },
            "backup": {
                "enabled": False,
                "suffix": ".backup",
                "directory": None
            },
            "reporting": {
                "verbose": False,
                "show_details": True,
                "save_report": False
            }
        }
    
    def _should_exclude_file(self, file_path: str) -> bool:
        """检查文件是否应该被排除"""
        for pattern in self.config["exclude_patterns"]:
            if re.search(pattern, file_path):
                return True
        return False
    
    def clean_file(self, file_path: str) -> Dict[str, Any]:
        """清理单个文件"""
        result = {
            "file": file_path,
            "cleaned": False,
            "skipped": False,
            "lines_removed": 0,
            "bytes_saved": 0,
            "backup_created": False,
            "error": None,
            "warning": None
        }
        
        try:
            self.stats["files_processed"] += 1
            
            # 检查是否应该排除
            if self._should_exclude_file(file_path):
                result["skipped"] = True
                self.stats["files_skipped"] += 1
                return result
            
            # 检查文件扩展名
            if Path(file_path).suffix not in self.config["extensions"]:
                result["skipped"] = True
                self.stats["files_skipped"] += 1
                return result
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            original_lines = len(content.split('\n'))
            original_size = len(content.encode('utf-8'))
            
            # 应用清理规则
            content = self._apply_cleaning_rules(content)
            
            # 如果内容有变化，写回文件
            if content != original_content:
                # 创建备份
                if self.config["backup"]["enabled"]:
                    backup_path = self._create_backup(file_path)
                    if backup_path:
                        result["backup_created"] = True
                        self.stats["backup_files_created"] += 1
                
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
    
    def _apply_cleaning_rules(self, content: str) -> str:
        """应用清理规则"""
        rules = self.config["cleaning_rules"]
        
        # 移除BOM
        if rules["remove_bom"]:
            content = content.lstrip('\ufeff')
        
        # 清理行尾空白
        if rules["remove_trailing_whitespace"]:
            content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
        
        # 清理行尾制表符
        if rules["remove_trailing_tabs"]:
            content = re.sub(r'\t+$', '', content, flags=re.MULTILINE)
        
        # 标准化行结束符
        if rules["normalize_line_endings"]:
            content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # 清理连续的空行
        if rules["max_consecutive_empty_lines"] > 0:
            max_empty = rules["max_consecutive_empty_lines"]
            pattern = r'\n{' + str(max_empty + 1) + ',}'
            content = re.sub(pattern, '\n' * max_empty, content)
        
        # 清理文件末尾的空行
        if rules["remove_final_empty_lines"]:
            content = content.rstrip() + '\n'
        
        return content
    
    def _create_backup(self, file_path: str) -> Optional[str]:
        """创建备份文件"""
        try:
            backup_config = self.config["backup"]
            
            if backup_config["directory"]:
                backup_dir = Path(backup_config["directory"])
                backup_dir.mkdir(parents=True, exist_ok=True)
                backup_path = backup_dir / (Path(file_path).name + backup_config["suffix"])
            else:
                backup_path = file_path + backup_config["suffix"]
            
            with open(file_path, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            return str(backup_path)
            
        except Exception as e:
            self.warnings.append(f"备份失败 {file_path}: {e}")
            return None
    
    def clean_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """清理目录中的文件"""
        results = []
        path = Path(directory_path)
        
        if path.is_file():
            result = self.clean_file(str(path))
            results.append(result)
        elif path.is_dir():
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    result = self.clean_file(str(file_path))
                    results.append(result)
        
        self.stats["end_time"] = time.time()
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """获取清理总结"""
        duration = self.stats["end_time"] - self.stats["start_time"] if self.stats["end_time"] else 0
        
        return {
            "stats": {
                **self.stats,
                "duration_seconds": duration
            },
            "cleaned_files": len(self.cleaned_files),
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "files": self.cleaned_files,
            "error_details": self.errors,
            "warning_details": self.warnings,
            "config": self.config
        }
    
    def save_report(self, output_file: str):
        """保存清理报告"""
        report = {
            "timestamp": time.time(),
            "summary": self.get_summary(),
            "details": self.cleaned_files
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='清理空白字符工具 最终版本')
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
    parser.add_argument('--backup-dir', help='备份文件目录')
    parser.add_argument('--max-empty-lines', type=int, default=2,
                       help='最大连续空行数')
    parser.add_argument('--verbose', action='store_true',
                       help='详细输出')
    parser.add_argument('--exclude', nargs='+', 
                       help='排除的文件模式')
    
    args = parser.parse_args()
    
    # 加载配置
    config = None
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    # 创建清理器
    cleaner = WhitespaceCleanerFinal(config)
    
    # 应用命令行参数
    cleaner.config["extensions"] = args.extensions
    cleaner.config["backup"]["enabled"] = args.backup
    cleaner.config["backup"]["directory"] = args.backup_dir
    cleaner.config["cleaning_rules"]["max_consecutive_empty_lines"] = args.max_empty_lines
    cleaner.config["reporting"]["verbose"] = args.verbose
    
    if args.exclude:
        cleaner.config["exclude_patterns"].extend(args.exclude)
    
    print(f"🧹 清理空白字符 最终版本: {args.path}")
    print(f"📁 文件类型: {', '.join(args.extensions)}")
    print(f"📊 最大连续空行: {args.max_empty_lines}")
    
    if args.backup:
        print(f"💾 备份已启用")
        if args.backup_dir:
            print(f"📁 备份目录: {args.backup_dir}")
    
    if args.dry_run:
        print("🔍 预览模式 - 不会实际修改文件")
        # 这里可以添加预览逻辑
        return
    
    results = cleaner.clean_directory(args.path)
    
    summary = cleaner.get_summary()
    
    print(f"✅ 清理完成!")
    print(f"⏱️ 耗时: {summary['stats']['duration_seconds']:.2f} 秒")
    print(f"📊 处理了 {summary['stats']['files_processed']} 个文件")
    print(f"🧹 清理了 {summary['stats']['files_cleaned']} 个文件")
    print(f"⏭️ 跳过了 {summary['stats']['files_skipped']} 个文件")
    print(f"📝 移除了 {summary['stats']['lines_removed']} 行")
    print(f"💾 节省了 {summary['stats']['bytes_saved']} 字节")
    
    if summary["stats"]["backup_files_created"] > 0:
        print(f"💾 创建了 {summary['stats']['backup_files_created']} 个备份文件")
    
    if summary["errors"]:
        print(f"❌ 遇到 {summary['errors']} 个错误:")
        for error in summary["error_details"]:
            print(f"  - {error}")
    
    if summary["warnings"]:
        print(f"⚠️ 遇到 {summary['warnings']} 个警告:")
        for warning in summary["warning_details"]:
            print(f"  - {warning}")
    
    if args.report:
        cleaner.save_report(args.report)
        print(f"📄 清理报告已保存到: {args.report}")


if __name__ == "__main__":
    main()
