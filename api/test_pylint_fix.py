import subprocess
import sys

# Run pylint on the helpers.py file
result = subprocess.run([
    sys.executable, "-m", "pylint", 
    "C:/Users/86138/Desktop/thisisfinal/CodeAgent/api/temp_extract/project_20251117_091003_926095_72074f0a/flask-2.0.0/src/flask/helpers.py"
], capture_output=True, text=True)

# Check if the specific warning about redefining 'type' is present
if "Redefining built-in 'type'" in result.stdout:
    print("FAILED: The pylint warning about redefining 'type' still exists")
    print(result.stdout)
else:
    print("SUCCESS: The pylint warning about redefining 'type' has been fixed")
    if result.returncode != 0:
        print("Other pylint warnings/errors:")
        print(result.stdout)
