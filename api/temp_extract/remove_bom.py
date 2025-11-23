# Remove BOM and fix encoding
with open(r"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251117_091003_926095_72074f0a\flask-2.0.0\src\flask\helpers.py", "r", encoding="utf-8-sig") as f:
    content = f.read()

with open(r"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251117_091003_926095_72074f0a\flask-2.0.0\src\flask\helpers.py", "w", encoding="utf-8") as f:
    f.write(content)

print("BOM removed and file saved with proper encoding")
