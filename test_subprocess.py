#!/usr/bin/env python3
"""
直接测试subprocess调用
"""
import subprocess
import json
import os

def test_pylint_direct():
    test_file = "tests/test_python_bad.py"
    
    if not os.path.exists(test_file):
        print(f"文件不存在: {test_file}")
        return
    
    print("测试pylint直接调用...")
    
    # 尝试不同的pylint命令
    commands = [
        ['pylint', test_file, '--output-format=json', '--disable=C0114'],
        ['pylint', test_file, '--output-format=json'],
        ['pylint', test_file],
        ['python', '-m', 'pylint', test_file, '--output-format=json']
    ]
    
    for i, cmd in enumerate(commands):
        print(f"\n尝试命令 {i+1}: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            print(f"  返回码: {result.returncode}")
            print(f"  stdout长度: {len(result.stdout)}")
            print(f"  stderr长度: {len(result.stderr)}")
            
            if result.stdout:
                print(f"  stdout前200字符: {result.stdout[:200]}")
            
            if result.stderr:
                print(f"  stderr前200字符: {result.stderr[:200]}")
                
            # 尝试解析JSON
            if result.stdout and result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    print(f"  JSON解析成功，项目数: {len(data)}")
                    if data:
                        print(f"  第一个项目: {data[0]}")
                except json.JSONDecodeError as e:
                    print(f"  JSON解析失败: {e}")
            
        except subprocess.TimeoutExpired:
            print("  超时")
        except Exception as e:
            print(f"  错误: {e}")

def test_flake8_direct():
    test_file = "tests/test_python_bad.py"
    
    print("\n测试flake8直接调用...")
    
    commands = [
        ['flake8', test_file],
        ['python', '-m', 'flake8', test_file]
    ]
    
    for i, cmd in enumerate(commands):
        print(f"\n尝试命令 {i+1}: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            print(f"  返回码: {result.returncode}")
            print(f"  stdout长度: {len(result.stdout)}")
            print(f"  stderr长度: {len(result.stderr)}")
            
            if result.stdout:
                print(f"  stdout: {result.stdout}")
            
            if result.stderr:
                print(f"  stderr: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("  超时")
        except Exception as e:
            print(f"  错误: {e}")

if __name__ == "__main__":
    test_pylint_direct()
    test_flake8_direct()

