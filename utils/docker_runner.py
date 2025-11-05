"""
Docker运行器 - 用于在Docker容器中运行测试和检测
解决Windows下虚拟环境创建卡住的问题
"""

import os
import subprocess
import tempfile
import shutil
import json
import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DockerRunner:
    """Docker运行器，用于在容器中执行Python代码和测试"""
    
    def __init__(self, image_name: str = "flask-2.0.0-test:latest", 
                 container_prefix: str = "codeagent-test"):
        self.image_name = image_name
        self.container_prefix = container_prefix
        self.base_image_checked = False
    
    async def ensure_image_exists(self) -> bool:
        """确保Docker镜像存在，如果不存在则构建"""
        if self.base_image_checked:
            return True
        
        try:
            # 检查镜像是否存在
            result = subprocess.run(
                ["docker", "images", "-q", self.image_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                logger.info(f"Docker镜像 {self.image_name} 已存在")
                self.base_image_checked = True
                return True
            
            # 镜像不存在，尝试构建
            logger.info(f"Docker镜像 {self.image_name} 不存在，开始构建...")
            
            # 查找Dockerfile：先尝试当前目录，然后尝试项目根目录
            dockerfile_path = None
            tried_paths = []
            
            # 方法1: 当前工作目录
            current_dir = Path.cwd()
            dockerfile_path = current_dir / "Dockerfile.flask-test"
            tried_paths.append(str(dockerfile_path))
            
            if not dockerfile_path.exists():
                # 方法2: 从当前文件位置推断项目根目录
                # utils/docker_runner.py -> 项目根目录
                current_file = Path(__file__).resolve()
                project_root = current_file.parent.parent
                dockerfile_path = project_root / "Dockerfile.flask-test"
                tried_paths.append(str(dockerfile_path))
                
                if not dockerfile_path.exists():
                    # 方法3: 尝试从环境变量获取项目根目录
                    project_root_env = os.getenv("PROJECT_ROOT")
                    if project_root_env:
                        dockerfile_path = Path(project_root_env) / "Dockerfile.flask-test"
                        tried_paths.append(str(dockerfile_path))
            
            if not dockerfile_path or not dockerfile_path.exists():
                logger.error(f"Dockerfile Dockerfile.flask-test 不存在")
                logger.error(f"尝试过的路径: {', '.join(tried_paths)}")
                return False
            
            logger.info(f"找到Dockerfile: {dockerfile_path.absolute()}")
            
            # 构建镜像时，使用Dockerfile所在目录作为构建上下文
            build_result = await self._build_image(dockerfile_path)
            if build_result:
                self.base_image_checked = True
                logger.info(f"Docker镜像 {self.image_name} 构建成功")
            
            return build_result
            
        except FileNotFoundError:
            logger.error("Docker未安装或不在PATH中")
            return False
        except Exception as e:
            logger.error(f"检查Docker镜像时出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def _build_image(self, dockerfile_path: Path) -> bool:
        """构建Docker镜像"""
        try:
            # 使用Dockerfile所在目录作为构建上下文
            build_context = dockerfile_path.parent.absolute()
            
            cmd = [
                "docker", "build",
                "-f", str(dockerfile_path.absolute()),
                "-t", self.image_name,
                str(build_context)
            ]
            
            logger.info(f"执行构建命令: {' '.join(cmd)}")
            logger.info(f"构建上下文目录: {build_context}")
            
            # Windows上使用同步subprocess.run在后台线程中执行，其他平台使用异步create_subprocess_exec
            if sys.platform == 'win32':
                # Windows: 使用同步subprocess在后台线程中执行
                def run_build():
                    try:
                        result = subprocess.run(
                            cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            cwd=str(build_context),
                            timeout=600,  # 10分钟超时
                            text=False  # 返回bytes
                        )
                        return result.returncode, result.stdout, result.stderr
                    except subprocess.TimeoutExpired as e:
                        # 超時異常，返回錯誤碼和錯誤信息
                        logger.error(f"Docker構建超時: {e}")
                        return -1, b"", f"Docker構建超時: {e}".encode('utf-8')
                    except Exception as e:
                        # 其他異常，返回錯誤碼和錯誤信息
                        logger.error(f"Docker構建異常: {e}")
                        return -1, b"", f"Docker構建異常: {e}".encode('utf-8')
                
                loop = asyncio.get_event_loop()
                returncode, stdout, stderr = await asyncio.wait_for(
                    loop.run_in_executor(None, run_build),
                    timeout=600
                )
                
                # 檢查構建結果
                if returncode == 0:
                    logger.info("Docker镜像构建成功")
                    if stdout:
                        logger.debug(f"构建输出: {stdout.decode('utf-8', errors='replace')[:500]}")
                    return True
                else:
                    error_output = stderr.decode('utf-8', errors='replace') if stderr else ""
                    logger.error(f"Docker镜像构建失败 (返回碼: {returncode})")
                    if error_output:
                        logger.error(f"构建错误输出: {error_output[:1000]}")
                    if stdout:
                        logger.debug(f"构建标准输出: {stdout.decode('utf-8', errors='replace')[:500]}")
                    return False
            else:
                # Unix/Linux: 使用异步exec方式执行
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(build_context)
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=600  # 10分钟超时
                )
                returncode = process.returncode
                
                if returncode == 0:
                    logger.info("Docker镜像构建成功")
                    if stdout:
                        logger.debug(f"构建输出: {stdout.decode('utf-8', errors='replace')[:500]}")
                    return True
                else:
                    error_output = stderr.decode('utf-8', errors='replace')
                    logger.error(f"Docker镜像构建失败: {error_output}")
                    if stdout:
                        logger.debug(f"构建标准输出: {stdout.decode('utf-8', errors='replace')[:500]}")
                    return False
                
        except subprocess.TimeoutExpired:
            logger.error("Docker镜像构建超时")
            return False
        except asyncio.TimeoutError:
            logger.error("Docker镜像构建超时")
            return False
        except Exception as e:
            logger.error(f"构建Docker镜像时出错: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def run_command(self, 
                         project_path: Path,
                         command: List[str],
                         working_dir: Optional[str] = None,
                         timeout: int = 300,
                         environment: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """在Docker容器中运行命令
        
        Args:
            project_path: 项目路径（将被挂载到容器）
            command: 要执行的命令列表
            working_dir: 容器内的工作目录（可选）
            timeout: 超时时间（秒）
            environment: 环境变量字典（可选）
            
        Returns:
            包含执行结果的字典
        """
        try:
            # 确保镜像存在
            if not await self.ensure_image_exists():
                return {
                    "success": False,
                    "error": "Docker镜像不存在且构建失败",
                    "stdout": "",
                    "stderr": "",
                    "returncode": -1
                }
            
            # 确保项目路径存在
            project_path = Path(project_path)
            if not project_path.exists():
                logger.error(f"项目路径不存在: {project_path}")
                return {
                    "success": False,
                    "error": f"项目路径不存在: {project_path}",
                    "stdout": "",
                    "stderr": "",
                    "returncode": -1
                }
            
            # 确保项目路径是目录
            if not project_path.is_dir():
                logger.error(f"项目路径不是目录: {project_path}")
                return {
                    "success": False,
                    "error": f"项目路径不是目录: {project_path}",
                    "stdout": "",
                    "stderr": "",
                    "returncode": -1
                }
            
            # 生成唯一的容器名
            container_name = f"{self.container_prefix}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # 准备环境变量
            env_vars = []
            if environment:
                for key, value in environment.items():
                    env_vars.extend(["-e", f"{key}={value}"])
            
            # 构建docker run命令
            docker_cmd = [
                "docker", "run",
                "--rm",  # 自动删除容器
                "--name", container_name,
                "-v", f"{project_path.absolute()}:/app/test_project:ro",  # 只读挂载项目目录
            ] + env_vars + [
                self.image_name,
            ] + command
            
            logger.info(f"执行Docker命令: {' '.join(docker_cmd)}")
            logger.info(f"项目路径: {project_path.absolute()}")
            
            # 设置工作目录（如果命令不是sh -c格式，需要包装）
            if working_dir:
                # 如果命令已经是sh -c格式，需要在内部cd
                if len(command) >= 2 and command[0] == "sh" and command[1] == "-c":
                    # 命令已经是shell格式，在内部添加cd
                    original_cmd = command[2] if len(command) > 2 else ""
                    docker_cmd[-1] = f"cd {working_dir} && {original_cmd}"
                else:
                    # 命令不是shell格式，需要包装
                    cmd_str = " ".join(command)
                    docker_cmd[-len(command):] = ["sh", "-c", f"cd {working_dir} && {cmd_str}"]
            
            # Windows上使用同步subprocess.run在后台线程中执行，其他平台使用异步create_subprocess_exec
            if sys.platform == 'win32':
                # Windows: 使用同步subprocess在后台线程中执行
                def run_docker():
                    try:
                        result = subprocess.run(
                            docker_cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            timeout=timeout,
                            text=False  # 返回bytes
                        )
                        return result.returncode, result.stdout, result.stderr, None
                    except subprocess.TimeoutExpired:
                        return -1, b"", b"", "timeout"
                    except KeyboardInterrupt:
                        return -1, b"", "用户中断".encode('utf-8'), "interrupted"
                    except Exception as e:
                        return -1, b"", str(e).encode('utf-8'), "error"
                
                try:
                    loop = asyncio.get_event_loop()
                    returncode, stdout, stderr, error_type = await asyncio.wait_for(
                        loop.run_in_executor(None, run_docker),
                        timeout=timeout + 5  # 给一点缓冲时间
                    )
                    
                    # 如果发生错误，尝试停止容器
                    if error_type == "timeout" or error_type == "interrupted":
                        logger.warning(f"命令执行被中断或超时，尝试停止容器: {container_name}")
                        try:
                            subprocess.run(
                                ["docker", "stop", container_name],
                                timeout=10,
                                capture_output=True,
                                text=False
                            )
                        except Exception as e:
                            logger.warning(f"停止容器失败: {e}")
                    
                    # 构建错误信息
                    error_msg = None
                    stdout_text = stdout.decode('utf-8', errors='replace') if stdout else ""
                    stderr_text = stderr.decode('utf-8', errors='replace') if stderr else ""
                    
                    if error_type == "timeout":
                        error_msg = "命令执行超时"
                    elif error_type == "interrupted":
                        error_msg = "用户中断"
                    elif error_type == "error":
                        error_msg = stderr_text[:500] if stderr_text else "执行错误"
                    elif returncode != 0:
                        # 命令执行失败，使用 stderr 或 stdout 作为错误信息
                        # 某些命令可能将错误输出到stdout
                        if stderr_text:
                            error_msg = f"命令执行失败（返回码: {returncode}）: {stderr_text[:500]}"
                        elif stdout_text:
                            error_msg = f"命令执行失败（返回码: {returncode}）: {stdout_text[:500]}"
                        else:
                            error_msg = f"命令执行失败（返回码: {returncode}）"
                        
                        # 记录完整的输出用于调试
                        if stderr_text:
                            logger.error(f"Docker命令stderr: {stderr_text[:1000]}")
                        if stdout_text:
                            logger.debug(f"Docker命令stdout: {stdout_text[:1000]}")
                    
                    return {
                        "success": returncode == 0,
                        "stdout": stdout.decode('utf-8', errors='replace') if stdout else "",
                        "stderr": stderr.decode('utf-8', errors='replace') if stderr else "",
                        "returncode": returncode,
                        "container_name": container_name,
                        "error": error_msg
                    }
                except asyncio.TimeoutError:
                    # 超时，尝试停止容器
                    logger.warning(f"命令执行超时，尝试停止容器: {container_name}")
                    try:
                        subprocess.run(
                            ["docker", "stop", container_name],
                            timeout=10,
                            capture_output=True,
                            text=False
                        )
                    except Exception as e:
                        logger.warning(f"停止容器失败: {e}")
                    
                    return {
                        "success": False,
                        "error": f"命令执行超时（{timeout}秒）",
                        "stdout": "",
                        "stderr": "",
                        "returncode": -1
                    }
                except KeyboardInterrupt:
                    # 用户中断，尝试停止容器
                    logger.warning(f"用户中断，尝试停止容器: {container_name}")
                    try:
                        subprocess.run(
                            ["docker", "stop", container_name],
                            timeout=10,
                            capture_output=True,
                            text=False
                        )
                    except Exception:
                        pass
                    
                    return {
                        "success": False,
                        "error": "用户中断",
                        "stdout": "",
                        "stderr": "",
                        "returncode": -1
                    }
            else:
                # Unix/Linux: 使用异步exec方式执行
                process = await asyncio.create_subprocess_exec(
                    *docker_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=timeout
                    )
                    
                    stdout_text = stdout.decode('utf-8', errors='replace') if stdout else ""
                    stderr_text = stderr.decode('utf-8', errors='replace') if stderr else ""
                    returncode = process.returncode
                    
                    # 构建错误信息
                    error_msg = None
                    if returncode != 0:
                        if stderr_text:
                            error_msg = f"命令执行失败（返回码: {returncode}）: {stderr_text[:500]}"
                        elif stdout_text:
                            error_msg = f"命令执行失败（返回码: {returncode}）: {stdout_text[:500]}"
                        else:
                            error_msg = f"命令执行失败（返回码: {returncode}）"
                        
                        # 记录完整的输出用于调试
                        if stderr_text:
                            logger.error(f"Docker命令stderr: {stderr_text[:1000]}")
                        if stdout_text:
                            logger.debug(f"Docker命令stdout: {stdout_text[:1000]}")
                    
                    return {
                        "success": returncode == 0,
                        "stdout": stdout_text,
                        "stderr": stderr_text,
                        "returncode": returncode,
                        "container_name": container_name,
                        "error": error_msg
                    }
                except asyncio.TimeoutError:
                    # 超时，尝试停止容器
                    try:
                        subprocess.run(
                            ["docker", "stop", container_name],
                            timeout=10,
                            capture_output=True
                        )
                    except Exception:
                        pass
                    
                    return {
                        "success": False,
                        "error": f"命令执行超时（{timeout}秒）",
                        "stdout": "",
                        "stderr": "",
                        "returncode": -1
                    }
                
        except Exception as e:
            logger.error(f"运行Docker命令时出错: {e}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
                "returncode": -1
            }
    
    async def install_dependencies(self, project_path: Path, requirements_file: Optional[Path] = None) -> Dict[str, Any]:
        """在Docker容器中安装项目依赖"""
        try:
            # 递归查找requirements.txt
            if requirements_file is None or not requirements_file.exists():
                # 首先在项目根目录查找
                requirements_file = project_path / "requirements.txt"
                
                # 如果不存在，递归查找子目录
                if not requirements_file.exists():
                    for root, dirs, files in os.walk(project_path):
                        if "requirements.txt" in files:
                            requirements_file = Path(root) / "requirements.txt"
                            logger.info(f"在子目录找到requirements.txt: {requirements_file}")
                            break
            
            # 计算容器内的相对路径
            if requirements_file.exists():
                # 获取相对于project_path的路径
                try:
                    rel_path = requirements_file.relative_to(project_path)
                    # 使用as_posix()确保路径使用正斜杠（POSIX格式），适用于Docker容器
                    rel_path_posix = rel_path.as_posix()
                    container_req_path = f"/app/test_project/{rel_path_posix}"
                    # 获取requirements.txt所在的目录（容器内）
                    req_dir_posix = rel_path.parent.as_posix() if rel_path.parent != Path('.') else ""
                    container_req_dir = f"/app/test_project/{req_dir_posix}" if req_dir_posix else "/app/test_project"
                except ValueError:
                    # 如果不在project_path下，使用绝对路径的最后部分
                    container_req_path = f"/app/test_project/{requirements_file.name}"
                    container_req_dir = "/app/test_project"
                
                logger.info(f"使用requirements.txt: {requirements_file}")
                logger.info(f"容器内路径: {container_req_path}")
                logger.info(f"容器内工作目录: {container_req_dir}")
                
                # 直接安装requirements.txt中的依赖，让pip根据requirements.txt中的版本要求处理
                # 注意：使用2>&1将stderr重定向到stdout，所以错误信息会在stdout中
                install_cmd = [
                    "sh", "-c",
                    f"cd {container_req_dir} && "
                    f"pip install -r {container_req_path} --no-cache-dir 2>&1"
                ]
                
                logger.info(f"执行安装命令: {' '.join(install_cmd)}")
            else:
                # 没有requirements.txt，不安装任何依赖
                logger.warning("未找到requirements.txt，跳过依赖安装")
                return {
                    "success": True,
                    "message": "未找到requirements.txt，跳过依赖安装",
                    "stdout": "",
                    "stderr": "",
                    "returncode": 0
                }
            
            result = await self.run_command(
                project_path=project_path,
                command=install_cmd,
                timeout=600  # 10分钟超时
            )
            
            # 记录结果用于调试
            if result.get("success"):
                logger.info("依赖安装成功")
            else:
                logger.error(f"依赖安装失败: returncode={result.get('returncode')}")
                logger.error(f"错误信息: {result.get('error')}")
                logger.error(f"stdout: {result.get('stdout', '')[:1000]}")
                logger.error(f"stderr: {result.get('stderr', '')[:1000]}")
            
            return result
            
        except Exception as e:
            logger.error(f"安装依赖时出错: {e}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": ""
            }
    
    async def run_python_script(self, 
                               project_path: Path,
                               script_path: str,
                               args: Optional[List[str]] = None,
                               timeout: int = 300) -> Dict[str, Any]:
        """在Docker容器中运行Python脚本"""
        try:
            # 将脚本路径转换为POSIX格式（使用正斜杠），适用于Docker容器
            script_path_posix = script_path.replace("\\", "/")
            # 构建Python命令
            cmd = ["python", f"/app/test_project/{script_path_posix}"]
            if args:
                cmd.extend(args)
            
            result = await self.run_command(
                project_path=project_path,
                command=cmd,
                timeout=timeout
            )
            
            return result
            
        except Exception as e:
            logger.error(f"运行Python脚本时出错: {e}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": ""
            }
    
    async def run_tests(self, 
                       project_path: Path,
                       test_command: Optional[str] = None,
                       timeout: int = 600) -> Dict[str, Any]:
        """在Docker容器中运行测试"""
        try:
            if test_command is None:
                # 默认运行pytest
                cmd = ["sh", "-c", "cd /app/test_project && python -m pytest -v"]
            else:
                cmd = ["sh", "-c", f"cd /app/test_project && {test_command}"]
            
            result = await self.run_command(
                project_path=project_path,
                command=cmd,
                timeout=timeout
            )
            
            return result
            
        except Exception as e:
            logger.error(f"运行测试时出错: {e}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": ""
            }
    
    async def check_python_import(self, 
                                  project_path: Path,
                                  module_name: str) -> Dict[str, Any]:
        """检查Python模块是否可以导入"""
        try:
            cmd = [
                "python", "-c",
                f"import sys; sys.path.insert(0, '/app/test_project'); import {module_name}; print('Import successful')"
            ]
            
            result = await self.run_command(
                project_path=project_path,
                command=cmd,
                timeout=60
            )
            
            return result
            
        except Exception as e:
            logger.error(f"检查模块导入时出错: {e}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": ""
            }
    
    async def run_flask_app(self,
                           project_path: Path,
                           app_file: str = "app.py",
                           host: str = "0.0.0.0",
                           port: int = 5000,
                           timeout: int = 30) -> Dict[str, Any]:
        """在Docker容器中启动Flask应用（用于测试）"""
        try:
            # 使用后台运行并在指定时间后停止
            cmd = [
                "sh", "-c",
                f"cd /app/test_project && "
                f"timeout {timeout} python {app_file} || true"
            ]
            
            # 注意：这是一个简化版本，实际可能需要更复杂的端口映射
            result = await self.run_command(
                project_path=project_path,
                command=cmd,
                timeout=timeout + 10,
                environment={
                    "FLASK_APP": app_file,
                    "FLASK_ENV": "testing"
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"运行Flask应用时出错: {e}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": ""
            }


# 全局Docker运行器实例
_docker_runner: Optional[DockerRunner] = None


def get_docker_runner() -> DockerRunner:
    """获取全局Docker运行器实例"""
    global _docker_runner
    if _docker_runner is None:
        _docker_runner = DockerRunner()
    return _docker_runner

