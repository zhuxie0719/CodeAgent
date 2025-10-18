#!/usr/bin/env python3
"""
Flask 2.0.0 简化测试运行器
支持静态和动态测试模式
"""

import sys
import argparse
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Flask 2.0.0 测试运行器')
    parser.add_argument('--mode', choices=['static', 'dynamic', 'both'],
                       default='static', help='测试模式: static(静态), dynamic(动态), both(两者)')
    parser.add_argument('--enable-web-test', action='store_true',
                       help='启用Web应用测试（仅动态模式）')

    args = parser.parse_args()

    print(f"运行Flask 2.0.0测试... (模式: {args.mode})")
    print("="*70)

    try:
        if args.mode in ['static', 'both']:
            print("\n运行静态测试...")
            import test_flask_simple
            test_flask_simple.run_all_tests()

        if args.mode in ['dynamic', 'both']:
            print("\n运行动态测试...")
            from dynamic_test_runner import FlaskDynamicTestRunner

            runner = FlaskDynamicTestRunner()
            results = runner.run_dynamic_tests(enable_web_app_test=args.enable_web_test)

            # 显示动态测试摘要
            summary = results.get("summary", {})
            print("\n" + "="*50)
            print("动态测试摘要")
            print("="*50)
            print(f"总测试数: {summary.get('total_tests', 0)}")
            print(f"成功测试: {summary.get('successful_tests', 0)}")
            print(f"失败测试: {summary.get('failed_tests', 0)}")
            print(f"成功率: {summary.get('success_rate', 0)}%")
            print(f"整体状态: {summary.get('overall_status', 'unknown')}")

    except (ImportError, RuntimeError, AttributeError) as e:
        print(f"❌ 测试运行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
