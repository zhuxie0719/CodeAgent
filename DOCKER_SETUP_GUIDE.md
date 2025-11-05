# Docker 配置指南

本指南说明如何使用 Docker 来解决 Windows 环境下虚拟环境创建卡住的问题。

## 问题背景

在 Windows 环境下，使用 Python 虚拟环境（venv）安装依赖时可能会遇到以下问题：
- 虚拟环境创建过程卡住
- 依赖安装超时
- 文件锁定问题
- Flask 2.0.0 和 Werkzeug 版本兼容性问题

使用 Docker 可以完全隔离这些问题，提供一个干净、可靠的测试环境。

## 前置要求

1. **安装 Docker Desktop** (Windows)
   - 下载地址：https://www.docker.com/products/docker-desktop/
   - 安装后确保 Docker Desktop 正在运行
   - 验证安装：在命令行运行 `docker --version`

2. **确保 Docker 服务运行**
   ```bash
   docker info
   ```

## 快速开始

### 1. 构建 Docker 镜像

首次使用或更新依赖后，需要构建镜像：

```bash
docker build -f Dockerfile.flask-test -t flask-2.0.0-test:latest .
```

构建时间约 2-5 分钟，取决于网络速度。

### 2. 启用 Docker 支持

有两种方式启用 Docker 支持：

#### 方式一：环境变量（推荐）

设置环境变量 `USE_DOCKER=true`：

**Windows (PowerShell):**
```powershell
$env:USE_DOCKER="true"
python start_api.py
```

**Windows (CMD):**
```cmd
set USE_DOCKER=true
python start_api.py
```

**Linux/Mac:**
```bash
export USE_DOCKER=true
python start_api.py
```

#### 方式二：修改代码配置

编辑 `api/comprehensive_detection_api.py`，修改第 65 行：

```python
use_docker = os.getenv("USE_DOCKER", "true").lower() == "true"  # 默认启用
```

### 3. 使用 docker-compose（可选）

如果使用 docker-compose，可以运行：

```bash
docker-compose -f docker-compose.flask-test.yml up -d
```

## 使用流程

1. **前端上传测试包**
   - 上传包含 `requirements.txt` 的 ZIP 压缩包
   - 系统会自动检测并使用 Docker 安装依赖

2. **系统自动处理**
   - 自动检测 `requirements.txt`
   - 在 Docker 容器中安装 Flask 2.0.0 和兼容依赖
   - 执行静态和动态检测

3. **查看结果**
   - 检测结果会返回给前端
   - 日志会显示 Docker 执行情况

## Docker 镜像内容

Docker 镜像 `flask-2.0.0-test:latest` 包含：

- Python 3.9
- Flask 2.0.0
- Werkzeug 2.0.0
- 兼容依赖包：
  - click >= 8.0
  - itsdangerous >= 2.0
  - Jinja2 >= 3.0
  - MarkupSafe >= 2.0
  - httpx >= 0.27, < 0.28
  - pytest >= 7.0
  - pytest-asyncio >= 0.21

## 故障排查

### 问题1: Docker 未安装或未运行

**错误信息:**
```
无法初始化Docker运行器: [WinError 2] 系统找不到指定的文件
```

**解决方案:**
1. 安装 Docker Desktop
2. 确保 Docker Desktop 正在运行
3. 运行 `docker info` 验证

### 问题2: 镜像构建失败

**错误信息:**
```
Docker镜像构建失败: ...
```

**解决方案:**
1. 检查网络连接
2. 清理旧的构建缓存：`docker system prune -a`
3. 重新构建镜像

### 问题3: 容器运行超时

**错误信息:**
```
命令执行超时（300秒）
```

**解决方案:**
1. 检查 Docker 资源限制（Docker Desktop -> Settings -> Resources）
2. 增加超时时间（修改 `utils/docker_runner.py` 中的 `timeout` 参数）

### 问题4: 权限问题

**Windows 特定问题:**
- 确保 Docker Desktop 有足够权限
- 以管理员身份运行 Docker Desktop

## 性能优化

1. **使用镜像缓存**
   - 首次构建后，后续构建会使用缓存，速度更快

2. **并行处理**
   - Docker 容器是独立的，可以并行运行多个检测任务

3. **资源限制**
   - 在 Docker Desktop 中设置合理的 CPU 和内存限制

## 回退到虚拟环境

如果 Docker 不可用或遇到问题，系统会自动回退到虚拟环境方式：

```python
# 手动禁用 Docker
export USE_DOCKER=false
```

或者在代码中：
```python
use_docker = False  # 禁用 Docker
```

## 测试 Docker 配置

运行测试脚本验证 Docker 配置：

```bash
python -c "
import asyncio
from utils.docker_runner import get_docker_runner

async def test():
    runner = get_docker_runner()
    if await runner.ensure_image_exists():
        print('✅ Docker 镜像可用')
        result = await runner.run_command(
            project_path=Path('.'),
            command=['python', '--version'],
            timeout=30
        )
        print(f'测试结果: {result}')
    else:
        print('❌ Docker 镜像不可用')

asyncio.run(test())
"
```

## 相关文件

- `Dockerfile.flask-test`: Docker 镜像定义
- `docker-compose.flask-test.yml`: Docker Compose 配置
- `utils/docker_runner.py`: Docker 运行器实现
- `agents/bug_detection_agent/agent.py`: Agent 的 Docker 支持

## 注意事项

1. **首次使用**: 首次构建镜像和运行容器需要较长时间，请耐心等待
2. **网络要求**: Docker 构建和运行需要网络连接以下载依赖
3. **资源消耗**: Docker 容器会消耗一定的系统资源（CPU、内存、磁盘）
4. **数据持久化**: 检测结果会保存到本地，Docker 容器删除不影响数据

## 技术支持

如遇到问题，请检查：
1. Docker Desktop 日志
2. 系统日志（Windows 事件查看器）
3. 代码日志输出









# Docker 镜像源配置指南

## 问题
Docker 无法拉取基础镜像，显示 "authorization failed" 错误。

## 解决方案：配置 Docker Desktop 镜像源

### 方法 1：通过 Docker Desktop 图形界面配置（推荐）

1. **打开 Docker Desktop**
   - 点击系统托盘中的 Docker 图标
   - 或从开始菜单打开 Docker Desktop

2. **进入设置**
   - 点击右上角的 ⚙️ **Settings**（设置）图标
   - 或点击菜单栏的 **Settings**

3. **配置镜像源**
   - 在左侧菜单中，点击 **Docker Engine**
   - 在右侧的 JSON 配置编辑器中，找到或添加 `registry-mirrors` 配置
   - 将以下配置复制粘贴到配置框中：

```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me",
    "https://dislabaiot.xyz",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

4. **应用配置**
   - 点击右上角的 **Apply & Restart**（应用并重启）
   - 等待 Docker Desktop 重启完成

5. **验证配置**
   - 打开 PowerShell 或命令提示符
   - 运行以下命令验证：
   ```powershell
   docker info | Select-String -Pattern "Registry Mirrors"
   ```
   - 应该能看到镜像源地址列表

### 方法 2：手动编辑配置文件（如果方法 1 不工作）

1. **关闭 Docker Desktop**
   - 右键点击系统托盘中的 Docker 图标
   - 选择 **Quit Docker Desktop**

2. **找到配置文件**
   - 配置文件位置：`%APPDATA%\Docker\settings.json`
   - 或直接在文件浏览器中输入：`C:\Users\你的用户名\AppData\Roaming\Docker\settings.json`

3. **编辑配置文件**
   - 用文本编辑器（如记事本、VS Code）打开 `settings.json`
   - 找到 `registryMirrors` 字段（如果不存在则添加）
   - 添加以下内容：

```json
{
  "registryMirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me",
    "https://dislabaiot.xyz",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

4. **保存并重启 Docker Desktop**
   - 保存文件
   - 重新打开 Docker Desktop

### 方法 3：使用代理或 VPN（如果镜像源不可用）

如果镜像源配置后仍然无法拉取镜像，可能需要：
1. 使用 VPN 连接
2. 配置 HTTP/HTTPS 代理

## 验证配置

配置完成后，运行以下命令验证：

```powershell
# 检查镜像源配置
docker info | Select-String -Pattern "Registry Mirrors"

# 测试拉取镜像
docker pull python:3.9-slim

# 如果成功，继续构建
docker build -f Dockerfile.flask-test -t flask-2.0.0-test:latest .
```

## 可用的国内镜像源

- **毫秒镜像**: `https://docker.1ms.run` ✅ 推荐
- **轩辕镜像**: `https://docker.xuanyuan.me` ✅ 推荐
- **dislabaiot**: `https://dislabaiot.xyz` ✅ 推荐
- **网易镜像**: `https://hub-mirror.c.163.com`
- **百度云镜像**: `https://mirror.baidubce.com`

## 故障排除

### 问题 1：配置后仍然无法拉取
- 确保 Docker Desktop 已完全重启
- 检查网络连接
- 尝试使用不同的镜像源

### 问题 2：配置文件格式错误
- 确保 JSON 格式正确（注意逗号和引号）
- 可以使用在线 JSON 验证器检查格式

### 问题 3：权限问题
- 确保以管理员身份运行 Docker Desktop
- 检查防火墙设置

## 下一步

配置完成后，重新运行构建命令：
```powershell
docker build -f Dockerfile.flask-test -t flask-2.0.0-test:latest .
```

# Docker 网络连接问题解决方案

## 问题描述

构建 Docker 镜像时出现以下错误：
```
ERROR: failed to build: failed to solve: failed to fetch oauth token: 
Post "https://auth.docker.io/token": dial tcp ... connectex: 
A connection attempt failed because the connected party did not properly respond
```

这通常是因为无法连接到 Docker Hub（网络问题或访问受限）。

## 解决方案

### 方案 1: 配置 Docker 镜像加速器（推荐）

#### Windows Docker Desktop 配置

1. **打开 Docker Desktop 设置**
   - 右键点击系统托盘中的 Docker 图标
   - 选择 "Settings"（设置）

2. **进入 Docker Engine 配置**
   - 在左侧菜单选择 "Docker Engine"

3. **添加镜像加速器配置**
   - 在 JSON 配置中添加或修改 `registry-mirrors` 字段：

```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com",
    "https://dockerhub.azk8s.cn"
  ]
}
```

4. **应用并重启**
   - 点击 "Apply & Restart" 按钮
   - 等待 Docker Desktop 重启完成

5. **验证配置**
   ```powershell
   docker info
   ```
   应该能看到 `Registry Mirrors` 配置

#### 验证镜像加速器是否生效

```powershell
# 测试拉取镜像
docker pull python:3.9-slim
```

如果配置成功，应该能正常下载镜像。

### 方案 2: 使用代理（如果已配置代理）

如果您的网络环境使用代理，需要在 Docker Desktop 中配置代理：

1. **打开 Docker Desktop 设置**
   - Settings → Resources → Proxies

2. **配置代理**
   - 选择 "Manual proxy configuration"
   - 填写代理服务器地址和端口
   - 如果需要认证，填写用户名和密码

3. **应用并重启**

### 方案 3: 使用国内镜像源替换基础镜像

如果镜像加速器仍然无法使用，可以修改 Dockerfile 使用国内镜像源：

#### 修改 Dockerfile.flask-test

将：
```dockerfile
FROM python:3.9-slim
```

改为使用国内镜像源之一：
```dockerfile
# 使用阿里云镜像
FROM registry.cn-hangzhou.aliyuncs.com/library/python:3.9-slim

# 或使用中科大镜像
# FROM docker.mirrors.ustc.edu.cn/library/python:3.9-slim
```

### 方案 4: 手动下载并导入镜像

如果以上方法都不行，可以：

1. **在其他网络环境下载镜像**
   - 使用 VPN 或切换到其他网络
   - 运行：`docker pull python:3.9-slim`
   - 导出镜像：`docker save python:3.9-slim -o python-3.9-slim.tar`

2. **导入镜像**
   ```powershell
   docker load -i python-3.9-slim.tar
   ```

3. **重新构建**
   ```powershell
   docker build -f Dockerfile.flask-test -t flask-2.0.0-test:latest .
   ```

## 快速配置脚本

### 运行配置脚本

**如果遇到 PowerShell 执行策略错误：**

使用以下命令绕过执行策略运行脚本：

```powershell
powershell -ExecutionPolicy Bypass -File .\configure_docker_mirror.ps1
```

或者临时更改当前会话的执行策略：

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\configure_docker_mirror.ps1
```

### Windows PowerShell 脚本（自动配置镜像加速器）

已创建文件 `configure_docker_mirror.ps1`：

```powershell
# 配置 Docker Desktop 镜像加速器
$configPath = "$env:APPDATA\Docker\settings.json"

# 检查 Docker Desktop 是否运行
$dockerRunning = docker info 2>&1 | Select-String -Pattern "Server Version"
if (-not $dockerRunning) {
    Write-Host "错误: Docker Desktop 未运行，请先启动 Docker Desktop" -ForegroundColor Red
    exit 1
}

Write-Host "正在配置 Docker 镜像加速器..." -ForegroundColor Yellow

# 注意：这需要手动编辑 settings.json，因为 Docker Desktop 需要重启才能生效
Write-Host ""
Write-Host "请按照以下步骤手动配置:" -ForegroundColor Cyan
Write-Host "1. 右键点击系统托盘中的 Docker 图标" -ForegroundColor White
Write-Host "2. 选择 'Settings'（设置）" -ForegroundColor White
Write-Host "3. 进入 'Docker Engine'" -ForegroundColor White
Write-Host "4. 添加以下配置到 JSON 中:" -ForegroundColor White
Write-Host ""
Write-Host '  "registry-mirrors": [' -ForegroundColor Green
Write-Host '    "https://docker.mirrors.ustc.edu.cn",' -ForegroundColor Green
Write-Host '    "https://hub-mirror.c.163.com",' -ForegroundColor Green
Write-Host '    "https://mirror.baidubce.com"' -ForegroundColor Green
Write-Host '  ]' -ForegroundColor Green
Write-Host ""
Write-Host "5. 点击 'Apply & Restart'" -ForegroundColor White
```

## 验证修复

配置完成后，重新构建镜像：

```powershell
docker build -f Dockerfile.flask-test -t flask-2.0.0-test:latest .
```

如果看到镜像开始下载并构建，说明配置成功。

## 仍然无法解决？

如果以上方法都不行：

1. **检查网络连接**
   ```powershell
   # 测试网络连接
   ping docker.io
   ping auth.docker.io
   ```

2. **检查防火墙设置**
   - 确保防火墙允许 Docker Desktop 访问网络

3. **使用 VPN 或更换网络**
   - 临时使用 VPN 或切换到其他网络环境

4. **联系网络管理员**
   - 如果是企业网络，可能需要网络管理员配置代理或白名单

## 临时解决方案：禁用 Docker

如果暂时无法解决网络问题，可以禁用 Docker 模式，使用虚拟环境：

```powershell
# 不设置 USE_DOCKER 环境变量，或设置为 false
$env:USE_DOCKER="false"
python start_api.py
```

系统会自动回退到虚拟环境方式运行。

{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me",
    "https://dislabaiot.xyz",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}