# CodeAgent 缓存清理脚本
# 用于清理系统运行过程中产生的临时文件和缓存

Write-Host "🧹 开始清理 CodeAgent 缓存和临时文件..." -ForegroundColor Cyan

$totalSize = 0

# 1. 清理项目解压临时目录
Write-Host "`n📁 清理临时解压目录..." -ForegroundColor Yellow
$tempExtractDirs = @(
    "temp_extract",
    "api\temp_extract"
)

foreach ($dir in $tempExtractDirs) {
    if (Test-Path $dir) {
        $size = (Get-ChildItem -Path $dir -Recurse -ErrorAction SilentlyContinue | 
                 Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
        if ($size) {
            $sizeMB = [math]::Round($size / 1MB, 2)
            Write-Host "  删除: $dir ($sizeMB MB)" -ForegroundColor Gray
            Remove-Item -Path $dir -Recurse -Force -ErrorAction SilentlyContinue
            $totalSize += $size
        }
    }
}

# 2. 清理预加载虚拟环境（可选，如果不需要缓存）
Write-Host "`n🐍 检查预加载虚拟环境..." -ForegroundColor Yellow
$venvPaths = @(
    "api\prebuilt_venvs",
    "$env:LOCALAPPDATA\CodeAgent\prebuilt_venvs"
)

foreach ($venvPath in $venvPaths) {
    if (Test-Path $venvPath) {
        $size = (Get-ChildItem -Path $venvPath -Recurse -ErrorAction SilentlyContinue | 
                 Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
        if ($size) {
            $sizeMB = [math]::Round($size / 1MB, 2)
            Write-Host "  发现: $venvPath ($sizeMB MB)" -ForegroundColor Gray
            $response = Read-Host "  是否删除预加载虚拟环境? (y/N)"
            if ($response -eq "y" -or $response -eq "Y") {
                Remove-Item -Path $venvPath -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "  已删除: $venvPath" -ForegroundColor Green
                $totalSize += $size
            } else {
                Write-Host "  保留: $venvPath" -ForegroundColor Gray
            }
        }
    }
}

# 3. 清理 Docker 缓存（可选）
Write-Host "`n🐳 检查 Docker 资源..." -ForegroundColor Yellow
try {
    $dockerImages = docker images --format "{{.Repository}}:{{.Tag}} {{.Size}}" 2>$null
    if ($dockerImages) {
        Write-Host "  当前 Docker 镜像:" -ForegroundColor Gray
        $dockerImages | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
        
        $response = Read-Host "`n  是否清理未使用的 Docker 镜像和缓存? (y/N)"
        if ($response -eq "y" -or $response -eq "Y") {
            Write-Host "  清理未使用的 Docker 镜像..." -ForegroundColor Gray
            docker image prune -f 2>$null
            Write-Host "  清理 Docker 构建缓存..." -ForegroundColor Gray
            docker builder prune -f 2>$null
            Write-Host "  ✅ Docker 缓存已清理" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "  ⚠️ Docker 命令执行失败（可能未安装 Docker）" -ForegroundColor Yellow
}

# 4. 清理 Python 缓存文件
Write-Host "`n🐍 清理 Python 缓存文件..." -ForegroundColor Yellow
$cachePatterns = @("__pycache__", "*.pyc", "*.pyo", ".pytest_cache", ".mypy_cache")
$found = $false

foreach ($pattern in $cachePatterns) {
    $files = Get-ChildItem -Path . -Recurse -Include $pattern -ErrorAction SilentlyContinue
    if ($files) {
        $size = ($files | Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
        if ($size) {
            $sizeMB = [math]::Round($size / 1MB, 2)
            Write-Host "  删除 $pattern 文件 ($sizeMB MB)" -ForegroundColor Gray
            $files | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
            $totalSize += $size
            $found = $true
        }
    }
}

if (-not $found) {
    Write-Host "  未发现 Python 缓存文件" -ForegroundColor Gray
}

# 5. 清理上传的临时文件（可选）
Write-Host "`n📦 检查上传临时文件..." -ForegroundColor Yellow
$uploadDirs = @("uploads", "api\uploads")
foreach ($dir in $uploadDirs) {
    if (Test-Path $dir) {
        $files = Get-ChildItem -Path $dir -File -ErrorAction SilentlyContinue
        if ($files) {
            $size = ($files | Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
            if ($size) {
                $sizeMB = [math]::Round($size / 1MB, 2)
                Write-Host "  发现: $dir ($sizeMB MB, $($files.Count) 个文件)" -ForegroundColor Gray
                $response = Read-Host "  是否清理上传文件? (y/N)"
                if ($response -eq "y" -or $response -eq "Y") {
                    $files | Remove-Item -Force -ErrorAction SilentlyContinue
                    Write-Host "  已清理: $dir" -ForegroundColor Green
                    $totalSize += $size
                }
            }
        }
    }
}

# 总结
Write-Host "`n✅ 清理完成！" -ForegroundColor Green
if ($totalSize -gt 0) {
    $totalMB = [math]::Round($totalSize / 1MB, 2)
    Write-Host "  释放空间: $totalMB MB" -ForegroundColor Cyan
} else {
    Write-Host "  未发现需要清理的文件" -ForegroundColor Gray
}

Write-Host "`n💡 提示: 可以定期运行此脚本清理缓存" -ForegroundColor Yellow

