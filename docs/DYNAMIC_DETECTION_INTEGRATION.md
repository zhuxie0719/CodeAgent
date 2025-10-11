# 动态检测功能集成说明

## 概述

已成功将 `start_dynamic_detection.py` 的功能整合到 `start_api.py` 中，实现了统一的启动方式。现在可以通过 `start_api.py` 启动包含动态检测功能的完整系统。

## 主要修改

### 1. 启动脚本统一 (`start_api.py`)
- ✅ 更新启动信息，包含动态检测界面地址
- ✅ 添加动态检测功能说明
- ✅ 统一通过端口 8001 启动所有功能

### 2. API层集成 (`api/main_api.py`)
- ✅ 挂载动态检测API路由 (`dynamic_api`)
- ✅ 添加动态检测相关端点信息
- ✅ 统一API前缀：`/api/dynamic`

### 3. 动态检测API (`api/dynamic_api.py`)
- ✅ 从FastAPI应用转换为APIRouter
- ✅ 更新所有端点路径，移除重复的`/api`前缀
- ✅ 修复导入路径问题

### 4. Agent层 (`agents/integrated_detector.py`)
- ✅ 修复导入路径问题
- ✅ 确保与现有组件的兼容性

### 5. 前端页面 (`frontend/dynamic_detection.html`)
- ✅ 更新API端点从 `localhost:8003` 到 `localhost:8001/api/dynamic`
- ✅ 更新API路径适配新的路由结构

## 功能特性

### 动态检测功能
- **静态分析**: 代码质量检查、安全问题检测
- **运行时分析**: 项目执行监控、错误检测
- **动态监控**: 系统资源监控、性能分析
- **综合报告**: 生成详细的检测报告和建议

### 支持的操作
- 上传项目压缩包 (ZIP格式)
- 自动解压缩项目
- 运行项目并监控执行过程
- 生成综合检测报告
- 下载检测结果

## 使用方法

### 1. 启动系统
```bash
python start_api.py
```

### 2. 访问服务
- **API文档**: http://localhost:8001/docs
- **主界面**: file://frontend/index.html
- **动态检测**: file://frontend/dynamic_detection.html
- **健康检查**: http://localhost:8001/health

### 3. 使用动态检测
1. 打开主界面 (`index.html`)
2. 选择"动态检测"功能
3. 上传项目ZIP文件
4. 选择检测选项（静态分析、动态监控、运行时分析）
5. 等待检测完成
6. 查看检测报告

## API端点

### 动态检测相关端点
- `POST /api/dynamic/detect` - 上传项目进行动态检测
- `GET /api/dynamic/status` - 获取检测状态
- `GET /api/dynamic/results/{filename}` - 获取检测结果
- `GET /api/dynamic/system-info` - 获取系统信息
- `POST /api/dynamic/test-monitor` - 测试监控功能
- `POST /api/dynamic/test-project-runner` - 测试项目运行器

## 测试验证

已通过完整测试验证以下功能：
- ✅ 集成检测器正常工作
- ✅ 项目解压缩功能正常
- ✅ 静态分析功能正常
- ✅ 运行时分析功能正常
- ✅ 报告生成功能正常
- ✅ API路由正确挂载
- ✅ 前端页面API调用正常
- ✅ API服务健康检查正常
- ✅ CORS配置正确
- ✅ 前端连接问题已修复

## 技术架构

```
start_api.py (统一启动)
├── api/main_api.py (主API服务)
│   ├── coordinator_api (协调中心)
│   ├── bug_detection_api (缺陷检测)
│   ├── code_quality_api (代码质量)
│   ├── code_analysis_api (代码分析)
│   └── dynamic_api (动态检测) ← 新增
│       ├── agents/integrated_detector.py
│       ├── agents/simple_monitor_agent.py
│       └── utils/project_runner.py
└── frontend/ (前端界面)
    ├── index.html (主界面)
    └── dynamic_detection.html (动态检测页面)
```

## 注意事项

1. **端口统一**: 所有功能现在通过端口 8001 提供服务
2. **文件格式**: 目前只支持ZIP格式的项目压缩包
3. **监控时间**: 默认监控60秒，可根据需要调整
4. **临时文件**: 系统会自动清理临时文件
5. **依赖要求**: 需要安装 `psutil` 用于系统监控

## 故障排除

### 常见问题
1. **端口占用**: 确保端口 8001 未被占用
2. **依赖缺失**: 运行 `pip install -r api/requirements.txt`
3. **文件权限**: 确保有创建临时文件的权限
4. **ZIP格式**: 确保上传的是有效的ZIP文件
5. **前端连接失败**: 确保API服务已启动 (`python start_api.py`)
6. **CORS错误**: 检查浏览器控制台，确保API服务正常运行

### 日志查看
- 启动日志会显示各组件状态
- API调用日志在控制台输出
- 检测过程日志实时显示

## 后续优化建议

1. **性能优化**: 减少监控时间，提高检测速度
2. **错误处理**: 增强错误处理和用户反馈
3. **结果存储**: 添加结果数据库存储
4. **批量处理**: 支持批量项目检测
5. **实时通知**: 添加WebSocket实时通知
6. **报告模板**: 支持自定义报告模板

---

**集成完成时间**: 2024年12月
**测试状态**: ✅ 通过
**功能状态**: ✅ 可用
