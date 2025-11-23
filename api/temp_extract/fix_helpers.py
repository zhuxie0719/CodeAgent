import re

# Read the original file
with open(r"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251117_091003_926095_72074f0a\flask-2.0.0\src\flask\helpers.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the problematic function call
old_pattern = r'''    return werkzeug\.utils\.send_file\(\s*\*\*_prepare_send_file_kwargs\(\s*path_or_file=path_or_file,\s*environ=request\.environ,\s*mimetype=mimetype,\s*as_attachment=as_attachment,\s*download_name=download_name,\s*attachment_filename=attachment_filename,\s*conditional=conditional,\s*etag=etag,\s*add_etags=add_etags,\s*last_modified=last_modified,\s*max_age=max_age,\s*cache_timeout=cache_timeout,\s*\)\s*\)'''

new_code = '''    file_kwargs = {
        "path_or_file": path_or_file,
        "environ": request.environ,
        "mimetype": mimetype,
        "as_attachment": as_attachment,
        "attachment_filename": attachment_filename,
        "conditional": conditional,
        "add_etags": add_etags,
        "last_modified": last_modified,
        "cache_timeout": cache_timeout,
    }
    kwargs = _prepare_send_file_kwargs(
        download_name=download_name,
        etag=etag,
        max_age=max_age,
        **file_kwargs
    )
    return werkzeug.utils.send_file(**kwargs)'''

# Use regex to find and replace
content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)

# Write the modified content back
with open(r"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251117_091003_926095_72074f0a\flask-2.0.0\src\flask\helpers.py", "w", encoding="utf-8") as f:
    f.write(content)

print("File modified successfully")
