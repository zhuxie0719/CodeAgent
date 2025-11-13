#!/usr/bin/env python3
"""
清理临时文件目录脚本
用于清理 api/temp_extract/ 下的临时项目目录
"""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def get_temp_dirs(base_path: Path) -> List[Path]:
    """获取所有临时目录"""
    temp_dirs = []
    if base_path.exists() and base_path.is_dir():
        for item in base_path.iterdir():
            if item.is_dir() and item.name.startswith("project_"):
                temp_dirs.append(item)
    return sorted(temp_dirs)

def get_dir_age(dir_path: Path) -> Optional[timedelta]:
    """获取目录的年龄（从创建时间到现在）"""
    try:
        # 尝试从目录名解析时间戳
        # 格式: project_YYYYMMDD_HHMMSS_或project_YYYYMMDD_HHMMSS_UUID
        name_parts = dir_path.name.split("_")
        if len(name_parts) >= 3:
            date_str = name_parts[1]  # YYYYMMDD
            time_str = name_parts[2]  # HHMMSS 或 HHMMSS_UUID
            
            # 处理可能包含UUID的情况
            if len(time_str) > 6:
                time_str = time_str[:6]  # 只取前6位（HHMMSS）
            
            if len(date_str) == 8 and len(time_str) == 6:
                try:
                    dir_time = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
                    return datetime.now() - dir_time
                except ValueError:
                    pass
        
        # 如果无法从名称解析，使用文件系统修改时间
        mtime = os.path.getmtime(dir_path)
        dir_time = datetime.fromtimestamp(mtime)
        return datetime.now() - dir_time
    except Exception as e:
        print(f"⚠️ 无法获取目录 {dir_path.name} 的年龄: {e}")
        return None

def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def get_dir_size(dir_path: Path) -> int:
    """获取目录大小（字节）"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(dir_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, FileNotFoundError):
                    pass
    except Exception as e:
        print(f"⚠️ 无法计算目录 {dir_path.name} 的大小: {e}")
    return total_size

def cleanup_temp_dirs(
    base_path: Path,
    older_than_days: Optional[int] = None,
    dry_run: bool = True,
    interactive: bool = False
) -> dict:
    """
    清理临时目录
    
    Args:
        base_path: 临时目录的基础路径
        older_than_days: 只清理超过指定天数的目录，None表示清理所有
        dry_run: 如果为True，只显示将要删除的目录，不实际删除
        interactive: 如果为True，删除前询问确认
    
    Returns:
        清理统计信息
    """
    stats = {
        "total_dirs": 0,
        "to_delete": 0,
        "deleted": 0,
        "failed": 0,
        "total_size": 0,
        "freed_size": 0
    }
    
    temp_dirs = get_temp_dirs(base_path)
    stats["total_dirs"] = len(temp_dirs)
    
    if not temp_dirs:
        print("✅ 没有找到临时目录")
        return stats
    
    print(f"📁 找到 {len(temp_dirs)} 个临时目录")
    print("=" * 80)
    
    # 分析目录
    dirs_to_delete = []
    for dir_path in temp_dirs:
        age = get_dir_age(dir_path)
        size = get_dir_size(dir_path)
        stats["total_size"] += size
        
        should_delete = True
        if older_than_days is not None and age:
            should_delete = age.days >= older_than_days
        
        if should_delete:
            dirs_to_delete.append({
                "path": dir_path,
                "age": age,
                "size": size
            })
            stats["to_delete"] += 1
            stats["freed_size"] += size
    
    if not dirs_to_delete:
        print("✅ 没有需要清理的目录")
        return stats
    
    # 显示将要删除的目录
    print(f"\n📋 将要{'删除' if not dry_run else '标记删除'}的目录 ({len(dirs_to_delete)} 个):")
    print("-" * 80)
    for i, dir_info in enumerate(dirs_to_delete, 1):
        age_str = f"{dir_info['age'].days}天" if dir_info['age'] else "未知"
        size_str = format_size(dir_info['size'])
        print(f"{i:3d}. {dir_info['path'].name}")
        print(f"     年龄: {age_str}, 大小: {size_str}")
    
    print("-" * 80)
    print(f"总计: {len(dirs_to_delete)} 个目录, 总大小: {format_size(stats['freed_size'])}")
    
    if dry_run:
        print("\n🔍 这是预览模式（dry-run），不会实际删除文件")
        print("   要实际删除，请使用 --execute 参数")
        return stats
    
    # 确认删除
    if interactive:
        response = input(f"\n⚠️  确定要删除这 {len(dirs_to_delete)} 个目录吗？(yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ 取消删除操作")
            return stats
    
    # 执行删除
    print(f"\n🗑️  开始删除 {len(dirs_to_delete)} 个目录...")
    for i, dir_info in enumerate(dirs_to_delete, 1):
        dir_path = dir_info["path"]
        try:
            print(f"[{i}/{len(dirs_to_delete)}] 删除: {dir_path.name}...", end=" ", flush=True)
            shutil.rmtree(dir_path, ignore_errors=False)
            print("✅")
            stats["deleted"] += 1
        except Exception as e:
            print(f"❌ 失败: {e}")
            stats["failed"] += 1
    
    print("\n" + "=" * 80)
    print(f"✅ 清理完成:")
    print(f"   - 成功删除: {stats['deleted']} 个目录")
    print(f"   - 失败: {stats['failed']} 个目录")
    print(f"   - 释放空间: {format_size(stats['freed_size'])}")
    
    return stats

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="清理临时文件目录",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 预览模式（不实际删除）
  python scripts/cleanup_temp_dirs.py
  
  # 删除所有临时目录
  python scripts/cleanup_temp_dirs.py --execute
  
  # 只删除7天前的目录
  python scripts/cleanup_temp_dirs.py --execute --older-than 7
  
  # 交互模式（删除前询问）
  python scripts/cleanup_temp_dirs.py --execute --interactive
        """
    )
    
    parser.add_argument(
        "--base-path",
        type=str,
        default="api/temp_extract",
        help="临时目录的基础路径（默认: api/temp_extract）"
    )
    
    parser.add_argument(
        "--older-than",
        type=int,
        default=None,
        help="只清理超过指定天数的目录（默认: 清理所有）"
    )
    
    parser.add_argument(
        "--execute",
        action="store_true",
        help="实际执行删除操作（默认: 预览模式）"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="删除前询问确认"
    )
    
    args = parser.parse_args()
    
    # 解析基础路径
    base_path = Path(project_root) / args.base_path
    
    if not base_path.exists():
        print(f"❌ 路径不存在: {base_path}")
        return 1
    
    print(f"📁 临时目录路径: {base_path.absolute()}")
    print(f"🔍 模式: {'执行删除' if args.execute else '预览模式'}")
    if args.older_than:
        print(f"⏰ 只清理超过 {args.older_than} 天的目录")
    else:
        print(f"⏰ 清理所有临时目录")
    print("=" * 80)
    
    # 执行清理
    stats = cleanup_temp_dirs(
        base_path=base_path,
        older_than_days=args.older_than,
        dry_run=not args.execute,
        interactive=args.interactive
    )
    
    return 0 if stats["failed"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

