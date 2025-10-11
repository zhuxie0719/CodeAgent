#!/usr/bin/env python3
"""
简单测试工具是否工作
"""
import sys
import os
import subprocess

def test_pylint_direct():
    """直接测试pylint命令"""
    print("=== 直接测试Pylint命令 ===")
    
    test_file = "tests/test_python_bad.py"
    
    # 设置环境变量
    env = os.environ.copy()
    env['PAGER'] = ''
    env['LESS'] = ''
    env['PYTHONUNBUFFERED'] = '1'
    env['TERM'] = 'dumb'
    
    cmd = ['python', '-m', 'pylint', test_file, '--output-format=json', '--disable=C0114']
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
            stdin=subprocess.DEVNULL
        )
        
        print(f"返回码: {result.returncode}")
        print(f"标准输出长度: {len(result.stdout)}")
        print(f"标准错误长度: {len(result.stderr)}")
        
        if result.stdout:
            print("标准输出前200字符:")
            print(result.stdout[:200])
        
        if result.stderr:
            print("标准错误:")
            print(result.stderr)
            
        return result.returncode == 1  # pylint发现问题时返回1
        
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_flake8_direct():
    """直接测试flake8命令"""
    print("\n=== 直接测试Flake8命令 ===")
    
    test_file = "tests/test_python_bad.py"
    
    # 设置环境变量
    env = os.environ.copy()
    env['PAGER'] = ''
    env['LESS'] = ''
    env['PYTHONUNBUFFERED'] = '1'
    env['TERM'] = 'dumb'
    
    cmd = ['python', '-m', 'flake8', test_file, '--max-line-length=120']
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
            stdin=subprocess.DEVNULL
        )
        
        print(f"返回码: {result.returncode}")
        print(f"标准输出长度: {len(result.stdout)}")
        print(f"标准错误长度: {len(result.stderr)}")
        
        if result.stdout:
            print("标准输出:")
            print(result.stdout)
        
        if result.stderr:
            print("标准错误:")
            print(result.stderr)
            
        return result.returncode == 1  # flake8发现问题时返回1
        
    except Exception as e:
        print(f"错误: {e}")
        return False

if __name__ == "__main__":
    print("开始直接测试工具命令...")
    
    pylint_works = test_pylint_direct()
    flake8_works = test_flake8_direct()
    
    print(f"\n=== 测试结果 ===")
    print(f"Pylint工作: {pylint_works}")
    print(f"Flake8工作: {flake8_works}")
    
    if pylint_works or flake8_works:
        print("✅ 至少有一个工具能正常工作")
    else:
        print("❌ 两个工具都有问题")