import requests

# 测试上传
files = {'file': ('test.py', 'def hello():\n    print("Hello")\n', 'text/plain')}
response = requests.post('http://localhost:8001/api/v1/detection/upload', files=files)
print(f'状态码: {response.status_code}')
print(f'响应: {response.text}')