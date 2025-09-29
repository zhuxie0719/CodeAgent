import os
import subprocess
from typing import Dict, Any

class CodeFixer:
    """多语言代码格式化修复器"""
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    async def fix_python(self, file: str, project_path: str) -> Dict[str, Any]:
        try:
            file_path = os.path.join(project_path, file)
            subprocess.run(["autoflake", "--in-place", "--remove-unused-variables", file_path], check=True)
            subprocess.run(["isort", file_path], check=True)
            subprocess.run(["black", file_path], check=True)
            return {"success": True, "changes": [f"Python文件已自动修复: {file_path}"], "message": "autoflake + isort + black 修复成功"}
        except Exception as e:
            return {"success": False, "changes": [], "message": f"Python修复失败: {e}"}

    async def fix_javascript(self, file: str, project_path: str) -> Dict[str, Any]:
        try:
            file_path = os.path.join(project_path, file)
            subprocess.run(["eslint", "--fix", file_path], check=True)
            subprocess.run(["prettier", "--write", file_path], check=True)
            return {"success": True, "changes": [f"JavaScript文件已格式化: {file_path}"], "message": "eslint + prettier 格式化成功"}
        except Exception as e:
            return {"success": False, "changes": [], "message": f"JavaScript格式化失败: {e}"}

    async def fix_java(self, file: str, project_path: str) -> Dict[str, Any]:
        try:
            file_path = os.path.join(project_path, file)
            subprocess.run(["google-java-format", "-i", file_path], check=True)
            return {"success": True, "changes": [f"Java文件已格式化: {file_path}"], "message": "google-java-format 格式化成功"}
        except Exception as e:
            return {"success": False, "changes": [], "message": f"Java格式化失败: {e}"}

    async def fix_cpp(self, file: str, project_path: str) -> Dict[str, Any]:
        try:
            file_path = os.path.join(project_path, file)
            subprocess.run(["clang-format", "-i", file_path], check=True)
            return {"success": True, "changes": [f"C/C++文件已格式化: {file_path}"], "message": "clang-format 格式化成功"}
        except Exception as e:
            return {"success": False, "changes": [], "message": f"C/C++格式化失败: {e}"}

    async def fix_go(self, file: str, project_path: str) -> Dict[str, Any]:
        try:
            file_path = os.path.join(project_path, file)
            subprocess.run(["gofmt", "-w", file_path], check=True)
            subprocess.run(["goimports", "-w", file_path], check=True)
            return {"success": True, "changes": [f"Go文件已格式化: {file_path}"], "message": "gofmt + goimports 格式化成功"}
        except Exception as e:
            return {"success": False, "changes": [], "message": f"Go格式化失败: {e}"}
