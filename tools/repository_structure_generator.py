"""
仓库结构生成器
生成类似Linux tree命令格式的目录结构描述
"""

import os
from typing import Dict, List, Set, Tuple
from pathlib import Path


class RepositoryStructureGenerator:
    """仓库结构生成器"""
    
    def __init__(self):
        self.ignored_dirs = {
            '.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env', 
            '.env', '.pytest_cache', '.mypy_cache', 'htmlcov', 'coverage',
            'dist', 'build', '.tox', '.eggs', '.coverage',
            'target', 'bin', 'obj', '.vs', '.vscode', '.idea', 'logs', 
            'tmp', 'temp', 'cache', '.cache', 'backup', 'backups'
        }
        self.ignored_files = {
            '.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.log', '.tmp',
            '.cache', '.lock', '.pid', '.swp', '.swo', '~', '.DS_Store',
            'Thumbs.db', 'desktop.ini'
        }
    
    def generate_tree_structure(self, project_path: str, max_depth: int = 10) -> str:
        """
        生成树形结构字符串（类似Linux tree命令）
        
        Args:
            project_path: 项目路径
            max_depth: 最大深度
            
        Returns:
            树形结构字符串
        """
        if not os.path.exists(project_path):
            return f"路径不存在: {project_path}\n"
        
        if os.path.isfile(project_path):
            return f"{os.path.basename(project_path)}\n"
        
        lines = []
        project_name = os.path.basename(project_path) or project_path
        lines.append(f"{project_name}/")
        
        # 收集所有目录和文件
        dir_structure = {}  # {rel_path: {'dirs': [...], 'files': [...]}}
        
        for root, dirs, files in os.walk(project_path):
            # 过滤忽略的目录和文件
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs and not d.startswith('.')]
            files = [f for f in files 
                    if not any(f.endswith(ext) for ext in self.ignored_files)
                    and not f.startswith('.')]
            
            rel_root = os.path.relpath(root, project_path)
            depth = len(Path(rel_root).parts) if rel_root != '.' else 0
            
            if depth > max_depth:
                dirs.clear()
                continue
            
            dir_structure[rel_root if rel_root != '.' else ''] = {
                'dirs': sorted(dirs),
                'files': sorted(files),
                'depth': depth
            }
        
        # 递归生成树形结构
        self._generate_tree_for_dir('', dir_structure, project_path, lines, '', True, max_depth)
        
        return "\n".join(lines)
    
    def _generate_tree_for_dir(self, rel_dir: str, dir_structure: Dict, project_path: str, 
                               lines: List[str], prefix: str, is_last: bool, max_depth: int):
        """递归生成目录的树形结构"""
        if rel_dir not in dir_structure:
            return
        
        info = dir_structure[rel_dir]
        dirs = info['dirs']
        files = info['files']
        depth = info['depth']
        
        if depth >= max_depth:
            return
        
        # 合并目录和文件
        all_items = [(d, True, os.path.join(rel_dir, d) if rel_dir else d) for d in dirs] + \
                    [(f, False, None) for f in files]
        
        # 按名称排序（目录在前）
        all_items.sort(key=lambda x: (not x[1], x[0].lower()))
        
        for i, (item, is_dir, next_rel_path) in enumerate(all_items):
            is_last_item = (i == len(all_items) - 1)
            
            # 确定连接符
            if is_last:
                connector = "└── " if is_last_item else "├── "
                next_prefix = prefix + ("    " if is_last_item else "│   ")
            else:
                connector = "└── " if is_last_item else "├── "
                next_prefix = prefix + ("    " if is_last_item else "│   ")
            
            # 添加到输出
            icon = "📁" if is_dir else "📄"
            suffix = "/" if is_dir else ""
            lines.append(f"{prefix}{connector}{icon} {item}{suffix}")
            
            # 如果是目录，递归处理
            if is_dir and next_rel_path in dir_structure:
                self._generate_tree_for_dir(
                    next_rel_path,
                    dir_structure,
                    project_path,
                    lines,
                    next_prefix,
                    is_last_item,
                    max_depth
                )
    
    def save_tree_structure(self, project_path: str, output_file: str, max_depth: int = 10) -> bool:
        """
        保存树形结构到文件
        
        Args:
            project_path: 项目路径
            output_file: 输出文件路径
            max_depth: 最大深度
            
        Returns:
            是否成功保存
        """
        try:
            tree_structure = self.generate_tree_structure(project_path, max_depth)
            
            # 统计信息
            total_dirs = 0
            total_files = 0
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if d not in self.ignored_dirs and not d.startswith('.')]
                files = [f for f in files 
                        if not any(f.endswith(ext) for ext in self.ignored_files)
                        and not f.startswith('.')]
                total_dirs += len(dirs)
                total_files += len(files)
            
            # 添加元信息
            from datetime import datetime
            header = f"""# 仓库结构
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
项目路径: {project_path}
最大深度: {max_depth}

"""
            footer = f"""

---
统计信息:
- 总目录数: {total_dirs}
- 总文件数: {total_files}
- 过滤的目录: {', '.join(sorted(list(self.ignored_dirs)[:10]))}...
"""
            
            content = header + tree_structure + footer
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception as e:
            print(f"保存树形结构失败: {e}")
            import traceback
            traceback.print_exc()
            return False


# 全局实例
repository_structure_generator = RepositoryStructureGenerator()