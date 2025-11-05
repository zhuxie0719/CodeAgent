# Flask 2.0.0 API测试示例

本文档提供API测试示例，用于测试各个bug的复现。

## 使用curl测试

### Bug #1: g类型提示
```bash
curl http://localhost:5000/bug1_g_type
```

### Bug #4, #6: send_file类型
```bash
curl http://localhost:5000/bug4_send_file_type
```

### Bug #7, #31: 蓝图URL前缀合并
```bash
curl http://localhost:5000/parent
curl http://localhost:5000/parent/child
curl http://localhost:5000/parent/child/grandchild
```

### Bug #9: send_from_directory
```bash
curl http://localhost:5000/bug9_send_from_directory
```

### Bug #10: Config.from_json
```bash
curl http://localhost:5000/bug10_config_json
```

### Bug #12, #32: 嵌套蓝图
```bash
curl http://localhost:5000/parent/child
```

### Bug #19: static_folder Path
```bash
curl http://localhost:5000/bug19_static_folder
```

### Bug #20: jsonify Decimal
```bash
curl http://localhost:5000/bug20_jsonify_decimal
```

### Bug #24, #28: 异步handler
```bash
curl http://localhost:5000/bug24_async
```

### Bug #25, #29: 回调顺序
```bash
curl http://localhost:5000/bug25_callback_order
```

### Bug #26, #30: 上下文边界
```bash
curl http://localhost:5000/bug26_context
```

### Bug #5, #17: 404错误处理
```bash
curl http://localhost:5000/unknown
```

## 使用Python requests测试

```python
import requests

BASE_URL = 'http://localhost:5000'

# Bug #1
response = requests.get(f'{BASE_URL}/bug1_g_type')
print(f"Bug #1: {response.status_code} - {response.text}")

# Bug #20 - 测试Decimal序列化
response = requests.get(f'{BASE_URL}/bug20_jsonify_decimal')
print(f"Bug #20: {response.status_code}")
print(f"JSON: {response.json()}")

# 测试嵌套蓝图
response = requests.get(f'{BASE_URL}/parent')
print(f"Bug #7: {response.status_code} - {response.text}")

response = requests.get(f'{BASE_URL}/parent/child')
print(f"Bug #12: {response.status_code} - {response.text}")

# 测试404处理
response = requests.get(f'{BASE_URL}/unknown')
print(f"Bug #5, #17: {response.status_code} - {response.text}")
```

## 预期行为对比

### Flask 2.0.0 (有bug的版本)
- Bug #1: g属性访问可能触发类型错误
- Bug #20: Decimal无法正确序列化为JSON，会抛出异常
- Bug #10: Config.from_json方法不存在
- Bug #24: 异步handler可能无法正常工作
- Bug #26: 在非请求上下文下使用after_this_request会报错

### Flask 2.0.1+ (修复后)
- Bug #1: g类型提示正确
- Bug #20: Decimal正确序列化为字符串
- Bug #10: Config.from_json方法恢复
- Bug #24: 异步handler正常工作
- Bug #26: 提供更好的错误信息



