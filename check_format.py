#!/usr/bin/env python3
"""
检查格式工具
用于检查代码文件的格式问题
"""

import os
import re
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

class FormatChecker:
    """格式检查器"""
    
    def __init__(self):
        self.issues = []
        self.stats = {
            "files_checked": 0,
            "files_with_issues": 0,
            "total_issues": 0
        }
    
    def check_file(self, file_path: str) -> List[Dict[str, Any]]:
        """检查单个文件"""
        file_issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # 检查各种格式问题
            for i, line in enumerate(lines):
                line_num = i + 1
                
                # 检查行尾空白
                if line.rstrip() != line:
                    file_issues.append({
                        "file": file_path,
                        "line": line_num,
                        "type": "trailing_whitespace",
                        "message": "行尾有多余空白字符",
                        "severity": "warning"
                    })
                
                # 检查行长度
                if len(line) > 120:
                    file_issues.append({
                        "file": file_path,
                        "line": line_num,
                        "type": "line_too_long",
                        "message": f"行长度超过120字符 ({len(line)})",
                        "severity": "warning"
                    })
                
                # 检查制表符
                if '\t' in line:
                    file_issues.append({
                        "file": file_path,
                        "line": line_num,
                        "type": "tab_character",
                        "message": "使用了制表符，建议使用空格",
                        "severity": "info"
                    })
                
                # 检查缩进
                if line.strip() and not line.startswith((' ', '\t')):
                    if any(keyword in line for keyword in ['def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except', 'with ']):
                        file_issues.append({
                            "file": file_path,
                            "line": line_num,
                            "type": "indentation",
                            "message": "缩进问题",
                            "severity": "error"
                        })
            
            # 检查文件末尾
            if content and not content.endswith('\n'):
                file_issues.append({
                    "file": file_path,
                    "line": len(lines),
                    "type": "missing_newline",
                    "message": "文件末尾缺少换行符",
                    "severity": "warning"
                })
            
            # 检查连续空行
            empty_line_count = 0
            for i, line in enumerate(lines):
                if not line.strip():
                    empty_line_count += 1
                else:
                    if empty_line_count > 2:
                        file_issues.append({
                            "file": file_path,
                            "line": i - empty_line_count + 1,
                            "type": "too_many_empty_lines",
                            "message": f"连续空行过多 ({empty_line_count})",
                            "severity": "warning"
                        })
                    empty_line_count = 0
            
        except Exception as e:
            file_issues.append({
                "file": file_path,
                "line": 0,
                "type": "file_error",
                "message": f"文件读取错误: {e}",
                "severity": "error"
            })
        
        return file_issues
    
    def check_directory(self, directory_path: str, extensions: List[str] = None) -> Dict[str, Any]:
        """检查目录中的文件"""
        if extensions is None:
            extensions = ['.py', '.js', '.html', '.css', '.md', '.txt']
        
        all_issues = []
        path = Path(directory_path)
        
        if path.is_file():
            if path.suffix in extensions:
                file_issues = self.check_file(str(path))
                all_issues.extend(file_issues)
                self.stats["files_checked"] += 1
                if file_issues:
                    self.stats["files_with_issues"] += 1
        elif path.is_dir():
            for file_path in path.rglob('*'):
                if file_path.is_file() and file_path.suffix in extensions:
                    file_issues = self.check_file(str(file_path))
                    all_issues.extend(file_issues)
                    self.stats["files_checked"] += 1
                    if file_issues:
                        self.stats["files_with_issues"] += 1
        
        self.issues = all_issues
        self.stats["total_issues"] = len(all_issues)
        
        return {
            "stats": self.stats,
            "issues": all_issues,
            "summary": self._get_summary()
        }
    
    def _get_summary(self) -> Dict[str, Any]:
        """获取问题总结"""
        summary = {
            "total_issues": len(self.issues),
            "by_type": {},
            "by_severity": {},
            "by_file": {}
        }
        
        for issue in self.issues:
            # 按类型统计
            issue_type = issue["type"]
            summary["by_type"][issue_type] = summary["by_type"].get(issue_type, 0) + 1
            
            # 按严重程度统计
            severity = issue["severity"]
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            
            # 按文件统计
            file_path = issue["file"]
            summary["by_file"][file_path] = summary["by_file"].get(file_path, 0) + 1
        
        return summary
    
    def save_report(self, output_file: str):
        """保存检查报告"""
        report = {
            "timestamp": os.path.getmtime(output_file) if os.path.exists(output_file) else None,
            "stats": self.stats,
            "issues": self.issues,
            "summary": self._get_summary()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='检查格式工具')
    parser.add_argument('path', help='要检查的文件或目录路径')
    parser.add_argument('--extensions', nargs='+', 
                       default=['.py', '.js', '.html', '.css', '.md', '.txt'],
                       help='要检查的文件扩展名')
    parser.add_argument('--report', help='保存检查报告到指定文件')
    parser.add_argument('--severity', choices=['error', 'warning', 'info'], 
                       default='warning', help='最低严重程度')
    
    args = parser.parse_args()
    
    checker = FormatChecker()
    
    print(f"🔍 检查格式: {args.path}")
    print(f"📁 文件类型: {', '.join(args.extensions)}")
    
    results = checker.check_directory(args.path, args.extensions)
    
    print(f"✅ 检查完成!")
    print(f"📊 检查了 {results['stats']['files_checked']} 个文件")
    print(f"⚠️ 发现 {results['stats']['total_issues']} 个问题")
    print(f"📝 有问题的文件: {results['stats']['files_with_issues']} 个")
    
    # 显示问题详情
    if results['issues']:
        print(f"\n📋 问题详情:")
        for issue in results['issues']:
            if issue['severity'] in ['error', 'warning']:
                print(f"  {issue['severity'].upper()}: {issue['file']}:{issue['line']} - {issue['message']}")
    
    # 显示总结
    summary = results['summary']
    print(f"\n📊 问题总结:")
    print(f"  按类型:")
    for issue_type, count in summary['by_type'].items():
        print(f"    {issue_type}: {count}")
    
    print(f"  按严重程度:")
    for severity, count in summary['by_severity'].items():
        print(f"    {severity}: {count}")
    
    if args.report:
        checker.save_report(args.report)
        print(f"📄 检查报告已保存到: {args.report}")


if __name__ == "__main__":
    main()
