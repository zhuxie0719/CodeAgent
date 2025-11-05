# CodeAgent 缓存清理指南

## ✅ 构建成功确认

从终端输出可以看到，Docker 镜像构建成功：
- **镜像名称**: `flask-2.0.0-test:latest`
- **镜像大小**: 506MB
- **状态**: ✅ 构建完成

## 🗑️ 系统产生的缓存文件位置

系统运行时会自动产生以下缓存和临时文件：

### 1. **项目解压临时目录** ⚠️ 主要占用空间
```
项目根目录/
├── temp_extract/              # 每次上传项目都会创建新的目录
│   └── project_YYYYMMDD_HHMMSS/
│       ├── venv/              # 每个项目的虚拟环境（可能很大）
│       └── [项目文件]
└── api/
    └── temp_extract/          # API 目录下的临时解压目录
```

**特点**:
- 每次上传项目都会创建新的时间戳目录
- 不会自动删除，需要手动清理
- 每个项目的 `venv/` 可能占用 100-500MB

### 2. **预加载虚拟环境**（可选保留）
```
Windows: %LOCALAPPDATA%\CodeAgent\prebuilt_venvs\flask_simple_test_venv
项目目录: api\prebuilt_venvs\flask_simple_test_venv
```

**特点**:
- 用于加速 `flask_simple_test` 项目的运行
- 如果不需要可以删除，系统会自动重新创建
- 大小约 100-200MB

### 3. **Docker 镜像和缓存**
```
Docker 镜像: flask-2.0.0-test:latest (506MB)
Docker 构建缓存: 可能占用几 GB
```

**特点**:
- Docker 镜像可以保留（用于运行测试）
- 构建缓存可以清理，不影响已构建的镜像

### 4. **Python 缓存文件**
```
__pycache__/          # Python 字节码缓存
*.pyc                 # 编译后的 Python 文件
.pytest_cache/        # pytest 缓存
.mypy_cache/          # mypy 缓存
```

**特点**:
- 占用空间较小
- 删除后会自动重新生成

## 🧹 清理方法

### 方法一：使用自动清理脚本（推荐）

运行 PowerShell 清理脚本：

```powershell
.\cleanup_cache.ps1
```

脚本会：
- ✅ 自动清理 `temp_extract/` 目录
- ✅ 询问是否清理预加载虚拟环境
- ✅ 询问是否清理 Docker 缓存
- ✅ 清理 Python 缓存文件
- ✅ 显示释放的空间大小

### 方法二：手动清理

#### 1. 清理临时解压目录

```powershell
# 删除项目根目录下的临时解压目录
Remove-Item -Path "temp_extract" -Recurse -Force

# 删除 API 目录下的临时解压目录
Remove-Item -Path "api\temp_extract" -Recurse -Force
```

#### 2. 清理预加载虚拟环境（可选）

```powershell
# 删除项目目录下的预加载虚拟环境
Remove-Item -Path "api\prebuilt_venvs" -Recurse -Force

# 删除系统缓存目录下的预加载虚拟环境
Remove-Item -Path "$env:LOCALAPPDATA\CodeAgent\prebuilt_venvs" -Recurse -Force
```

#### 3. 清理 Docker 缓存

```powershell
# 清理未使用的 Docker 镜像
docker image prune -f

# 清理 Docker 构建缓存（可能释放几 GB）
docker builder prune -f

# 如果要删除 flask-2.0.0-test 镜像（不推荐，除非确定不再使用）
docker rmi flask-2.0.0-test:latest
```

#### 4. 清理 Python 缓存

```powershell
# 清理所有 __pycache__ 目录
Get-ChildItem -Path . -Recurse -Include "__pycache__" | Remove-Item -Recurse -Force

# 清理所有 .pyc 文件
Get-ChildItem -Path . -Recurse -Include "*.pyc" | Remove-Item -Force
```

## 📊 清理频率建议

| 文件类型 | 清理频率 | 是否必须保留 |
|---------|---------|------------|
| `temp_extract/` | **每次检测后** | ❌ 不需要 |
| 预加载虚拟环境 | 偶尔（几周一次） | ⚠️ 可选，保留可加速 |
| Docker 镜像 | 很少（几个月） | ✅ 建议保留 |
| Docker 构建缓存 | 每月 | ❌ 不需要 |
| Python 缓存 | 每次检测后 | ❌ 不需要 |

## ⚠️ 注意事项

1. **不要删除正在使用的文件**
   - 如果系统正在运行，不要删除正在使用的项目目录
   - 建议在系统空闲时清理

2. **预加载虚拟环境**
   - 删除后系统会自动重新创建，但首次创建需要时间
   - 如果经常测试 `flask_simple_test`，建议保留

3. **Docker 镜像**
   - `flask-2.0.0-test:latest` 镜像建议保留
   - 删除后需要重新构建（约 2-5 分钟）

4. **自动清理（未来功能）**
   - 可以考虑添加定时清理任务
   - 或者添加检测完成后自动清理的选项

## 🔍 检查磁盘占用

查看各目录占用空间：

```powershell
# 查看 temp_extract 目录大小
Get-ChildItem -Path "temp_extract" -Recurse -ErrorAction SilentlyContinue | 
    Measure-Object -Property Length -Sum | 
    Select-Object @{Name="Size(MB)";Expression={[math]::Round($_.Sum / 1MB, 2)}}

# 查看 Docker 镜像大小
docker images

# 查看 Docker 磁盘使用情况
docker system df
```

## 💡 快速清理命令（一键清理）

如果确定要清理所有临时文件：

```powershell
# 清理所有临时解压目录
Remove-Item -Path "temp_extract", "api\temp_extract" -Recurse -Force -ErrorAction SilentlyContinue

# 清理 Python 缓存
Get-ChildItem -Path . -Recurse -Include "__pycache__", "*.pyc" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# 清理 Docker 构建缓存（保留镜像）
docker builder prune -f
```

## 📝 总结

**当前状态**:
- ✅ Docker 镜像构建成功（506MB）
- ⚠️ `temp_extract/` 目录可能占用大量空间（建议定期清理）
- ⚠️ 预加载虚拟环境可以保留（加速测试）

**建议操作**:
1. 运行 `.\cleanup_cache.ps1` 清理临时文件
2. 保留 Docker 镜像（用于运行测试）
3. 定期清理 `temp_extract/` 目录（每次检测后）

