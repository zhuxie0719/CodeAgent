#!/usr/bin/env python3
"""
修复执行Agent API测试脚本
演示如何通过API接口使用修复执行Agent
"""

import requests
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional


class FixAgentAPITester:
    """修复执行Agent API测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def check_api_health(self) -> bool:
        """检查API健康状态"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ API服务正常运行")
                return True
            else:
                print(f"❌ API服务异常: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 无法连接到API服务: {e}")
            return False
    
    def upload_file_for_analysis(self, file_path: str, analysis_options: Dict[str, Any] = None) -> Optional[str]:
        """上传文件进行分析"""
        if analysis_options is None:
            analysis_options = {
                "enable_static": True,
                "enable_pylint": True,
                "enable_flake8": True,
                "enable_ai_analysis": False,
                "enable_deep_analysis": False
            }
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = analysis_options
                
                response = self.session.post(
                    f"{self.base_url}/api/v1/detection/upload",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        task_id = result['data']['task_id']
                        print(f"✅ 文件上传成功，任务ID: {task_id}")
                        return task_id
                    else:
                        print(f"❌ 上传失败: {result.get('message')}")
                        return None
                else:
                    print(f"❌ 上传失败: HTTP {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"❌ 上传异常: {e}")
            return None
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/tasks/{task_id}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result['data']
                else:
                    print(f"❌ 获取状态失败: {result.get('message')}")
                    return None
            else:
                print(f"❌ 获取状态失败: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 获取状态异常: {e}")
            return None
    
    def wait_for_task_completion(self, task_id: str, timeout: int = 60) -> Optional[Dict[str, Any]]:
        """等待任务完成"""
        print(f"⏳ 等待任务完成: {task_id}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_task_status(task_id)
            
            if status is None:
                return None
            
            task_status = status.get('status')
            print(f"   任务状态: {task_status}")
            
            if task_status == 'completed':
                print("✅ 任务完成")
                return status
            elif task_status == 'failed':
                print(f"❌ 任务失败: {status.get('error')}")
                return status
            
            time.sleep(2)
        
        print(f"⏰ 任务超时 ({timeout}秒)")
        return None
    
    def get_ai_report(self, task_id: str) -> Optional[str]:
        """获取AI分析报告"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/ai-reports/{task_id}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result['data']['report']
                else:
                    print(f"❌ 获取报告失败: {result.get('message')}")
                    return None
            else:
                print(f"❌ 获取报告失败: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 获取报告异常: {e}")
            return None
    
    def get_structured_data(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取结构化数据"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/structured-data/{task_id}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result['data']
                else:
                    print(f"❌ 获取结构化数据失败: {result.get('message')}")
                    return None
            else:
                print(f"❌ 获取结构化数据失败: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 获取结构化数据异常: {e}")
            return None
    
    def test_basic_analysis(self, file_path: str):
        """测试基础分析功能"""
        print("\n🔍 测试基础分析功能")
        print("-" * 30)
        
        # 上传文件
        task_id = self.upload_file_for_analysis(file_path, {
            "enable_static": True,
            "enable_pylint": True,
            "enable_flake8": True,
            "enable_ai_analysis": False,
            "enable_deep_analysis": False
        })
        
        if not task_id:
            return
        
        # 等待完成
        result = self.wait_for_task_completion(task_id)
        if not result:
            return
        
        # 显示结果
        self.display_analysis_result(result)
    
    def test_ai_analysis(self, file_path: str):
        """测试AI分析功能"""
        print("\n🤖 测试AI分析功能")
        print("-" * 30)
        
        # 上传文件
        task_id = self.upload_file_for_analysis(file_path, {
            "enable_static": True,
            "enable_pylint": True,
            "enable_flake8": True,
            "enable_ai_analysis": True,
            "enable_deep_analysis": False
        })
        
        if not task_id:
            return
        
        # 等待完成
        result = self.wait_for_task_completion(task_id)
        if not result:
            return
        
        # 获取AI报告
        report = self.get_ai_report(task_id)
        if report:
            print("📊 AI分析报告:")
            print(report[:500] + "..." if len(report) > 500 else report)
    
    def test_deep_analysis(self, file_path: str):
        """测试深度分析功能"""
        print("\n🔬 测试深度分析功能")
        print("-" * 30)
        
        # 上传文件
        task_id = self.upload_file_for_analysis(file_path, {
            "enable_static": True,
            "enable_pylint": True,
            "enable_flake8": True,
            "enable_ai_analysis": True,
            "enable_deep_analysis": True
        })
        
        if not task_id:
            return
        
        # 等待完成
        result = self.wait_for_task_completion(task_id)
        if not result:
            return
        
        # 显示深度分析结果
        self.display_deep_analysis_result(result)
    
    def display_analysis_result(self, result: Dict[str, Any]):
        """显示分析结果"""
        print("📋 分析结果:")
        
        if 'result' in result:
            data = result['result']
            print(f"   分析文件数: {data.get('files_analyzed', 0)}")
            print(f"   发现问题数: {data.get('issues_found', 0)}")
            print(f"   分析类型: {data.get('analysis_type', 'unknown')}")
            print(f"   摘要: {data.get('summary', '无')}")
            
            # 显示文件详情
            if 'file_details' in data:
                print("   文件详情:")
                for file_detail in data['file_details']:
                    print(f"     - {file_detail.get('filename', 'unknown')}: {file_detail.get('size', 0)} bytes")
            
            # 显示分析结果
            if 'analysis_results' in data:
                print("   分析结果:")
                for analysis in data['analysis_results']:
                    filename = analysis.get('filename', 'unknown')
                    issues_count = len(analysis.get('issues', []))
                    print(f"     - {filename}: {issues_count} 个问题")
                    
                    # 显示前3个问题
                    for issue in analysis.get('issues', [])[:3]:
                        severity = issue.get('severity', 'unknown')
                        message = issue.get('message', '无描述')
                        line = issue.get('line', 0)
                        print(f"       [{severity}] 行{line}: {message}")
    
    def display_deep_analysis_result(self, result: Dict[str, Any]):
        """显示深度分析结果"""
        print("📊 深度分析结果:")
        
        if 'result' in result and 'deep_analysis' in result['result']:
            deep_data = result['result']['deep_analysis']
            
            # 显示AI洞察
            if 'ai_insights' in deep_data:
                insights = deep_data['ai_insights']
                print("   🤖 AI洞察:")
                for key, value in insights.items():
                    if isinstance(value, list):
                        print(f"     {key}: {', '.join(map(str, value))}")
                    else:
                        print(f"     {key}: {value}")
            
            # 显示代码质量报告
            if 'code_quality_report' in deep_data:
                quality = deep_data['code_quality_report']
                print("   📈 代码质量:")
                print(f"     质量评分: {quality.get('quality_score', 0)}/100")
                print(f"     可维护性: {quality.get('maintainability', 'unknown')}")
                print(f"     可读性: {quality.get('readability', 'unknown')}")
            
            # 显示性能分析
            if 'performance_analysis' in deep_data:
                performance = deep_data['performance_analysis']
                print("   ⚡ 性能分析:")
                print(f"     算法复杂度: {performance.get('algorithm_complexity', 'unknown')}")
                print(f"     性能评分: {performance.get('performance_score', 0)}/100")
    
    def test_code_analysis_api(self, file_path: str):
        """测试代码分析API"""
        print("\n📝 测试代码分析API")
        print("-" * 30)
        
        try:
            with open(file_path, 'rb') as f:
                files = [('files', f)]
                data = {
                    'include_ai_analysis': True,
                    'analysis_depth': 'basic'
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/simple-code-analysis/analyze-upload",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        task_id = result['data']['task_id']
                        print(f"✅ 代码分析任务创建成功: {task_id}")
                        
                        # 等待完成
                        analysis_result = self.wait_for_task_completion(task_id)
                        if analysis_result:
                            self.display_code_analysis_result(analysis_result)
                    else:
                        print(f"❌ 代码分析失败: {result.get('message')}")
                else:
                    print(f"❌ 代码分析失败: HTTP {response.status_code}")
                    
        except Exception as e:
            print(f"❌ 代码分析异常: {e}")
    
    def display_code_analysis_result(self, result: Dict[str, Any]):
        """显示代码分析结果"""
        print("📋 代码分析结果:")
        
        if 'result' in result:
            data = result['result']
            print(f"   分析文件数: {data.get('files_analyzed', 0)}")
            print(f"   分析类型: {data.get('analysis_type', 'unknown')}")
            print(f"   包含AI分析: {data.get('include_ai_analysis', False)}")
            print(f"   摘要: {data.get('summary', '无')}")
            
            # 显示AI摘要
            if 'ai_summary' in data:
                print("   🤖 AI分析摘要:")
                summary = data['ai_summary']
                # 只显示前300个字符
                print(f"     {summary[:300]}{'...' if len(summary) > 300 else ''}")
    
    def run_comprehensive_test(self, test_file_path: str):
        """运行综合测试"""
        print("🚀 开始修复执行Agent API综合测试")
        print("=" * 50)
        
        # 检查API健康状态
        if not self.check_api_health():
            print("❌ API服务不可用，请先启动API服务")
            return
        
        # 检查测试文件
        if not Path(test_file_path).exists():
            print(f"❌ 测试文件不存在: {test_file_path}")
            return
        
        print(f"📁 使用测试文件: {test_file_path}")
        
        # 运行各项测试
        self.test_basic_analysis(test_file_path)
        self.test_ai_analysis(test_file_path)
        self.test_deep_analysis(test_file_path)
        self.test_code_analysis_api(test_file_path)
        
        print("\n✅ 所有API测试完成!")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="修复执行Agent API测试")
    parser.add_argument("--file", "-f", default="tests/test_python_bad.py", 
                       help="测试文件路径")
    parser.add_argument("--url", "-u", default="http://localhost:8001",
                       help="API服务地址")
    
    args = parser.parse_args()
    
    # 创建测试器
    tester = FixAgentAPITester(args.url)
    
    # 运行测试
    tester.run_comprehensive_test(args.file)


if __name__ == "__main__":
    main()


