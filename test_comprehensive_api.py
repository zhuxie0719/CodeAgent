#!/usr/bin/env python3
"""
测试综合检测API的Python脚本
"""

import requests
import json
import time

def test_comprehensive_detection():
    """测试综合检测API"""
    
    # API端点
    url = "http://localhost:8001/api/comprehensive/detect"
    
    # 准备文件
    files = {
        'file': ('test_project_fixed.zip', open('test_project_fixed.zip', 'rb'), 'application/zip')
    }
    
    # 准备表单数据
    data = {
        'static_analysis': 'true',
        'dynamic_monitoring': 'true', 
        'runtime_analysis': 'true',
        'enable_web_app_test': 'true',
        'enable_dynamic_detection': 'true',
        'enable_flask_specific_tests': 'true',
        'enable_server_testing': 'true',
        'upload_type': 'file'
    }
    
    print("🚀 开始测试综合检测API...")
    print(f"📁 上传文件: test_project_fixed.zip")
    print(f"🔗 API端点: {url}")
    print(f"⚙️ 检测选项: {data}")
    print("-" * 50)
    
    try:
        # 发送请求
        response = requests.post(url, files=files, data=data, timeout=300)
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("✅ 综合检测成功完成!")
                
                # 显示检测结果摘要
                results = result.get('data', {}).get('results', {})
                summary = results.get('summary', {})
                
                print("\n📋 检测结果摘要:")
                print(f"  - 检测类型: {results.get('detection_type', 'N/A')}")
                print(f"  - 检测时间: {results.get('timestamp', 'N/A')}")
                print(f"  - 总文件数: {summary.get('total_files', 0)}")
                print(f"  - 分析完成: {summary.get('analysis_completed', False)}")
                print(f"  - 总问题数: {summary.get('total_issues', 0)}")
                print(f"  - 严重问题: {summary.get('critical_issues', 0)}")
                print(f"  - 警告问题: {summary.get('warning_issues', 0)}")
                print(f"  - 信息问题: {summary.get('info_issues', 0)}")
                print(f"  - 整体状态: {summary.get('overall_status', 'N/A')}")
                
                # 显示检测选项
                options = results.get('analysis_options', {})
                print(f"\n⚙️ 检测配置:")
                for key, value in options.items():
                    print(f"  - {key}: {value}")
                
                # 显示AI报告摘要
                ai_report = result.get('data', {}).get('ai_report', '')
                if ai_report:
                    print(f"\n🤖 AI报告已生成 (长度: {len(ai_report)} 字符)")
                    print("AI报告预览:")
                    print("-" * 30)
                    print(ai_report[:500] + "..." if len(ai_report) > 500 else ai_report)
                    print("-" * 30)
                
                # 显示错误信息（如果有）
                if results.get('error'):
                    print(f"\n⚠️ 检测过程中出现错误: {results.get('error')}")
                
                # 显示建议
                recommendations = summary.get('recommendations', [])
                if recommendations:
                    print(f"\n💡 改进建议:")
                    for i, rec in enumerate(recommendations, 1):
                        print(f"  {i}. {rec}")
                
                print(f"\n📄 结果文件: {result.get('data', {}).get('results_file', 'N/A')}")
                print(f"📁 文件名: {result.get('data', {}).get('filename', 'N/A')}")
                
            else:
                print(f"❌ 检测失败: {result.get('message', '未知错误')}")
                if result.get('error'):
                    print(f"错误详情: {result.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ 请求超时，检测可能需要更长时间")
    except requests.exceptions.ConnectionError:
        print("🔌 连接错误，请确保API服务正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        # 关闭文件
        if 'files' in locals():
            files['file'][1].close()

def test_api_health():
    """测试API健康状态"""
    print("🔍 检查API健康状态...")
    
    try:
        # 检查主API健康状态
        response = requests.get("http://localhost:8001/health", timeout=10)
        if response.status_code == 200:
            print("✅ 主API服务正常")
        else:
            print(f"⚠️ 主API服务异常: {response.status_code}")
        
        # 检查综合检测API健康状态
        response = requests.get("http://localhost:8001/api/comprehensive/health", timeout=10)
        if response.status_code == 200:
            print("✅ 综合检测API服务正常")
        else:
            print(f"⚠️ 综合检测API服务异常: {response.status_code}")
            
        # 检查综合检测API状态
        response = requests.get("http://localhost:8001/api/comprehensive/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print("✅ 综合检测API状态正常")
            print(f"  - 状态: {status_data.get('status', 'N/A')}")
            print(f"  - 支持格式: {status_data.get('supported_formats', [])}")
            features = status_data.get('features', {})
            print(f"  - 功能特性:")
            for feature, enabled in features.items():
                print(f"    * {feature}: {'✅' if enabled else '❌'}")
        else:
            print(f"⚠️ 综合检测API状态异常: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")

if __name__ == "__main__":
    print("🧪 综合检测API测试脚本")
    print("=" * 50)
    
    # 首先检查API健康状态
    test_api_health()
    print()
    
    # 然后进行综合检测测试
    test_comprehensive_detection()
    
    print("\n🎉 测试完成!")
