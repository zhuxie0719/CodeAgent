"""
AI AGENT系统静态检测功能演示脚本
"""

import os
import sys
import json
from pathlib import Path
from static_detector import StaticDetector


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    AI AGENT 系统演示                         ║
║                静态代码缺陷检测功能                           ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_menu():
    """打印菜单"""
    menu = """
请选择操作：
1. 检测坏代码示例 (bad_code.py)
2. 检测好代码示例 (good_code.py)
3. 检测指定文件
4. 批量检测目录
5. 查看检测规则
6. 退出

请输入选项 (1-6): """
    return input(menu).strip()


def detect_file(file_path: str):
    """检测单个文件"""
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    print(f"\n🔍 正在检测文件: {file_path}")
    print("=" * 60)
    
    detector = StaticDetector()
    issues = detector.detect_issues(file_path)
    
    # 显示检测结果
    report = detector.generate_report(issues)
    print(report)
    
    # 显示详细统计
    if issues:
        print("\n📊 详细统计:")
        severity_count = {'error': 0, 'warning': 0, 'info': 0}
        type_count = {}
        
        for issue in issues:
            severity_count[issue['severity']] += 1
            issue_type = issue['type']
            type_count[issue_type] = type_count.get(issue_type, 0) + 1
        
        print(f"  严重程度分布:")
        for severity, count in severity_count.items():
            if count > 0:
                print(f"    {severity}: {count} 个")
        
        print(f"  问题类型分布:")
        for issue_type, count in sorted(type_count.items()):
            print(f"    {issue_type}: {count} 个")
    
    return issues


def detect_directory(directory_path: str):
    """检测目录中的所有Python文件"""
    if not os.path.exists(directory_path):
        print(f"❌ 目录不存在: {directory_path}")
        return
    
    print(f"\n🔍 正在检测目录: {directory_path}")
    print("=" * 60)
    
    detector = StaticDetector()
    all_issues = []
    file_count = 0
    
    # 遍历目录中的Python文件
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                print(f"\n📁 检测文件: {file_path}")
                
                issues = detector.detect_issues(file_path)
                all_issues.extend(issues)
                file_count += 1
                
                if issues:
                    print(f"   发现 {len(issues)} 个问题")
                else:
                    print("   ✅ 无问题")
    
    # 显示总体报告
    print(f"\n📊 总体检测结果:")
    print(f"  检测文件数: {file_count}")
    print(f"  总问题数: {len(all_issues)}")
    
    if all_issues:
        severity_count = {'error': 0, 'warning': 0, 'info': 0}
        for issue in all_issues:
            severity_count[issue['severity']] += 1
        
        print(f"  问题分布:")
        for severity, count in severity_count.items():
            if count > 0:
                print(f"    {severity}: {count} 个")
    
    return all_issues


def show_detection_rules():
    """显示检测规则"""
    rules = """
🔍 检测规则说明：

1. 未使用的导入 (unused_imports)
   - 检测导入但未使用的模块

2. 硬编码秘密信息 (hardcoded_secrets)
   - 检测硬编码的密码、API密钥等

3. 不安全的eval使用 (unsafe_eval)
   - 检测使用eval函数的安全风险

4. 缺少类型注解 (missing_type_hints)
   - 检测函数参数和返回值缺少类型注解

5. 过长的函数 (long_functions)
   - 检测超过50行的函数

6. 重复代码 (duplicate_code)
   - 检测相似的代码块

7. 异常处理不当 (bad_exception_handling)
   - 检测裸露的except语句

8. 全局变量使用 (global_variables)
   - 检测全局变量的使用

9. 魔法数字 (magic_numbers)
   - 检测硬编码的数字常量

10. 不安全的文件操作 (unsafe_file_operations)
    - 检测硬编码的文件路径

11. 缺少文档字符串 (missing_docstrings)
    - 检测函数和类缺少文档

12. 命名不规范 (bad_naming)
    - 检测不符合Python命名规范的标识符

13. 未处理的异常 (unhandled_exceptions)
    - 检测可能抛出异常但未处理的代码

14. 过深的嵌套 (deep_nesting)
    - 检测超过4层的代码嵌套

15. 不安全的随机数 (insecure_random)
    - 检测使用不安全的随机数生成

16. 内存泄漏风险 (memory_leaks)
    - 检测可能的内存泄漏

17. 缺少输入验证 (missing_input_validation)
    - 检测用户输入处理缺少验证

18. 代码格式问题 (bad_formatting)
    - 检测缩进和格式问题

19. 死代码 (dead_code)
    - 检测可能未被使用的代码

20. 未使用的变量 (unused_variables)
    - 检测定义但未使用的变量
    """
    print(rules)


def save_report(issues: list, filename: str = "detection_report.json"):
    """保存检测报告到文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(issues, f, ensure_ascii=False, indent=2)
        print(f"📄 检测报告已保存到: {filename}")
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")


def main():
    """主函数"""
    print_banner()
    
    # 检查演示文件是否存在
    demo_dir = Path(__file__).parent
    bad_code_file = demo_dir / "bad_code.py"
    good_code_file = demo_dir / "good_code.py"
    
    if not bad_code_file.exists():
        print("❌ 演示文件 bad_code.py 不存在")
        return
    
    if not good_code_file.exists():
        print("❌ 演示文件 good_code.py 不存在")
        return
    
    while True:
        choice = print_menu()
        
        if choice == '1':
            # 检测坏代码示例
            issues = detect_file(str(bad_code_file))
            if issues:
                save_choice = input("\n是否保存检测报告? (y/n): ").strip().lower()
                if save_choice == 'y':
                    save_report(issues, "bad_code_report.json")
        
        elif choice == '2':
            # 检测好代码示例
            issues = detect_file(str(good_code_file))
            if issues:
                save_choice = input("\n是否保存检测报告? (y/n): ").strip().lower()
                if save_choice == 'y':
                    save_report(issues, "good_code_report.json")
        
        elif choice == '3':
            # 检测指定文件
            file_path = input("请输入文件路径: ").strip()
            if file_path:
                issues = detect_file(file_path)
                if issues:
                    save_choice = input("\n是否保存检测报告? (y/n): ").strip().lower()
                    if save_choice == 'y':
                        save_report(issues, "custom_file_report.json")
        
        elif choice == '4':
            # 批量检测目录
            dir_path = input("请输入目录路径: ").strip()
            if dir_path:
                issues = detect_directory(dir_path)
                if issues:
                    save_choice = input("\n是否保存检测报告? (y/n): ").strip().lower()
                    if save_choice == 'y':
                        save_report(issues, "directory_report.json")
        
        elif choice == '5':
            # 查看检测规则
            show_detection_rules()
        
        elif choice == '6':
            # 退出
            print("\n👋 感谢使用AI AGENT系统演示！")
            break
        
        else:
            print("❌ 无效选项，请重新选择")
        
        input("\n按回车键继续...")


if __name__ == "__main__":
    main()
