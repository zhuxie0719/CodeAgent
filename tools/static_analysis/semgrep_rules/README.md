# Semgrep Flask 2.0.0 自定义规则

本目录包含用于检测 Flask 2.0.0 已知问题的 Semgrep 自定义规则。

## 规则文件

- `flask_2_0_0_issues.yml` - Flask 2.0.0 主要问题的检测规则

## 覆盖的问题

### S类问题（静态可检）

1. **蓝图命名约束** (#4041) - ERROR级别
   - 检测不安全的蓝图命名（空、None、以点开头、包含斜杠）

2. **蓝图URL前缀合并** (#4037) - WARNING级别
   - 检测多层蓝图URL前缀嵌套，可能未正确合并

3. **嵌套蓝图命名** (#4069) - WARNING级别
   - 检测嵌套蓝图缺少显式命名，可能导致端点冲突

4. **同名多次注册** (#1091, #4124) - ERROR级别
   - 检测同一蓝图被重复注册

### A类问题（静态可检部分）

5. **send_from_directory参数重命名** (#4019) - WARNING级别
   - 检测使用已弃用的 `filename` 参数

6. **Config.from_json误删** (#4078) - ERROR级别
   - 检测使用可能被误删的 `Config.from_json` 方法

7. **jsonify Decimal编码** (#4157) - WARNING级别
   - 检测可能使用 Decimal 类型的 jsonify

8. **CLI loader关键字参数** (#4170) - WARNING级别
   - 检测 CLI loader 使用 `create_app(**kwargs)`

9. **static_folder PathLike类型** (#4150) - WARNING级别
   - 检测使用 pathlib.Path 作为 static_folder

### 类型注解问题（信息提示）

10. **errorhandler装饰器类型** (#4295) - INFO级别
11. **before_request装饰器类型** (#4104) - INFO级别

## 使用方法

### 1. 在代码中配置

```python
# 在 agent.py 或配置文件中
semgrep_config = {
    "enabled": True,
    "rules_configs": ["python", "p/python"],
    "custom_rules": [
        "tools/static_analysis/semgrep_rules/flask_2_0_0_issues.yml"
    ]
}
```

### 2. 命令行使用

```bash
# 使用自定义规则
semgrep --config=tools/static_analysis/semgrep_rules/flask_2_0_0_issues.yml --config=python src/

# 或结合官方规则
semgrep --config=tools/static_analysis/semgrep_rules/flask_2_0_0_issues.yml --config=p/python src/
```

### 3. 在CI/CD中使用

```yaml
# .github/workflows/semgrep.yml
- name: Run Semgrep Flask Rules
  run: |
    semgrep --config=tools/static_analysis/semgrep_rules/flask_2_0_0_issues.yml \
            --config=p/python \
            --json \
            -o semgrep-results.json \
            src/
```

## 规则严重程度

- **ERROR**: 可能导致运行时错误或严重问题，建议立即修复
- **WARNING**: 可能导致不兼容或行为异常，建议在迁移前修复
- **INFO**: 类型相关提示，在严格类型模式下可能有影响

## 预期覆盖能力

- **S类问题**: 80-90%（蓝图相关问题、API参数问题）
- **A类问题（静态部分）**: 50-60%（参数使用、方法存在性检测）
- **类型问题**: 30-40%（主要通过mypy检测，规则仅提供提示）

## 规则维护

规则基于 Flask 2.0.1/2.0.2/2.0.3 的变更记录编写，对应以下GitHub Issues：

- #4019, #4024, #4026, #4037, #4041, #4044
- #4060, #4069, #4078, #4093, #4095, #4098
- #4104, #4112, #4124, #4150, #4157, #4170
- #4229, #4295, #4333

## 注意事项

1. 某些规则可能产生误报，特别是涉及动态值的情况
2. 建议结合 MyPy、Pylint 等其他工具一起使用
3. 对于复杂的嵌套蓝图场景，可能需要人工审查
4. 规则主要针对 Flask 2.0.0 基线版本的问题

## 贡献

如需添加新规则或改进现有规则，请参考：
- [Semgrep规则编写指南](https://semgrep.dev/docs/writing-rules/)
- [Flask版本选择与Issue策略文档](../docs/Flask版本选择与Issue策略.md)
