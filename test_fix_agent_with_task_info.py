#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试修复Agent能否正常使用任务信息JSON文件"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from agents.fix_execution_agent.agent import FixExecutionAgent

def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def print_subsection(title: str):
    """打印子章节标题"""
    print(f"\n--- {title} ---")

def load_task_info(task_info_file: str) -> List[Dict[str, Any]]:
    """加载任务信息JSON文件"""
    try:
        with open(task_info_file, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        print(f"✅ 成功加载任务信息文件: {task_info_file}")
        print(f"   任务数量: {len(tasks)}")
        return tasks
    except Exception as e:
        print(f"❌ 加载任务信息文件失败: {e}")
        return []

def find_merged_defects_file(task_info_file: str) -> Optional[str]:
    """根据任务信息文件名查找对应的合并缺陷文件"""
    # 从任务信息文件名提取时间戳
    # 格式: agent_task_info_YYYYMMDD_HHMMSS.json
    task_file_name = Path(task_info_file).name
    if "agent_task_info_" in task_file_name:
        timestamp = task_file_name.replace("agent_task_info_", "").replace(".json", "")
        print(f"📝 查找时间戳为 {timestamp} 的缺陷文件...")
        
        # 在comprehensive_test_results目录中查找
        results_dir = Path("comprehensive_test_results")
        if results_dir.exists():
            defects_file = results_dir / f"flask_2_0_0_merged_defects_{timestamp}.json"
            print(f"   检查: {defects_file}")
            if defects_file.exists():
                print(f"   ✅ 找到: {defects_file}")
                return str(defects_file)
            else:
                # 尝试查找最接近时间戳的文件
                print(f"   未找到精确匹配，查找最接近的文件...")
                matching_files = list(results_dir.glob(f"flask_2_0_0_merged_defects_*.json"))
                if matching_files:
                    # 按时间戳排序，选择最接近的
                    matching_files.sort(key=lambda x: x.name)
                    closest_file = matching_files[-1]  # 选择最新的
                    print(f"   ✅ 使用最接近的文件: {closest_file}")
                    return str(closest_file)
        
        # 也在comprehensive_detection_results目录中查找完整结果
        detection_results_dir = Path("comprehensive_detection_results")
        if detection_results_dir.exists():
            # 查找包含该时间戳的结果文件
            for result_file in detection_results_dir.glob(f"comprehensive_detection_results_{timestamp}.json"):
                print(f"   ✅ 找到完整结果文件: {result_file}")
                return str(result_file)
        
        print(f"   ⚠️ 未找到匹配的缺陷文件")
    
    return None

def load_merged_defects(defects_file: Optional[str] = None, 
                        results_file: Optional[str] = None) -> List[Dict[str, Any]]:
    """加载合并缺陷清单"""
    if defects_file and os.path.exists(defects_file):
        try:
            with open(defects_file, 'r', encoding='utf-8') as f:
                defects = json.load(f)
            print(f"✅ 成功加载合并缺陷文件: {defects_file}")
            print(f"   缺陷数量: {len(defects)}")
            return defects
        except Exception as e:
            print(f"❌ 加载合并缺陷文件失败: {e}")
    
    # 尝试从完整结果文件中提取
    if results_file and os.path.exists(results_file):
        try:
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            defects = results.get("merged_defects", [])
            if defects:
                print(f"✅ 从完整结果文件中提取缺陷: {results_file}")
                print(f"   缺陷数量: {len(defects)}")
                return defects
        except Exception as e:
            print(f"❌ 加载完整结果文件失败: {e}")
    
    print("⚠️ 未找到合并缺陷文件，将使用任务信息中的文件路径")
    return []

def match_defects_to_task(task: Dict[str, Any], 
                         merged_defects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """将缺陷与任务匹配"""
    problem_file = task.get("problem_file", "")
    if not problem_file:
        return []
    
    # 标准化文件路径
    problem_file_normalized = problem_file.replace("\\", "/")
    
    # 匹配属于该文件的缺陷
    matched_defects = []
    for defect in merged_defects:
        defect_file = defect.get("file", "")
        defect_file_normalized = defect_file.replace("\\", "/")
        
        # 检查是否是同一个文件
        if problem_file_normalized in defect_file_normalized or defect_file_normalized in problem_file_normalized:
            # 转换为修复agent需要的格式
            issue = {
                "file": defect_file,
                "file_path": defect_file,  # 修复agent可能使用这个键
                "line": defect.get("line", 0),
                "message": defect.get("description", defect.get("message", "")),
                "severity": defect.get("severity", "info"),
                "tool": defect.get("tool", "unknown"),
                "source": defect.get("source", "unknown"),
                "symbol": defect.get("tool", ""),  # 修复agent可能需要
                "type": defect.get("tool", ""),
            }
            # 添加原始问题信息
            if "original_issue" in defect:
                original = defect["original_issue"]
                issue.update({
                    "message": original.get("message", issue["message"]),
                    "symbol": original.get("symbol", issue.get("symbol", "")),
                })
            
            matched_defects.append(issue)
    
    return matched_defects

async def test_fix_agent_with_task(task: Dict[str, Any], 
                                   defects: List[Dict[str, Any]],
                                   test_mode: bool = True) -> Dict[str, Any]:
    """使用单个任务测试修复Agent"""
    print_subsection(f"测试任务: {task.get('task', 'N/A')}")
    
    # 匹配缺陷
    matched_defects = match_defects_to_task(task, defects)
    print(f"   匹配到的缺陷数量: {len(matched_defects)}")
    
    if not matched_defects:
        print("⚠️ 未找到匹配的缺陷，使用任务信息中的defect_info创建缺陷数据...")
        # 使用任务信息中的defect_info创建缺陷数据
        problem_file = task.get("problem_file", "")
        defect_info = task.get("defect_info", {})
        task_description = task.get("task", "")
        
        if problem_file:
            # 从任务描述中提取信息，或使用defect_info
            line = defect_info.get("line", 0)
            severity = defect_info.get("severity", "warning")
            tool = defect_info.get("tool", "unknown")
            source = defect_info.get("source", "unknown")
            
            # 从任务描述中提取问题消息
            # 格式通常是："在 xxx.py 的第 N 行，tool 检测到问题：message"
            message = task_description
            if "，" in task_description and "：" in task_description:
                # 尝试提取冒号后的消息
                parts = task_description.split("：", 1)
                if len(parts) > 1:
                    message = parts[1].strip()
            
            matched_defects = [{
                "file": problem_file,
                "file_path": problem_file,
                "line": line,
                "message": message,
                "severity": severity,
                "tool": tool,
                "source": source,
                "symbol": tool,
                "type": tool,
            }]
            print(f"   已创建 {len(matched_defects)} 个缺陷用于测试（基于defect_info）")
            print(f"   行号: {line}, 严重程度: {severity}, 工具: {tool}")
    
    # 检查问题文件是否存在
    problem_file = task.get("problem_file", "")
    file_exists = problem_file and os.path.exists(problem_file)
    
    if not file_exists:
        print(f"⚠️ 问题文件不存在: {problem_file}")
        print(f"   如果这是临时文件路径，这是正常的")
        print(f"   项目根目录: {task.get('project_root', 'N/A')}")
    
    # 创建修复Agent实例（即使文件不存在也测试Agent初始化）
    agent_initialized = False
    try:
        print("🔧 正在初始化修复Agent...")
        agent = FixExecutionAgent(config={
            "LLM_MODEL": "deepseek-coder",
            "LLM_BASE_URL": "https://api.deepseek.com/v1/chat/completions"
        })
        await agent.initialize()
        agent_initialized = True
        print("✅ 修复Agent初始化成功")
    except Exception as e:
        print(f"❌ 修复Agent初始化失败: {e}")
        import traceback
        traceback.print_exc()
        if test_mode:
            # 测试模式下，即使初始化失败也返回部分结果
            return {
                "success": False,
                "test_mode": True,
                "message": f"Agent初始化失败: {e}",
                "task": task.get("task", ""),
                "matched_defects_count": len(matched_defects),
                "file_exists": file_exists,
                "agent_initialized": False
            }
        else:
            return {
                "success": False,
                "message": f"Agent初始化失败: {e}",
                "task": task.get("task", "")
            }
    
    if not file_exists:
        if test_mode:
            # 测试模式：验证数据结构，不实际修复
            return {
                "success": True,
                "test_mode": True,
                "message": "测试模式：文件不存在但数据结构正确，Agent初始化成功",
                "task": task.get("task", ""),
                "matched_defects_count": len(matched_defects),
                "file_exists": False,
                "agent_initialized": agent_initialized
            }
        else:
            return {
                "success": False,
                "message": f"文件不存在，无法执行修复: {problem_file}",
                "task": task.get("task", ""),
                "agent_initialized": agent_initialized
            }
    
    # 准备任务数据
    task_id = f"test_task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    task_data = {
        "file_path": problem_file,
        "project_path": task.get("project_root", ""),
        "issues": matched_defects
    }
    
    print(f"   任务ID: {task_id}")
    print(f"   文件路径: {problem_file}")
    print(f"   问题数量: {len(matched_defects)}")
    
    if test_mode:
        print("📝 测试模式：仅验证数据结构和Agent初始化，不执行实际修复")
        return {
            "success": True,
            "test_mode": True,
            "task_id": task_id,
            "task": task.get("task", ""),
            "file_path": problem_file,
            "matched_defects_count": len(matched_defects),
            "file_exists": True,
            "agent_initialized": True
        }
    
    # 执行修复（实际模式）
    try:
        print("🚀 开始执行修复...")
        result = await agent.process_task(task_id, task_data)
        print(f"✅ 修复完成")
        return result
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"修复失败: {e}",
            "task": task.get("task", "")
        }

async def test_fix_agent_with_task_info(task_info_file: str, 
                                       max_tasks: int = 3,
                                       test_mode: bool = True):
    """使用任务信息文件测试修复Agent"""
    print_section("修复Agent测试")
    
    # 加载任务信息
    tasks = load_task_info(task_info_file)
    if not tasks:
        print("❌ 无法加载任务信息，测试终止")
        return False
    
    # 显示任务列表
    print_subsection("任务列表")
    for i, task in enumerate(tasks[:max_tasks], 1):
        print(f"{i}. {task.get('task', 'N/A')}")
        print(f"   文件: {task.get('problem_file', 'N/A')}")
        print(f"   项目根目录: {task.get('project_root', 'N/A')}")
    
    # 尝试加载合并缺陷
    print_subsection("加载缺陷数据")
    merged_defects_file = find_merged_defects_file(task_info_file)
    merged_defects = load_merged_defects(merged_defects_file)
    
    # 测试前N个任务
    print_section("执行测试")
    test_results = []
    
    for i, task in enumerate(tasks[:max_tasks], 1):
        print(f"\n{'='*70}")
        print(f"测试任务 {i}/{min(max_tasks, len(tasks))}")
        print(f"{'='*70}")
        
        result = await test_fix_agent_with_task(task, merged_defects, test_mode=test_mode)
        test_results.append(result)
        
        if result.get("success"):
            print(f"✅ 任务 {i} 测试通过")
        else:
            print(f"❌ 任务 {i} 测试失败: {result.get('message', 'Unknown error')}")
    
    # 总结
    print_section("测试总结")
    success_count = sum(1 for r in test_results if r.get("success"))
    total_count = len(test_results)
    
    print(f"总任务数: {total_count}")
    print(f"成功: {success_count}")
    print(f"失败: {total_count - success_count}")
    
    if test_mode:
        print("\n📝 注意：这是测试模式，只验证数据结构和Agent初始化")
        print("   要执行实际修复，请将 test_mode 设置为 False")
    
    # 显示详细结果
    print_subsection("详细结果")
    for i, result in enumerate(test_results, 1):
        print(f"\n任务 {i}:")
        print(f"  成功: {result.get('success', False)}")
        print(f"  任务: {result.get('task', 'N/A')}")
        if result.get("test_mode"):
            print(f"  匹配缺陷数: {result.get('matched_defects_count', 0)}")
            print(f"  文件存在: {result.get('file_exists', False)}")
            print(f"  Agent初始化: {result.get('agent_initialized', False)}")
        else:
            print(f"  修复文件数: {len(result.get('fix_results', []))}")
            if result.get("errors"):
                print(f"  错误: {', '.join(result['errors'])}")
    
    return success_count == total_count

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="测试修复Agent能否正常使用任务信息JSON文件")
    parser.add_argument(
        "--task-info",
        type=str,
        default="comprehensive_detection_results/agent_task_info_20251102_214713.json",
        help="任务信息JSON文件路径"
    )
    parser.add_argument(
        "--max-tasks",
        type=int,
        default=3,
        help="最大测试任务数（默认3个）"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="执行实际修复（默认只测试数据结构）"
    )
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.task_info):
        print(f"❌ 任务信息文件不存在: {args.task_info}")
        print("\n可用的任务信息文件:")
        results_dir = Path("comprehensive_detection_results")
        if results_dir.exists():
            for task_file in sorted(results_dir.glob("agent_task_info_*.json")):
                print(f"  - {task_file}")
        return 1
    
    try:
        success = asyncio.run(
            test_fix_agent_with_task_info(
                args.task_info,
                max_tasks=args.max_tasks,
                test_mode=not args.execute
            )
        )
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

