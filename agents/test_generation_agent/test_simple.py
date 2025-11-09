#!/usr/bin/env python3
"""
TestGenerationAgent 简单测试脚本
直接调用Agent，仅使用LLM生成测试（不需要Docker）
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径（CodeAgent目录）
# test_simple.py 在 agents/test_generation_agent/ 下
# 需要回到 CodeAgent 目录
current_file = Path(__file__).resolve()
codeagent_dir = current_file.parent.parent.parent  # 从 test_simple.py 向上3级到 CodeAgent
sys.path.insert(0, str(codeagent_dir))

# 现在可以导入
from agents.test_generation_agent.agent import TestGenerationAgent


async def main():
    """最简单的测试：直接调用Agent，仅使用LLM生成"""
    
    print("="*60)
    print("TestGenerationAgent 简单测试")
    print("="*60)
    
    # 1. 创建Agent（不使用Docker，仅LLM）
    print("\n1. 创建Agent...")
    agent = TestGenerationAgent(config={
        "use_docker": False,  # 不使用Docker
        "use_llm": True,      # 使用LLM生成
        "use_pynguin": False, # 不使用Pynguin
        "use_evosuite": False # 不使用EvoSuite
    })
    
    # 2. 初始化
    print("2. 初始化Agent...")
    init_result = await agent.initialize()
    if not init_result:
        print("[ERROR] Agent初始化失败")
        return
    print("[OK] Agent初始化成功")
    
    # 3. 准备测试项目路径（替换为你的项目路径）
    project_path = "test_calculator"  # 替换为实际路径
    
    # 检查项目是否存在
    if not Path(project_path).exists():
        print(f"\n[ERROR] 项目路径不存在: {project_path}")
        print("\n请先创建测试项目：")
        print("""
mkdir test_calculator
cd test_calculator
cat > calculator.py << 'EOF'
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("除数不能为0")
    return a / b
EOF
        """)
        return
    
    print(f"\n3. 为项目 {project_path} 生成测试...")
    
    # 4. 生成测试
    result = await agent.process_task("test_task_001", {
        "project_path": project_path,
        "issues": [],  # 可选：问题列表
        "issue_description": "测试divide函数在除数为0时是否抛出异常"  # 可选
    })
    
    # 5. 打印结果
    print("\n" + "="*60)
    print("测试生成结果")
    print("="*60)
    print(f"[OK] 成功: {result['success']}")
    print(f"[INFO] 语言: {result.get('languages', [])}")
    print(f"[INFO] 测试目录: {result.get('tests_dir', 'N/A')}")
    print(f"[INFO] 测试文件数: {result.get('total_tests', 0)}")
    
    if result.get('results'):
        print("\n详细结果:")
        for lang, lang_result in result['results'].items():
            print(f"\n  {lang.upper()}:")
            print(f"    [OK] 成功: {lang_result.get('success', False)}")
            print(f"    [INFO] 测试文件数: {lang_result.get('total_tests', 0)}")
            print(f"    [INFO] 测试目录: {lang_result.get('tests_dir', 'N/A')}")
            
            if lang_result.get('generated_tests'):
                print(f"    [INFO] 生成的文件:")
                for test_file in lang_result['generated_tests']:
                    print(f"      - {test_file}")
            
            if lang_result.get('errors'):
                print(f"    [WARNING] 错误:")
                for error in lang_result['errors']:
                    print(f"      - {error}")
    
    if result.get('errors'):
        print(f"\n[WARNING] 全局错误:")
        for error in result['errors']:
            print(f"  - {error}")
    
    # 6. 验证生成的测试文件
    if result.get('success') and result.get('tests_dir'):
        tests_dir = Path(result['tests_dir'])
        if tests_dir.exists():
            # 查找所有测试文件（排除临时文件）
            all_test_files = list(tests_dir.glob("test_*.py"))
            # 过滤掉临时文件
            test_files = [f for f in all_test_files if "temp" not in f.name.lower()]
            
            print(f"\n[OK] 验证: 找到 {len(test_files)} 个测试文件")
            for test_file in test_files:
                print(f"  - {test_file.name}")
            
            # 显示测试文件内容预览
            if test_files:
                print(f"\n[INFO] 测试文件内容预览（{test_files[0].name}）:")
                print("-" * 60)
                try:
                    with open(test_files[0], 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 只显示前20行
                        lines = content.split('\n')[:20]
                        print('\n'.join(lines))
                        if len(content.split('\n')) > 20:
                            print("... (文件已截断)")
                except Exception as e:
                    print(f"无法读取文件: {e}")
                print("-" * 60)
            
            # 尝试运行测试（如果pytest可用）
            try:
                import subprocess
                import shutil
                # 检查pytest是否安装
                pytest_path = shutil.which("pytest")
                if not pytest_path:
                    # 尝试使用python -m pytest
                    pytest_path = shutil.which("python")
                    if pytest_path:
                        print("\n[INFO] 尝试运行测试（使用 python -m pytest）...")
                        # 使用绝对路径
                        tests_dir_abs = Path(tests_dir).absolute()
                        project_path_abs = Path(project_path).absolute()
                        result_run = subprocess.run(
                            [pytest_path, "-m", "pytest", str(tests_dir_abs), "-v"],
                            capture_output=True,
                            text=True,
                            timeout=30,
                            cwd=str(project_path_abs)
                        )
                        if result_run.returncode == 0:
                            print("[OK] 测试运行成功")
                            if result_run.stdout:
                                print(result_run.stdout[-500:])  # 显示最后500字符
                        else:
                            print("[WARNING] 测试运行有错误（这是正常的，生成的测试可能需要调整）")
                            if result_run.stderr:
                                print(f"错误信息: {result_run.stderr[:300]}")
                            if result_run.stdout:
                                print(f"输出: {result_run.stdout[-300:]}")
                    else:
                        print("\n[INFO] pytest未安装，跳过测试运行")
                        print("安装pytest: pip install pytest")
                else:
                    print("\n[INFO] 尝试运行测试...")
                    # 使用绝对路径
                    tests_dir_abs = Path(tests_dir).absolute()
                    project_path_abs = Path(project_path).absolute()
                    result_run = subprocess.run(
                        ["pytest", str(tests_dir_abs), "-v"],
                        capture_output=True,
                        text=True,
                        timeout=30,
                        cwd=str(project_path_abs)
                    )
                    if result_run.returncode == 0:
                        print("[OK] 测试运行成功")
                        if result_run.stdout:
                            print(result_run.stdout[-500:])  # 显示最后500字符
                    else:
                        print("[WARNING] 测试运行有错误（这是正常的，生成的测试可能需要调整）")
                        if result_run.stderr:
                            print(f"错误信息: {result_run.stderr[:300]}")
                        if result_run.stdout:
                            print(f"输出: {result_run.stdout[-300:]}")
            except FileNotFoundError:
                print("\n[INFO] pytest未安装，跳过测试运行")
                print("安装pytest: pip install pytest")
            except Exception as e:
                print(f"\n[WARNING] 无法运行测试: {e}")
                print(f"提示: 可以手动运行: cd {project_path} && pytest tests/ -v")


if __name__ == "__main__":
    asyncio.run(main())

