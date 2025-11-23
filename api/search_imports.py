import os
import sys

def search_cryptography_imports():
    project_root = r'C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251119_134538_571467_1f92395f'
    
    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if 'cryptography' in content and ('ImportError' in content or 'BadParameter' in content):
                            print(f'Found in: {filepath}')
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if 'cryptography' in line or 'ImportError' in line or 'BadParameter' in line:
                                    print(f'  Line {i}: {line.strip()}')
                            print()
                except Exception as e:
                    continue

if __name__ == '__main__':
    search_cryptography_imports()
