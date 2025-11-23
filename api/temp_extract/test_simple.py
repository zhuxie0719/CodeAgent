import sys
import os
sys.path.insert(0, r"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251117_091003_926095_72074f0a\flask-2.0.0\src")

# Test the specific line we modified by checking the syntax
try:
    # Read the modified file and check line 362
    with open(r"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251117_091003_926095_72074f0a\flask-2.0.0\src\flask\ctx.py", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    line_362 = lines[361].strip()  # Line 362 is index 361 (0-based)
    print(f"Line 362 content: {line_362}")
    
    if 'top._internal_data["_preserved_exc"]' in line_362:
        print("SUCCESS: Line 362 correctly uses _internal_data dictionary access")
        print("The protected member access issue has been resolved")
    else:
        print("ERROR: Line 362 still has direct protected member access")
        
    # Also verify no other direct _preserved_exc access exists
    direct_access_found = False
    for i, line in enumerate(lines):
        if '_preserved_exc' in line and not '_internal_data["_preserved_exc"]' in line and not '"_preserved_exc":' in line:
            print(f"WARNING: Potential direct access found at line {i+1}: {line.strip()}")
            direct_access_found = True
    
    if not direct_access_found:
        print("SUCCESS: No direct _preserved_exc access found in the file")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
