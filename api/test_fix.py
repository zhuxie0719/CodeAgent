import sys
sys.path.insert(0, r"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251119_134538_571467_1f92395f\flask-2.0.0\src")
try:
    from flask.json.tag import PassDict, TaggedJSONSerializer
    serializer = TaggedJSONSerializer()
    pass_dict = PassDict(serializer)
    print("PassDict has to_python method:", hasattr(pass_dict, "to_python"))
    print("Method signature:", getattr(pass_dict, "to_python", None))
    print("SUCCESS: to_python method exists in PassDict class")
except Exception as e:
    print("ERROR:", e)
