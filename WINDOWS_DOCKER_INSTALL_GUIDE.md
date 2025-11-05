# Windows Docker 安装指南

本指南详细介绍如何在 Windows 系统上安装 Docker Desktop，以便使用 CodeAgent 项目的 Docker 功能。

## 📋 系统要求

在开始安装之前，请确保您的 Windows 系统满足以下要求：

### 硬件要求
- **CPU**: 支持虚拟化的 64 位处理器（Intel/AMD）
- **内存**: 至少 4GB RAM（推荐 8GB 或更多）
- **磁盘空间**: 至少 10GB 可用空间

### 软件要求
- **Windows 版本**: 
  - Windows 10 64位：专业版、企业版或教育版（版本 1903 或更高，带 Build 18362 或更高）
  - Windows 11 64位：家庭版或专业版
  - Windows Server 2019 或更高版本
- **启用 Hyper-V 和容器功能**（Windows 10/11 专业版会自动启用）
- **启用虚拟化**（在 BIOS/UEFI 中）

## 🔍 检查系统是否支持

### 步骤 1: 检查 Windows 版本

1. 按 `Win + R` 打开运行对话框
2. 输入 `winver` 并回车
3. 查看 Windows 版本信息

### 步骤 2: 检查虚拟化是否启用

1. 按 `Ctrl + Shift + Esc` 打开任务管理器
2. 切换到"性能"标签页
3. 选择"CPU"
4. 查看右下角的"虚拟化"状态
   - ✅ **已启用**: 可以继续安装
   - ❌ **已禁用**: 需要进入 BIOS 启用虚拟化（见下方说明）

### 步骤 3: 检查 Hyper-V 是否可用（可选）

**重要**: 此命令需要管理员权限。

**以管理员身份打开 PowerShell**:
1. 按 `Win + X` 打开快捷菜单
2. 选择 "Windows PowerShell (管理员)" 或 "终端 (管理员)"
3. 如果出现用户账户控制（UAC）提示，点击"是"

**或者**:
1. 在开始菜单搜索 "PowerShell"
2. 右键点击 "Windows PowerShell"
3. 选择 "以管理员身份运行"
4. 如果出现用户账户控制（UAC）提示，点击"是"

然后在 PowerShell 中运行：

```powershell
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All
```

**可能的输出情况**:

1. **如果显示 `State : Enabled`**: 说明 Hyper-V 已启用 ✅
2. **如果显示 `State : Disabled`**: 说明 Hyper-V 未启用，但可以启用
3. **如果没有任何输出**: 可能的原因：
   - **Windows 10/11 家庭版不支持 Hyper-V**（这是最常见的原因）
   - Hyper-V 功能未安装
   - 系统版本较旧不支持

**替代检查方法**:

如果上述命令没有输出，可以尝试以下方法：

**方法 1: 检查 Windows 版本是否支持 Hyper-V**
```powershell
Get-WindowsEdition -Online
```
- 如果显示 `Edition : Core` 或 `Home`，说明不支持 Hyper-V
- 如果显示 `Professional`、`Enterprise` 或 `Education`，则支持 Hyper-V

**方法 2: 使用更详细的命令**
```powershell
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All | Format-List
```

**方法 3: 检查所有可选功能（查找 Hyper-V 相关）**
```powershell
Get-WindowsOptionalFeature -Online | Where-Object {$_.FeatureName -like "*Hyper*"}
```

**重要提示**:
- **Windows 10/11 家庭版不支持 Hyper-V**，但可以使用 **WSL 2** 来运行 Docker Desktop
- 即使没有 Hyper-V，Docker Desktop 也可以正常工作（使用 WSL 2 后端）
- 如果您使用的是家庭版，可以跳过 Hyper-V 检查，直接安装 Docker Desktop

**注意**: 如果您看到错误提示"请求的操作需要提升"，说明当前 PowerShell 没有管理员权限，请按照上述步骤以管理员身份重新打开 PowerShell。

## 📥 下载 Docker Desktop

1. **访问 Docker 官网**
   - 打开浏览器，访问：https://www.docker.com/products/docker-desktop/
   - 或者直接访问：https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe

2. **选择下载版本**
   - 点击 "Download for Windows" 按钮
   - 下载 `Docker Desktop Installer.exe`（约 500MB）

3. **备用下载地址**（如果官网下载慢）
   - 可以使用国内镜像源或使用下载工具

## 🚀 安装步骤

### 步骤 1: 运行安装程序

1. 双击下载的 `Docker Desktop Installer.exe`
2. 如果出现用户账户控制（UAC）提示，点击"是"
3. 等待安装程序启动

### 步骤 2: 配置安装选项

在安装向导中：

1. ✅ **勾选 "Use WSL 2 instead of Hyper-V"**（推荐）
   - 这是 Docker Desktop 推荐的配置方式
   - 如果您的系统不支持 WSL 2，会自动使用 Hyper-V

2. ✅ **勾选 "Add shortcut to desktop"**（可选）
   - 方便以后快速启动

3. 点击 **"OK"** 继续

### 步骤 3: 等待安装完成

1. 安装程序会自动：
   - 安装 Docker Desktop
   - 配置 WSL 2（如果选择了该选项）
   - 设置必要的系统组件

2. 安装时间：约 5-10 分钟（取决于系统性能）

3. 安装完成后，点击 **"Close and restart"** 重启电脑

### 步骤 4: 重启后启动 Docker Desktop

1. 电脑重启后，Docker Desktop 会自动启动
2. 如果没有自动启动，从开始菜单找到 "Docker Desktop" 并启动
3. 首次启动需要等待 Docker 引擎初始化（约 1-2 分钟）

### 步骤 5: 接受服务协议

1. Docker Desktop 启动后，会显示服务协议
2. 阅读并勾选 "I accept the terms"
3. 点击 **"Accept"**

### 步骤 6: 完成初始设置

1. 选择使用场景：
   - **个人使用**: 选择 "Personal"
   - **商业使用**: 选择 "Business"

2. 点击 **"Finish"** 完成设置

## ✅ 验证安装

### 方法 1: 使用命令行验证

1. 打开 PowerShell 或 CMD
2. 运行以下命令：

```powershell
docker --version
```

应该看到类似输出：
```
Docker version 24.0.0, build abc123
```

3. 运行：

```powershell
docker info
```

应该看到 Docker 系统信息，没有错误。

### 方法 2: 使用项目检查脚本

在项目根目录运行：

```powershell
python check_docker.py
```

如果看到 "Docker 可用" 或类似成功消息，说明安装成功。

### 方法 3: 运行测试容器

```powershell
docker run hello-world
```

如果看到 "Hello from Docker!" 消息，说明 Docker 工作正常。

## ⚙️ 配置 Docker Desktop

### 基本设置

1. 右键点击系统托盘中的 Docker 图标
2. 选择 "Settings"（设置）

### 推荐配置

1. **Resources（资源）**
   - **CPU**: 设置为可用 CPU 的 50-75%
   - **Memory**: 设置为至少 4GB（如果系统有 8GB 或更多）
   - **Disk**: 确保有足够的磁盘空间

2. **General（常规）**
   - ✅ 勾选 "Start Docker Desktop when you log in"（登录时自动启动）
   - ✅ 勾选 "Use the WSL 2 based engine"（如果可用）

3. **Docker Engine**
   - 可以配置镜像加速器（国内用户推荐）

### 配置国内镜像加速器（可选，推荐）

如果下载镜像速度慢，可以配置国内镜像源：

1. 打开 Docker Desktop Settings
2. 进入 "Docker Engine"
3. 在 JSON 配置中添加：

```json
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me",
    "https://dislabaiot.xyz",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

4. 点击 "Apply & Restart"

## ❌ 常见问题解决

### 问题 1: 虚拟化未启用

**症状**: 安装后 Docker Desktop 无法启动，提示虚拟化相关错误

**解决方案**:
1. 重启电脑，进入 BIOS/UEFI 设置
   - 通常按 `F2`、`F10`、`Del` 或 `Esc`（具体按键取决于主板）
2. 找到虚拟化相关选项（通常在 "Advanced" 或 "CPU Configuration" 中）
   - Intel CPU: 找到 "Intel Virtualization Technology (VT-x)" 并启用
   - AMD CPU: 找到 "AMD-V" 或 "SVM" 并启用
3. 保存设置并重启电脑

### 问题 2: 安装过程中提示需要更新 WSL

**症状**: 安装过程中出现以下提示：
```
适用于 Linux 的 Windows 子系统必须更新到最新版本才能继续。可通过运行 "wsl.exe --update" 进行更新。
按任意键安装适用于 Linux 的 Windows 子系统。
按 CTRL-C 或关闭此窗口以取消。
此提示将在 60 秒后超时。
```

**说明**:
- 这是正常现象，Docker Desktop 需要 WSL 2 作为后端
- 安装程序会自动更新 WSL 到最新版本
- 您只需要按任意键继续即可

**解决方案**:

**方法 1: 让安装程序自动更新（推荐）**
1. 在提示窗口中按任意键（如空格、回车等）
2. 等待安装程序自动更新 WSL
3. 更新完成后，安装程序会继续安装 Docker Desktop

**方法 2: 手动更新 WSL（如果自动更新失败）**
1. 按 `CTRL-C` 取消当前安装
2. 以管理员身份打开 PowerShell
3. 运行以下命令手动更新 WSL：
   ```powershell
   wsl.exe --update
   ```
4. 等待更新完成
5. 重新运行 Docker Desktop 安装程序

**方法 3: 完全手动安装 WSL 2（如果上述方法都失败）**

1. **以管理员身份运行 PowerShell**

2. **启用 WSL 功能**:
   ```powershell
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   ```

3. **启用虚拟机器平台**:
   ```powershell
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```

4. **重启电脑**

5. **重启后，安装 WSL 2 内核更新包**:
   - 下载: https://aka.ms/wsl2kernel
   - 安装下载的 MSI 文件

6. **设置 WSL 2 为默认版本**:
   ```powershell
   wsl --set-default-version 2
   ```

7. **验证 WSL 版本**:
   ```powershell
   wsl --version
   ```
   应该显示 WSL 版本为 2.x.x

8. **重新运行 Docker Desktop 安装程序**

### 问题 3: Docker Desktop 启动后立即退出

**症状**: Docker Desktop 启动后图标消失，无法正常运行

**解决方案**:
1. 检查 Windows 更新，确保系统是最新的
2. 以管理员身份运行 Docker Desktop
3. 检查防火墙设置，确保 Docker 未被阻止
4. 查看 Docker Desktop 日志：
   - 右键系统托盘 Docker 图标 → "Troubleshoot" → "View Logs"

### 问题 4: 提示 "WSL 2 installation is incomplete"

**解决方案**:
1. 下载并安装 WSL 2 内核更新包：
   - https://aka.ms/wsl2kernel
2. 重启电脑
3. 在 PowerShell 中运行：
   ```powershell
   wsl --set-default-version 2
   ```

### 问题 5: 权限不足

**症状**: 
- 运行 Docker 命令时提示权限错误
- 运行 `Get-WindowsOptionalFeature` 时提示"请求的操作需要提升"

**解决方案**:

**对于 PowerShell 命令**:
1. 关闭当前的 PowerShell 窗口
2. 以管理员身份重新打开 PowerShell:
   - 按 `Win + X` → 选择 "Windows PowerShell (管理员)"
   - 或：开始菜单搜索 "PowerShell" → 右键 → "以管理员身份运行"
3. 如果出现用户账户控制（UAC）提示，点击"是"
4. 重新运行命令

**对于 Docker 命令**:
1. 确保您是管理员组的成员
2. 以管理员身份运行 PowerShell/CMD
3. 检查 Docker Desktop 是否以管理员权限运行

### 问题 6: 网络连接问题

**症状**: 无法拉取镜像或连接 Docker Hub

**解决方案**:
1. 检查网络连接
2. 配置镜像加速器（见上方配置说明）
3. 检查代理设置（如果使用代理）

## 🔧 卸载 Docker Desktop

如果需要卸载 Docker Desktop：

1. 打开 "设置" → "应用" → "应用和功能"
2. 搜索 "Docker Desktop"
3. 点击 "卸载"
4. 按照提示完成卸载
5. 重启电脑（可选，但推荐）

## 📚 下一步

安装完成后，您可以：

1. **验证安装**:
   ```powershell
   python check_docker.py
   ```

2. **构建项目所需的 Docker 镜像**:
   ```powershell
   docker build -f Dockerfile.flask-test -t flask-2.0.0-test:latest .
   ```

3. **启动 CodeAgent 服务**:
   ```powershell
   $env:USE_DOCKER="true"
   python start_api.py
   ```

4. **查看详细使用指南**:
   - `DOCKER_QUICKSTART.md` - 快速开始
   - `DOCKER_SETUP_GUIDE.md` - 详细配置指南

## 📞 获取帮助

如果遇到问题：

1. **查看 Docker Desktop 日志**:
   - 右键系统托盘 Docker 图标 → "Troubleshoot" → "View Logs"

2. **检查项目文档**:
   - `DOCKER_SETUP_GUIDE.md` - 故障排查章节
   - `DOCKER_QUICKSTART.md` - 常见问题

3. **Docker 官方文档**:
   - https://docs.docker.com/desktop/install/windows-install/

4. **Docker 社区**:
   - Docker 官方论坛: https://forums.docker.com/
   - Stack Overflow: https://stackoverflow.com/questions/tagged/docker

## 🎉 安装完成！

恭喜！您已经成功安装了 Docker Desktop。现在可以开始使用 CodeAgent 的 Docker 功能了。

---

**提示**: Docker Desktop 首次启动和镜像下载可能需要一些时间，请耐心等待。使用过程中，确保 Docker Desktop 保持运行状态（系统托盘中有 Docker 图标）。

# Docker 网络问题快速修复指南

## 🔴 当前问题

构建 Docker 镜像时无法连接到 Docker Hub：
```
ERROR: failed to fetch oauth token: Post "https://auth.docker.io/token": 
connectex: A connection attempt failed
```

## ✅ 快速解决方案（3 步）

### 步骤 1: 配置镜像加速器（两种方式）

**方式 A: 绕过执行策略运行脚本（推荐）**

如果遇到"禁止运行脚本"错误，使用以下命令：

```powershell
powershell -ExecutionPolicy Bypass -File .\configure_docker_mirror.ps1
```

**方式 B: 直接手动配置（无需运行脚本）**

直接按照下面的步骤 2 进行配置，跳过脚本。

### 步骤 2: 在 Docker Desktop 中配置镜像加速器

1. **打开 Docker Desktop**
   - 右键系统托盘 Docker 图标 → "Settings"

2. **进入 Docker Engine**
   - 左侧菜单选择 "Docker Engine"

3. **添加配置**
   - 在 JSON 中找到或添加 `registry-mirrors` 字段
   - 复制以下配置：

```json
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me",
    "https://dislabaiot.xyz",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

4. **应用并重启**
   - 点击 "Apply & Restart"
   - 等待重启完成（约 30 秒）

### 步骤 3: 验证并重新构建

```powershell
# 验证配置
docker info | Select-String -Pattern "Registry Mirrors"

# 测试拉取镜像
docker pull python:3.9-slim

# 重新构建项目镜像
docker build -f Dockerfile.flask-test -t flask-2.0.0-test:latest .
```

## 🚀 如果还是不行

### 方案 A: 修改 Dockerfile 使用国内镜像源

编辑 `Dockerfile.flask-test`，将第 2 行改为：

```dockerfile
FROM registry.cn-hangzhou.aliyuncs.com/library/python:3.9-slim
```

### 方案 B: 临时禁用 Docker

```powershell
$env:USE_DOCKER="false"
python start_api.py
```

系统会自动使用虚拟环境方式运行。

## 📚 详细说明

查看 `DOCKER_NETWORK_FIX.md` 获取更多解决方案。

