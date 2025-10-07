#!/usr/bin/env python3
"""
完整功能测试脚本
测试深度分析和基本分析功能
"""

import requests
import time
import json

def test_api_health():
    """测试API健康状态"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        print(f"✅ 主API健康检查: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ 主API健康检查失败: {e}")
        return False

def test_code_analysis_health():
    """测试代码分析API健康状态"""
    try:
        response = requests.get("http://localhost:8001/api/code-analysis/health", timeout=5)
        print(f"✅ 代码分析API健康检查: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ 代码分析API健康检查失败: {e}")
        return False

def test_simple_analysis_health():
    """测试简化版分析API健康状态"""
    try:
        response = requests.get("http://localhost:8001/api/simple-code-analysis/health", timeout=5)
        print(f"✅ 简化版分析API健康检查: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ 简化版分析API健康检查失败: {e}")
        return False

def test_basic_analysis():
    """测试基本分析功能"""
    try:
        print("\n🔍 测试基本分析功能...")
        
        # 创建测试文件
        test_content = '''
def hello_world():
    """测试函数"""
    print("Hello, World!")
    return "Hello, World!"

if __name__ == "__main__":
    hello_world()
'''
        
        files = {"file": ("test.py", test_content, "text/plain")}
        params = {
            "enable_static": "true",
            "enable_pylint": "true", 
            "enable_flake8": "true",
            "enable_ai_analysis": "false",
            "analysis_type": "file"
        }
        
        response = requests.post(
            "http://localhost:8001/api/v1/detection/upload",
            files=files,
            params=params,
            timeout=10
        )
        
        print(f"基本分析上传状态: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("data", {}).get("task_id")
            print(f"✅ 基本分析上传成功，任务ID: {task_id}")
            
            # 测试任务状态查询
            if task_id:
                status_response = requests.get(f"http://localhost:8001/api/v1/tasks/{task_id}", timeout=5)
                print(f"任务状态查询: {status_response.status_code}")
                if status_response.status_code == 200:
                    print("✅ 任务状态查询成功")
                else:
                    print(f"❌ 任务状态查询失败: {status_response.text}")
            
            return True
        else:
            print(f"❌ 基本分析上传失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 基本分析测试失败: {e}")
        return False

def test_deep_analysis():
    """测试深度分析功能"""
    try:
        print("\n🔍 测试深度分析功能...")
        
        # 创建测试文件
        test_content = '''
def hello_world():
    """测试函数"""
    print("Hello, World!")
    return "Hello, World!"

if __name__ == "__main__":
    hello_world()
'''
        
        files = {"files": ("test.py", test_content, "text/plain")}
        data = {
            "include_ai_analysis": "true",
            "analysis_depth": "comprehensive"
        }
        
        response = requests.post(
            "http://localhost:8001/api/code-analysis/analyze-upload",
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"深度分析上传状态: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ 深度分析上传成功")
            print(f"分析结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ 深度分析上传失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 深度分析测试失败: {e}")
        return False

def test_simple_analysis():
    """测试简化版分析功能"""
    try:
        print("\n🔍 测试简化版分析功能...")
        
        # 创建测试文件
        test_content = '''
def hello_world():
    """测试函数"""
    print("Hello, World!")
    return "Hello, World!"

if __name__ == "__main__":
    hello_world()
'''
        
        files = {"files": ("test.py", test_content, "text/plain")}
        data = {
            "include_ai_analysis": "false",
            "analysis_depth": "basic"
        }
        
        response = requests.post(
            "http://localhost:8001/api/simple-code-analysis/analyze-upload",
            files=files,
            data=data,
            timeout=10
        )
        
        print(f"简化版分析上传状态: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ 简化版分析上传成功")
            print(f"分析结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ 简化版分析上传失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 简化版分析测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始完整功能测试...")
    print("=" * 50)
    
    # 等待API启动
    print("等待API启动...")
    time.sleep(5)
    
    # 测试API健康状态
    print("\n📊 测试API健康状态...")
    health_ok = test_api_health()
    code_analysis_ok = test_code_analysis_health()
    simple_analysis_ok = test_simple_analysis_health()
    
    if not (health_ok and code_analysis_ok and simple_analysis_ok):
        print("❌ API健康检查失败，请检查API服务器")
        return
    
    # 测试基本分析
    basic_ok = test_basic_analysis()
    
    # 测试深度分析
    deep_ok = test_deep_analysis()
    
    # 测试简化版分析
    simple_ok = test_simple_analysis()
    
    # 总结
    print("\n" + "=" * 50)
    print("📋 测试结果总结:")
    print(f"基本分析: {'✅ 通过' if basic_ok else '❌ 失败'}")
    print(f"深度分析: {'✅ 通过' if deep_ok else '❌ 失败'}")
    print(f"简化版分析: {'✅ 通过' if simple_ok else '❌ 失败'}")
    
    if basic_ok and (deep_ok or simple_ok):
        print("\n🎉 所有功能测试通过！")
    else:
        print("\n⚠️ 部分功能测试失败，需要进一步修复")

if __name__ == "__main__":
    main()

