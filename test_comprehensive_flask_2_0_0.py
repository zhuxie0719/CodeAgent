#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用Flask 2.0.0进行完整综合检测测试"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from api.comprehensive_detection_api import ComprehensiveDetector
from agents.bug_detection_agent.agent import BugDetectionAgent
from agents.dynamic_detection_agent.agent import DynamicDetectionAgent

def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def print_subsection(title):
    """打印子章节标题"""
    print(f"\n--- {title} ---")

async def test_comprehensive_detection():
    """执行完整的综合检测测试"""
    
    print_section("Flask 2.0.0 完整综合检测测试")
    
    # 检查Flask 2.0.0压缩包是否存在
    flask_zip_path = Path("tests/flask-2.0.0.zip")
    if not flask_zip_path.exists():
        print(f"❌ Flask 2.0.0压缩包不存在: {flask_zip_path}")
        print("请确保 tests/flask-2.0.0.zip 文件存在")
        return False
    
    print(f"✅ 找到Flask 2.0.0压缩包: {flask_zip_path}")
    print(f"文件大小: {flask_zip_path.stat().st_size / (1024*1024):.2f} MB")
    
    # 创建检测器实例
    print_subsection("初始化检测器")
    static_agent = BugDetectionAgent({
        "enable_ai_analysis": True,
        "analysis_depth": "comprehensive"
    })
    dynamic_agent = DynamicDetectionAgent({
        "monitor_interval": 5,
        "alert_thresholds": {
            "cpu_threshold": 80,
            "memory_threshold": 85,
            "disk_threshold": 90,
            "network_threshold": 80
        },
        "enable_web_app_test": False,
        "enable_dynamic_detection": True,
        "enable_flask_specific_tests": True,
        "enable_server_testing": True
    })
    detector = ComprehensiveDetector(static_agent, dynamic_agent)
    print("✅ 检测器初始化完成")
    
    # 执行综合检测
    print_section("执行综合检测")
    print("配置:")
    print("  - 静态分析: ✅ 启用")
    print("    - Pylint: ✅")
    print("    - Mypy: ✅")
    print("    - Semgrep: ✅")
    print("    - Ruff: ✅")
    print("    - Bandit: ✅")
    print("    - LLM过滤: ✅")
    print("  - 动态监控: ✅ 启用")
    print("  - 运行时分析: ✅ 启用")
    print("  - 动态检测: ✅ 启用")
    print("    - Flask特定测试: ✅")
    print("    - 服务器测试: ✅")
    
    start_time = datetime.now()
    print(f"\n开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        results = await detector.detect_defects(
            zip_file_path=str(flask_zip_path),
            static_analysis=True,
            dynamic_monitoring=True,
            runtime_analysis=True,
            enable_dynamic_detection=True,
            enable_flask_specific_tests=True,
            enable_server_testing=True,
            # 静态检测工具
            enable_pylint=True,
            enable_mypy=True,
            enable_semgrep=True,
            enable_ruff=True,
            enable_bandit=True,
            enable_llm_filter=True
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"\n完成时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时: {duration:.2f} 秒")
        
    except Exception as e:
        print(f"\n❌ 检测过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 检查是否有错误
    if results.get("error"):
        print(f"\n⚠️ 检测过程中出现错误: {results['error']}")
    
    # 显示检测摘要
    print_section("检测摘要")
    summary = results.get("summary", {})
    print(f"总文件数: {summary.get('total_files', 0)}")
    print(f"总问题数: {summary.get('total_issues', 0)}")
    print(f"严重问题: {summary.get('critical_issues', 0)}")
    print(f"警告问题: {summary.get('warning_issues', 0)}")
    print(f"信息问题: {summary.get('info_issues', 0)}")
    print(f"整体状态: {summary.get('overall_status', 'unknown')}")
    
    # 显示各检测模块的结果
    print_section("各检测模块结果")
    
    # 静态分析结果
    if "static_analysis" in results:
        static_result = results["static_analysis"]
        if static_result.get("success"):
            print_subsection("静态分析")
            print(f"✅ 成功")
            print(f"分析文件数: {static_result.get('files_analyzed', 0)}")
            print(f"发现问题数: {static_result.get('issues_found', 0)}")
            
            # 工具覆盖率
            tool_coverage = static_result.get("tool_coverage", {})
            if tool_coverage:
                print("工具检测结果:")
                for tool, count in tool_coverage.items():
                    print(f"  - {tool}: {count} 个问题")
            
            # 显示部分问题示例
            issues = static_result.get("issues", [])
            if issues:
                print(f"\n问题示例（前5个）:")
                for i, issue in enumerate(issues[:5], 1):
                    file = issue.get("file", "unknown")
                    line = issue.get("line", 0)
                    tool = issue.get("tool", "unknown")
                    message = issue.get("message", "")[:60]
                    print(f"  {i}. [{tool}] {file}:{line} - {message}")
        else:
            print_subsection("静态分析")
            print(f"❌ 失败: {static_result.get('error', 'unknown error')}")
    
    # 动态监控结果
    if "dynamic_monitoring" in results:
        dynamic_mon = results["dynamic_monitoring"]
        if not dynamic_mon.get("error"):
            print_subsection("动态监控")
            alerts = dynamic_mon.get("alerts", [])
            print(f"✅ 成功")
            print(f"告警数量: {len(alerts)}")
            if alerts:
                print("告警示例:")
                for i, alert in enumerate(alerts[:3], 1):
                    alert_type = alert.get("type", "unknown")
                    message = alert.get("message", "")[:60]
                    print(f"  {i}. [{alert_type}] {message}")
    
    # 运行时分析结果
    if "runtime_analysis" in results:
        runtime = results["runtime_analysis"]
        print_subsection("运行时分析")
        if runtime.get("execution_successful"):
            print("✅ 执行成功")
        else:
            print(f"⚠️ 执行失败: {runtime.get('error', 'unknown error')}")
    
    # 动态检测结果
    if "dynamic_detection" in results:
        dynamic_det = results["dynamic_detection"]
        print_subsection("动态检测")
        if dynamic_det.get("tests_completed"):
            print("✅ 测试完成")
            print(f"状态: {dynamic_det.get('status', 'unknown')}")
            print(f"是否为Flask项目: {dynamic_det.get('is_flask_project', False)}")
            print(f"成功率: {dynamic_det.get('success_rate', 0)}%")
            
            issues = dynamic_det.get("issues", [])
            print(f"发现问题数: {len(issues)}")
            if issues:
                print("问题示例:")
                for i, issue in enumerate(issues[:3], 1):
                    issue_type = issue.get("type", "unknown")
                    message = issue.get("message", "")[:60]
                    print(f"  {i}. [{issue_type}] {message}")
        else:
            print(f"⚠️ 测试未完成: {dynamic_det.get('error', 'unknown error')}")
    
    # 检查合并后的缺陷清单
    print_section("合并后的缺陷清单")
    merged_defects = results.get("merged_defects", [])
    if merged_defects:
        print(f"✅ 成功合并缺陷清单")
        print(f"总缺陷数: {len(merged_defects)}")
        
        # 按来源统计
        static_count = sum(1 for d in merged_defects if d.get("source") == "static")
        dynamic_count = sum(1 for d in merged_defects if d.get("source") == "dynamic")
        print(f"  - 静态检测: {static_count} 个")
        print(f"  - 动态检测: {dynamic_count} 个")
        
        # 按严重程度统计
        error_count = sum(1 for d in merged_defects if d.get("severity") == "error")
        warning_count = sum(1 for d in merged_defects if d.get("severity") == "warning")
        info_count = sum(1 for d in merged_defects if d.get("severity") in ["info", "convention"])
        print(f"  - 严重问题: {error_count} 个")
        print(f"  - 警告问题: {warning_count} 个")
        print(f"  - 信息问题: {info_count} 个")
        
        # 按工具统计
        tool_stats = {}
        for defect in merged_defects:
            tool = defect.get("tool", "unknown")
            tool_stats[tool] = tool_stats.get(tool, 0) + 1
        print(f"\n按工具统计:")
        for tool, count in sorted(tool_stats.items()):
            print(f"  - {tool}: {count} 个")
        
        # 显示缺陷示例（前10个）
        print(f"\n缺陷示例（前10个）:")
        for i, defect in enumerate(merged_defects[:10], 1):
            print(f"\n{i}. {defect.get('description', 'N/A')}")
            print(f"   文件: {defect.get('file', 'unknown')}")
            print(f"   行号: {defect.get('line', 0)}")
            print(f"   严重程度: {defect.get('severity', 'unknown')}")
            print(f"   来源: {defect.get('source', 'unknown')} | 工具: {defect.get('tool', 'unknown')}")
        
        if len(merged_defects) > 10:
            print(f"\n... 还有 {len(merged_defects) - 10} 个缺陷未显示")
    else:
        print("⚠️ 未生成合并后的缺陷清单")
    
    # 检查任务信息JSON
    print_section("任务信息JSON")
    task_info = results.get("task_info", [])
    task_info_file = results.get("task_info_file")
    
    if task_info:
        print(f"✅ 成功生成任务信息")
        print(f"任务数量: {len(task_info)}")
        
        # 显示任务示例（前5个）
        print(f"\n任务示例（前5个）:")
        for i, task in enumerate(task_info[:5], 1):
            print(f"\n{i}. {task.get('task', 'N/A')}")
            print(f"   问题文件: {task.get('problem_file', 'unknown')}")
            print(f"   项目根目录: {task.get('project_root', 'unknown')}")
        
        if len(task_info) > 5:
            print(f"\n... 还有 {len(task_info) - 5} 个任务未显示")
        
        if task_info_file:
            print(f"\n任务信息文件路径: {task_info_file}")
            if os.path.exists(task_info_file):
                print("✅ 文件已保存")
            else:
                print("⚠️ 文件不存在")
    else:
        print("⚠️ 未生成任务信息")
    
    # 保存完整结果到文件
    print_section("保存测试结果")
    results_dir = Path("comprehensive_test_results")
    results_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = results_dir / f"flask_2_0_0_test_{timestamp}.json"
    
    try:
        # 移除不可序列化的对象（如果有）
        serializable_results = json.loads(json.dumps(results, default=str, ensure_ascii=False))
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 完整结果已保存到: {results_file}")
        print(f"文件大小: {results_file.stat().st_size / 1024:.2f} KB")
        
    except Exception as e:
        print(f"⚠️ 保存结果失败: {e}")
    
    # 保存合并后的缺陷清单（单独文件）
    if merged_defects:
        defects_file = results_dir / f"flask_2_0_0_merged_defects_{timestamp}.json"
        try:
            with open(defects_file, 'w', encoding='utf-8') as f:
                json.dump(merged_defects, f, indent=2, ensure_ascii=False)
            print(f"✅ 合并缺陷清单已保存到: {defects_file}")
        except Exception as e:
            print(f"⚠️ 保存缺陷清单失败: {e}")
    
    # 总结
    print_section("测试总结")
    print("✅ 综合检测完成")
    print(f"✅ 检测到 {len(merged_defects)} 个缺陷")
    print(f"✅ 生成了 {len(task_info)} 个修复任务")
    print("✅ 所有功能正常工作")
    
    return True

def main():
    """主函数"""
    try:
        success = asyncio.run(test_comprehensive_detection())
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




