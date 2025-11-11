# Buggy Project (Simple)

A minimal Python project with intentionally introduced bugs to exercise the generic detection rules.

## Files and intended issues

- `app.py`
  - Unsafe request params: `request.args["id"]`
  - Dynamic execution: `eval(...)`
  - Unsafe file read with user input path
  - Division by zero handling with empty except
  - Unvalidated file upload
- `utils.py`
  - `yaml.load`, `pickle.loads`, `json.loads`
  - File opened without closing
  - Recursion without base case
  - Division by zero
- `concurrency.py`
  - Thread race on shared counter
- `async_bug.py`
  - Missing `await` in async function
- `boundary.py`
  - Loop boundary off-by-one
- `config.py`
  - Missing env default
  - Timezone-naive `datetime.now()`
- `sockets.py`
  - Socket not closed
- `xml_issue.py`
  - Direct `ET.parse` on external input
- `exceptions.py`
  - Broad and empty except

## Quick start

This project is not intended to run. It just needs to be scanned by the agent.

1. Zip the folder:
   - On Windows: right-click `examples/buggy_project_simple/` -> Send to -> Compressed (zipped) folder.
2. Upload the zip in the frontend to trigger the detection workflow.
3. Inspect the detected issues and severity in the results.

## Optional (if you want to run Flask demo)

```bash
pip install flask pyyaml
python examples/buggy_project_simple/app.py
```

Then open:
- http://127.0.0.1:5000/user?id=../../etc/passwd&data=__import__('os').system('echo pwned')  (dangerous; for demo only)


