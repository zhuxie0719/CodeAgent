"""
静态检测器测试运行器
"""

import unittest
import sys
import os
import time
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from static_detector import StaticDetector


class TestStaticDetector(unittest.TestCase):
    """静态检测器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.detector = StaticDetector()
        self.demo_dir = Path(__file__).parent
        self.bad_code_file = self.demo_dir / "bad_code.py"
        self.good_code_file = self.demo_dir / "good_code.py"
    
    def test_basic_detection(self):
        """测试基本检测功能"""
        print("\n🧪 测试基本检测功能...")
        
        # 检查文件是否存在
        self.assertTrue(self.bad_code_file.exists(), "bad_code.py 文件不存在")
        self.assertTrue(self.good_code_file.exists(), "good_code.py 文件不存在")
        
        # 检测坏代码
        bad_issues = self.detector.detect_issues(str(self.bad_code_file))
        self.assertGreater(len(bad_issues), 0, "坏代码应该检测到问题")
        print(f"   ✅ 坏代码检测到 {len(bad_issues)} 个问题")
        
        # 检测好代码
        good_issues = self.detector.detect_issues(str(self.good_code_file))
        print(f"   ✅ 好代码检测到 {len(good_issues)} 个问题")
    
    def test_detection_accuracy(self):
        """测试检测精度"""
        print("\n🧪 测试检测精度...")
        
        # 检测坏代码
        bad_issues = self.detector.detect_issues(str(self.bad_code_file))
        
        # 验证特定类型的问题被检测到
        issue_types = [issue['type'] for issue in bad_issues]
        
        expected_types = [
            'hardcoded_secret',
            'unsafe_eval', 
            'missing_type_hint',
            'long_function',
            'duplicate_code',
            'bad_exception_handling',
            'global_variable',
            'magic_number',
            'unsafe_file_operation',
            'missing_docstring',
            'bad_naming',
            'unhandled_exception',
            'deep_nesting',
            'insecure_random',
            'memory_leak',
            'missing_input_validation',
            'bad_formatting',
            'dead_code',
            'unused_variable'
        ]
        
        detected_types = []
        for expected_type in expected_types:
            if expected_type in issue_types:
                detected_types.append(expected_type)
        
        print(f"   ✅ 检测到 {len(detected_types)} 种问题类型: {', '.join(detected_types)}")
        self.assertGreaterEqual(len(detected_types), 10, "应该检测到至少10种问题类型")
    
    def test_good_code_detection(self):
        """测试好代码检测"""
        print("\n🧪 测试好代码检测...")
        
        good_issues = self.detector.detect_issues(str(self.good_code_file))
        
        # 好代码应该检测到较少问题
        print(f"   ✅ 好代码检测到 {len(good_issues)} 个问题")
        self.assertLessEqual(len(good_issues), 10, "好代码应该检测到较少问题")
    
    def test_rule_switches(self):
        """测试规则开关"""
        print("\n🧪 测试规则开关...")
        
        # 禁用某些规则
        self.detector.rules['unused_imports'] = False
        self.detector.rules['magic_numbers'] = False
        
        issues = self.detector.detect_issues(str(self.bad_code_file))
        
        # 验证特定类型的问题未被检测到
        unused_issues = [i for i in issues if i['type'] == 'unused_import']
        magic_issues = [i for i in issues if i['type'] == 'magic_number']
        
        print(f"   ✅ 未使用导入检测: {len(unused_issues)} 个 (应该为0)")
        print(f"   ✅ 魔法数字检测: {len(magic_issues)} 个 (应该为0)")
        
        self.assertEqual(len(unused_issues), 0, "未使用导入检测应该被禁用")
        self.assertEqual(len(magic_issues), 0, "魔法数字检测应该被禁用")
    
    def test_performance(self):
        """测试性能"""
        print("\n🧪 测试性能...")
        
        start_time = time.time()
        issues = self.detector.detect_issues(str(self.bad_code_file))
        end_time = time.time()
        
        detection_time = end_time - start_time
        print(f"   ✅ 检测耗时: {detection_time:.3f} 秒")
        
        self.assertLess(detection_time, 2.0, f"检测时间应该小于2秒，实际: {detection_time:.3f}秒")
    
    def test_empty_file(self):
        """测试空文件处理"""
        print("\n🧪 测试空文件处理...")
        
        # 创建临时空文件
        empty_file = self.demo_dir / "empty_test.py"
        with open(empty_file, 'w') as f:
            f.write("")
        
        try:
            issues = self.detector.detect_issues(str(empty_file))
            print(f"   ✅ 空文件检测到 {len(issues)} 个问题")
            self.assertIsInstance(issues, list, "应该返回问题列表")
        finally:
            # 清理临时文件
            if empty_file.exists():
                empty_file.unlink()
    
    def test_syntax_error_file(self):
        """测试语法错误文件处理"""
        print("\n🧪 测试语法错误文件处理...")
        
        # 创建语法错误文件
        error_file = self.demo_dir / "syntax_error_test.py"
        with open(error_file, 'w') as f:
            f.write("def broken_function(\n    return 'error'\n")
        
        try:
            issues = self.detector.detect_issues(str(error_file))
            print(f"   ✅ 语法错误文件检测到 {len(issues)} 个问题")
            
            # 应该检测到解析错误
            parse_errors = [i for i in issues if i['type'] == 'parse_error']
            self.assertGreater(len(parse_errors), 0, "应该检测到解析错误")
        finally:
            # 清理临时文件
            if error_file.exists():
                error_file.unlink()
    
    def test_report_generation(self):
        """测试报告生成"""
        print("\n🧪 测试报告生成...")
        
        issues = self.detector.detect_issues(str(self.bad_code_file))
        report = self.detector.generate_report(issues)
        
        self.assertIsInstance(report, str, "报告应该是字符串")
        self.assertIn("代码检测报告", report, "报告应该包含标题")
        self.assertIn("个问题", report, "报告应该包含问题数量")
        
        print("   ✅ 报告生成成功")
    
    def test_severity_distribution(self):
        """测试严重程度分布"""
        print("\n🧪 测试严重程度分布...")
        
        issues = self.detector.detect_issues(str(self.bad_code_file))
        
        severity_count = {'error': 0, 'warning': 0, 'info': 0}
        for issue in issues:
            severity_count[issue['severity']] += 1
        
        print(f"   ✅ 严重程度分布: {severity_count}")
        
        # 应该检测到各种严重程度的问题
        total_issues = sum(severity_count.values())
        self.assertGreater(total_issues, 0, "应该检测到问题")
    
    def test_issue_details(self):
        """测试问题详情"""
        print("\n🧪 测试问题详情...")
        
        issues = self.detector.detect_issues(str(self.bad_code_file))
        
        if issues:
            issue = issues[0]
            
            # 验证问题对象结构
            required_fields = ['type', 'severity', 'message', 'line']
            for field in required_fields:
                self.assertIn(field, issue, f"问题对象应该包含 {field} 字段")
            
            print(f"   ✅ 问题详情结构正确: {issue}")
    
    def tearDown(self):
        """测试后清理"""
        pass


def run_performance_benchmark():
    """运行性能基准测试"""
    print("\n🚀 运行性能基准测试...")
    
    detector = StaticDetector()
    demo_dir = Path(__file__).parent
    
    test_files = [
        "bad_code.py",
        "good_code.py"
    ]
    
    total_time = 0
    total_issues = 0
    
    for file_name in test_files:
        file_path = demo_dir / file_name
        if file_path.exists():
            start_time = time.time()
            issues = detector.detect_issues(str(file_path))
            end_time = time.time()
            
            detection_time = end_time - start_time
            total_time += detection_time
            total_issues += len(issues)
            
            print(f"   📁 {file_name}: {len(issues)} 个问题, {detection_time:.3f} 秒")
    
    if total_time > 0:
        avg_time = total_time / len(test_files)
        print(f"   📊 平均检测时间: {avg_time:.3f} 秒")
        print(f"   📊 总问题数: {total_issues}")


def main():
    """主函数"""
    print("🧪 开始运行静态检测器测试...")
    print("=" * 60)
    
    # 运行单元测试
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 运行性能基准测试
    run_performance_benchmark()
    
    print("\n✅ 所有测试完成！")


if __name__ == "__main__":
    main()
