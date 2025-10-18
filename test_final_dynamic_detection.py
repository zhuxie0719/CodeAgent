#!/usr/bin/env python3
"""
最终动态检测测试 - 综合测试所有动态检测功能
"""

import sys
import os
import json
import time
import traceback
import asyncio
from pathlib import Path
from typing import Dict, Any, List

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

class FinalDynamicDetectionTest:
    """最终动态检测测试类"""
    
    def __init__(self):
        self.test_results = {
            "timestamp": time.time(),
            "test_type": "final_dynamic_detection",
            "tests": {},
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0,
                "success_rate": 0.0,
                "overall_status": "unknown"
            }
        }
    
    async def run_final_tests(self, target_path: str = ".") -> Dict[str, Any]:
        """运行最终动态检测测试"""
        print("🚀 运行最终动态检测测试...")
        print(f"🎯 目标路径: {target_path}")
        
        try:
            # 测试1: 静态检测测试
            self._test_static_detection(target_path)
            
            # 测试2: 简化动态测试
            self._test_simple_dynamic(target_path)
            
            # 测试3: 无Flask动态测试
            self._test_no_flask_dynamic(target_path)
            
            # 测试4: 完整动态测试
            self._test_full_dynamic(target_path)
            
            # 测试5: API集成测试
            await self._test_api_integration(target_path)
            
            # 测试6: 前端集成测试
            self._test_frontend_integration()
            
            # 计算总结
            self._calculate_summary()
            
            print(f"✅ 最终动态检测测试完成")
            print(f"📊 成功率: {self.test_results['summary']['success_rate']:.1f}%")
            
            return self.test_results
            
        except Exception as e:
            print(f"❌ 最终动态检测测试失败: {e}")
            traceback.print_exc()
            return {
                "error": str(e),
                "timestamp": time.time(),
                "test_type": "final_dynamic_detection"
            }
    
    def _test_static_detection(self, target_path: str):
        """测试静态检测"""
        test_name = "static_detection"
        print(f"  🔍 测试静态检测...")
        
        try:
            from flask_simple_test.test_flask_simple import StaticTestRunner
            
            static_runner = StaticTestRunner()
            static_results = static_runner.run_analysis(target_path)
            
            # 分析静态检测结果
            issues_count = len(static_results.get("issues", []))
            flask_issues_count = len([issue for issue in static_results.get("issues", []) 
                                    if issue.get("category") == "flask"])
            
            self.test_results["tests"][test_name] = {
                "status": "passed",
                "details": {
                    "total_issues": issues_count,
                    "flask_issues": flask_issues_count,
                    "static_results": static_results
                }
            }
            print(f"    ✅ 静态检测完成 (发现 {issues_count} 个问题)")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"    ❌ 静态检测测试失败: {e}")
    
    def _test_simple_dynamic(self, target_path: str):
        """测试简化动态测试"""
        test_name = "simple_dynamic"
        print(f"  🔧 测试简化动态测试...")
        
        try:
            from flask_simple_test.simple_dynamic_test import SimpleDynamicTest
            
            simple_tester = SimpleDynamicTest()
            simple_results = simple_tester.run_simple_tests(target_path)
            
            # 分析简化动态测试结果
            success_rate = simple_results.get("summary", {}).get("success_rate", 0)
            total_tests = simple_results.get("summary", {}).get("total_tests", 0)
            
            self.test_results["tests"][test_name] = {
                "status": "passed" if success_rate >= 60 else "failed",
                "details": {
                    "success_rate": success_rate,
                    "total_tests": total_tests,
                    "simple_results": simple_results
                }
            }
            print(f"    ✅ 简化动态测试完成 (成功率: {success_rate:.1f}%)")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"    ❌ 简化动态测试失败: {e}")
    
    def _test_no_flask_dynamic(self, target_path: str):
        """测试无Flask动态测试"""
        test_name = "no_flask_dynamic"
        print(f"  🔧 测试无Flask动态测试...")
        
        try:
            from flask_simple_test.no_flask_dynamic_test import NoFlaskDynamicTest
            
            no_flask_tester = NoFlaskDynamicTest()
            no_flask_results = no_flask_tester.run_no_flask_tests(target_path)
            
            # 分析无Flask动态测试结果
            success_rate = no_flask_results.get("summary", {}).get("success_rate", 0)
            total_tests = no_flask_results.get("summary", {}).get("total_tests", 0)
            
            self.test_results["tests"][test_name] = {
                "status": "passed" if success_rate >= 60 else "failed",
                "details": {
                    "success_rate": success_rate,
                    "total_tests": total_tests,
                    "no_flask_results": no_flask_results
                }
            }
            print(f"    ✅ 无Flask动态测试完成 (成功率: {success_rate:.1f}%)")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"    ❌ 无Flask动态测试失败: {e}")
    
    def _test_full_dynamic(self, target_path: str):
        """测试完整动态测试"""
        test_name = "full_dynamic"
        print(f"  🚀 测试完整动态测试...")
        
        try:
            from flask_simple_test.dynamic_test_runner import DynamicTestRunner
            
            dynamic_runner = DynamicTestRunner()
            dynamic_results = dynamic_runner.run_dynamic_tests(target_path)
            
            # 分析完整动态测试结果
            success_rate = dynamic_results.get("summary", {}).get("success_rate", 0)
            total_tests = dynamic_results.get("summary", {}).get("total_tests", 0)
            
            self.test_results["tests"][test_name] = {
                "status": "passed" if success_rate >= 60 else "failed",
                "details": {
                    "success_rate": success_rate,
                    "total_tests": total_tests,
                    "dynamic_results": dynamic_results
                }
            }
            print(f"    ✅ 完整动态测试完成 (成功率: {success_rate:.1f}%)")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"    ❌ 完整动态测试失败: {e}")
    
    async def _test_api_integration(self, target_path: str):
        """测试API集成"""
        test_name = "api_integration"
        print(f"  🔌 测试API集成...")
        
        try:
            # 测试动态检测API
            from api.dynamic_api import SimpleDetector, DynamicMonitorAgent
            
            # 创建监控代理
            monitor_agent = DynamicMonitorAgent({
                "monitor_interval": 5,
                "alert_thresholds": {
                    "cpu_threshold": 80,
                    "memory_threshold": 85,
                    "disk_threshold": 90,
                    "network_threshold": 80
                }
            })
            
            detector = SimpleDetector(monitor_agent)
            
            # 测试Flask项目检测
            is_flask = await detector._detect_flask_project(target_path)
            
            # 测试动态检测
            dynamic_results = await detector._perform_dynamic_detection(
                target_path, 
                enable_flask_tests=True, 
                enable_server_tests=True
            )
            
            self.test_results["tests"][test_name] = {
                "status": "passed",
                "details": {
                    "is_flask_project": is_flask,
                    "dynamic_detection_results": dynamic_results,
                    "api_available": True
                }
            }
            print(f"    ✅ API集成测试完成")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"    ❌ API集成测试失败: {e}")
    
    def _test_frontend_integration(self):
        """测试前端集成"""
        test_name = "frontend_integration"
        print(f"  🎨 测试前端集成...")
        
        try:
            # 检查前端文件
            frontend_files = [
                "frontend/dynamic_detection.html",
                "frontend/index.html",
                "frontend/main.html"
            ]
            
            frontend_status = {}
            for file_path in frontend_files:
                if Path(file_path).exists():
                    frontend_status[file_path] = "exists"
                else:
                    frontend_status[file_path] = "missing"
            
            # 检查前端功能
            dynamic_detection_file = Path("frontend/dynamic_detection.html")
            frontend_features = {}
            
            if dynamic_detection_file.exists():
                with open(dynamic_detection_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查关键功能
                frontend_features = {
                    "enableDynamicDetection": "enableDynamicDetection" in content,
                    "enableFlaskSpecificTests": "enableFlaskSpecificTests" in content,
                    "enableServerTesting": "enableServerTesting" in content,
                    "ajax_calls": "ajax" in content.lower(),
                    "form_handling": "form" in content.lower()
                }
            
            self.test_results["tests"][test_name] = {
                "status": "passed",
                "details": {
                    "frontend_files": frontend_status,
                    "frontend_features": frontend_features,
                    "dynamic_detection_available": dynamic_detection_file.exists()
                }
            }
            print(f"    ✅ 前端集成测试完成")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"    ❌ 前端集成测试失败: {e}")
    
    def _calculate_summary(self):
        """计算测试总结"""
        tests = self.test_results["tests"]
        total = len(tests)
        passed = sum(1 for test in tests.values() if test["status"] == "passed")
        failed = sum(1 for test in tests.values() if test["status"] == "failed")
        skipped = sum(1 for test in tests.values() if test["status"] == "skipped")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        if success_rate >= 80:
            overall_status = "excellent"
        elif success_rate >= 60:
            overall_status = "good"
        elif success_rate >= 40:
            overall_status = "fair"
        else:
            overall_status = "poor"
        
        self.test_results["summary"].update({
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "skipped_tests": skipped,
            "success_rate": success_rate,
            "overall_status": overall_status
        })
    
    def save_results(self, results: Dict[str, Any], output_file: str):
        """保存测试结果"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"📄 测试结果已保存到: {output_file}")
        except Exception as e:
            print(f"❌ 保存结果失败: {e}")


async def test_async_functions():
    """测试异步函数"""
    print("🔄 测试异步功能...")
    
    try:
        # 测试动态检测API的异步功能
        from api.dynamic_api import SimpleDetector, DynamicMonitorAgent
        
        monitor_agent = DynamicMonitorAgent({
            "monitor_interval": 5,
            "alert_thresholds": {
                "cpu_threshold": 80,
                "memory_threshold": 85,
                "disk_threshold": 90,
                "network_threshold": 80
            }
        })
        
        detector = SimpleDetector(monitor_agent)
        
        # 测试Flask项目检测
        is_flask = await detector._detect_flask_project(".")
        print(f"  - Flask项目检测: {'是' if is_flask else '否'}")
        
        # 测试动态检测
        dynamic_results = await detector._perform_dynamic_detection(
            ".", 
            enable_flask_tests=True, 
            enable_server_tests=True
        )
        print(f"  - 动态检测结果: {dynamic_results.get('status', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 异步功能测试失败: {e}")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='最终动态检测测试')
    parser.add_argument('--target', type=str, default='.', 
                       help='目标文件或目录路径')
    parser.add_argument('--output', type=str, 
                       help='输出文件路径（可选）')
    parser.add_argument('--async-test', action='store_true',
                       help='运行异步测试')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("最终动态检测测试")
    print("=" * 60)
    
    tester = FinalDynamicDetectionTest()
    
    # 运行异步测试
    results = asyncio.run(tester.run_final_tests(args.target))
    
    # 运行异步测试
    if args.async_test:
        print("\n🔄 运行异步测试...")
        async_success = asyncio.run(test_async_functions())
        results["async_test_success"] = async_success
    
    if args.output:
        tester.save_results(results, args.output)
    
    return results


if __name__ == "__main__":
    main()
