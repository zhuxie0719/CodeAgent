import sys
try:
    with open(r'C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251119_134538_571467_1f92395f\flask-2.0.0\src\flask\cli.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i in range(819, 830):
            if i < len(lines):
                print(f"{i+1}: {lines[i].rstrip()}")
except Exception as e:
    print(f"Error: {e}")
