import subprocess
import sys

# Test the original pylint issue
result = subprocess.run([
    sys.executable, "-m", "pylint", 
    "--disable=all", 
    "--enable=import-outside-toplevel",
    "C:/Users/86138/Desktop/thisisfinal/CodeAgent/api/temp_extract/project_20251119_134538_571467_1f92395f/flask-2.0.0/src/flask/cli.py"
], capture_output=True, text=True)

print("Pylint output:")
print(result.stdout)
print("Return code:", result.returncode)
