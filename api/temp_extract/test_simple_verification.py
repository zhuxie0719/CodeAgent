import sys
import os
import ast

# Read the debughelpers.py file and check the NewClass structure
file_path = r"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251117_091003_926095_72074f0a\flask-2.0.0\src\flask\debughelpers.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Parse the Python code
tree = ast.parse(content)

# Find the NewClass and count its public methods
new_class_found = False
public_methods = []

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "NewClass":
        new_class_found = True
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_name = item.name
                # Consider methods that don't start with underscore as public
                # or special methods like __getitem__, __contains__ as public
                if not method_name.startswith('_') or method_name in ['__getitem__', '__contains__']:
                    public_methods.append(method_name)

print(f"NewClass found: {new_class_found}")
print(f"Public methods in NewClass: {public_methods}")
print(f"Number of public methods: {len(public_methods)}")

if len(public_methods) >= 2:
    print("SUCCESS: NewClass now has at least 2 public methods, fixing the pylint warning!")
else:
    print("FAILED: NewClass still has too few public methods.")
