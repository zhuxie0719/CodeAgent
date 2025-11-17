#!/usr/bin/env python3
"""
在Python文件中运行fixcodeagent命令
"""
import subprocess
import sys
import os


def run_fixcodeagent():
    """运行fixcodeagent命令"""
    # 设置Windows环境下的编码
    if sys.platform == "win32":
        os.environ["PYTHONIOENCODING"] = "utf-8"
        os.environ["FIXCODE_SILENT_STARTUP"] = "1"
    
    # 准备命令参数
    task = "Fix the import error for flask module in conftest.py"
    cmd = [
        sys.executable,
        "-m",
        "fixcodeagent",
        "--task",
        task,
        "--yolo",
        "--exit-immediately"
    ]
    
    # 准备环境变量
    env = os.environ.copy()
    if sys.platform == "win32":
        env["PYTHONIOENCODING"] = "utf-8"
        env["FIXCODE_SILENT_STARTUP"] = "1"
    
    print(f"正在执行命令: {' '.join(cmd)}")
    print("-" * 50)
    
    # 运行命令
    try:
        process = subprocess.Popen(
            cmd,
            env=env
        )
        # 等待进程完成
        process.wait()
        print("-" * 50)
        print(f"命令执行完成，退出码: {process.returncode}")
    except KeyboardInterrupt:
        process.terminate()
        print("\n进程被用户中断。")
    except Exception as e:
        print(f"执行命令时出错: {e}")


if __name__ == "__main__":
    run_fixcodeagent()

