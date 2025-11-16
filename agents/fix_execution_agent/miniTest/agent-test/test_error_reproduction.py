# Test script to reproduce the average calculation error
import os
file_path = r"C:\Users\86138\Desktop\白白\模式设计\大作业\CodeAgent\agents\fix_execution_agent\miniTest\error.py"
try:
    with open(file_path, "r") as f:
        code = f.read()
    exec(code)
    print("Script executed successfully!")
except Exception as e:
    print(f"Error occurred: {e}")
    print(f"Error type: {type(e).__name__}")
