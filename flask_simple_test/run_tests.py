#!/usr/bin/env python3
"""
Flask简单测试运行器
支持静态和动态检测模式
"""

import argparse
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask_simple_test.dynamic_test_runner import DynamicTestRunner
from flask_simple_test.test_flask_simple import StaticTestRunner


def main():
    parser = argparse.ArgumentParser(description='Flask简单测试运行器')
    parser.add_argument('--mode', choices=['static', 'dynamic', 'both'], 
                       default='both', help='检测模式')
    parser.add_argument('--target', type=str, default='.', 
                       help='目标文件或目录路径')
    parser.add_argument('--output', type=str, 
                       help='输出文件路径（可选）')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Flask简单测试运行器")
    print("=" * 60)
    
    # 运行静态检测
    if args.mode in ['static', 'both']:
        print("\n🔍 开始静态检测...")
        static_runner = StaticTestRunner()
        static_results = static_runner.run_analysis(args.target)
        
        if args.output:
            static_output = f"{args.output}_static.json"
            static_runner.save_results(static_results, static_output)
            print(f"静态检测结果已保存到: {static_output}")
    
    # 运行动态检测
    if args.mode in ['dynamic', 'both']:
        print("\n🚀 开始动态检测...")
        dynamic_runner = DynamicTestRunner()
        dynamic_results = dynamic_runner.run_dynamic_tests(args.target)
        
        if args.output:
            dynamic_output = f"{args.output}_dynamic.json"
            dynamic_runner.save_results(dynamic_results, dynamic_output)
            print(f"动态检测结果已保存到: {dynamic_output}")
    
    print("\n✅ 检测完成!")


if __name__ == "__main__":
    main()
