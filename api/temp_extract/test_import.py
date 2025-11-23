import sys
sys.path.insert(0, r"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251117_091003_926095_72074f0a\flask-2.0.0\src")
try:
    from flask.helpers import LockedCachedProperty
    print("SUCCESS: LockedCachedProperty class imported successfully")
    print(f"Class name: {LockedCachedProperty.__name__}")
except Exception as e:
    print(f"ERROR: {e}")
