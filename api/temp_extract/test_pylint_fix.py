import sys
import os
sys.path.insert(0, r"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251117_091003_926095_72074f0a\flask-2.0.0\src")
import subprocess

# Run pylint on the helpers.py file to check if the issue is fixed
result = subprocess.run([
    'pylint', 
    r'C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251117_091003_926095_72074f0a\flask-2.0.0\src\flask\helpers.py',
    '--disable=all',
    '--enable=too-many-arguments'
], capture_output=True, text=True)

print("Pylint output:")
print(result.stdout)
print(result.stderr)

# Check if the specific error is gone
if "too-many-arguments" not in result.stdout:
    print("SUCCESS: The 'too-many-arguments' issue has been fixed!")
else:
    print("FAILED: The 'too-many-arguments' issue still exists.")
