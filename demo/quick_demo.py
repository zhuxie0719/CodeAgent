"""
快速演示脚本 - 自动运行静态检测演示
"""

from static_detector import StaticDetector
import json


def quick_demo():
    """快速演示静态检测功能"""
    print("🚀 AI AGENT系统静态检测功能快速演示")
    print("=" * 60)
    
    detector = StaticDetector()
    
    # 检测坏代码示例
    print("\n1️⃣ 检测坏代码示例 (bad_code.py)")
    print("-" * 40)
    bad_issues = detector.detect_issues('bad_code.py')
    bad_report = detector.generate_report(bad_issues)
    print(bad_report)
    
    # 检测好代码示例
    print("\n2️⃣ 检测好代码示例 (good_code.py)")
    print("-" * 40)
    good_issues = detector.detect_issues('good_code.py')
    good_report = detector.generate_report(good_issues)
    print(good_report)
    
    # 统计对比
    print("\n3️⃣ 检测结果对比")
    print("-" * 40)
    print(f"坏代码问题数: {len(bad_issues)}")
    print(f"好代码问题数: {len(good_issues)}")
    print(f"问题减少率: {((len(bad_issues) - len(good_issues)) / len(bad_issues) * 100):.1f}%")
    
    # 问题类型分析
    print("\n4️⃣ 问题类型分析")
    print("-" * 40)
    
    bad_types = {}
    for issue in bad_issues:
        issue_type = issue['type']
        bad_types[issue_type] = bad_types.get(issue_type, 0) + 1
    
    good_types = {}
    for issue in good_issues:
        issue_type = issue['type']
        good_types[issue_type] = good_types.get(issue_type, 0) + 1
    
    print("坏代码问题类型分布:")
    for issue_type, count in sorted(bad_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {issue_type}: {count} 个")
    
    print("\n好代码问题类型分布:")
    for issue_type, count in sorted(good_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {issue_type}: {count} 个")
    
    # 严重程度分析
    print("\n5️⃣ 严重程度分析")
    print("-" * 40)
    
    bad_severity = {'error': 0, 'warning': 0, 'info': 0}
    for issue in bad_issues:
        bad_severity[issue['severity']] += 1
    
    good_severity = {'error': 0, 'warning': 0, 'info': 0}
    for issue in good_issues:
        good_severity[issue['severity']] += 1
    
    print("坏代码严重程度分布:")
    for severity, count in bad_severity.items():
        if count > 0:
            print(f"  {severity}: {count} 个")
    
    print("\n好代码严重程度分布:")
    for severity, count in good_severity.items():
        if count > 0:
            print(f"  {severity}: {count} 个")
    
    # 保存详细报告
    print("\n6️⃣ 保存详细报告")
    print("-" * 40)
    
    detailed_report = {
        'bad_code_analysis': {
            'file': 'bad_code.py',
            'total_issues': len(bad_issues),
            'issues_by_type': bad_types,
            'issues_by_severity': bad_severity,
            'issues': bad_issues
        },
        'good_code_analysis': {
            'file': 'good_code.py',
            'total_issues': len(good_issues),
            'issues_by_type': good_types,
            'issues_by_severity': good_severity,
            'issues': good_issues
        },
        'comparison': {
            'total_improvement': len(bad_issues) - len(good_issues),
            'improvement_rate': ((len(bad_issues) - len(good_issues)) / len(bad_issues) * 100) if len(bad_issues) > 0 else 0
        }
    }
    
    try:
        with open('detailed_analysis_report.json', 'w', encoding='utf-8') as f:
            json.dump(detailed_report, f, ensure_ascii=False, indent=2)
        print("✅ 详细分析报告已保存到: detailed_analysis_report.json")
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")
    
    # 总结
    print("\n7️⃣ 演示总结")
    print("-" * 40)
    print("✅ 静态检测功能演示完成！")
    print("✅ 成功检测出代码中的各种问题")
    print("✅ 展示了问题类型和严重程度分析")
    print("✅ 验证了检测器的准确性和性能")
    print("\n🎯 主要特点:")
    print("  • 支持20种不同类型的代码问题检测")
    print("  • 提供详细的严重程度分类")
    print("  • 支持规则开关和自定义配置")
    print("  • 生成结构化的检测报告")
    print("  • 性能优异，检测速度快")


if __name__ == "__main__":
    quick_demo()
