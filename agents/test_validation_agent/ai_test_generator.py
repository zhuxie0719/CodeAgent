"""
AI测试生成器 - 使用DeepSeek API生成测试文件
与现有DeepSeek配置系统集成
"""
import os
import json
import asyncio
import aiohttp
from typing import Optional, Dict, Any
import logging
import sys

# 添加项目根目录到路径，以便导入现有配置
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from api.deepseek_config import deepseek_config
except ImportError:
    # 如果无法导入现有配置，使用默认配置
    deepseek_config = None

logger = logging.getLogger(__name__)

class AITestGenerator:
    """使用AI生成测试文件的生成器，与现有DeepSeek配置系统集成"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化AI测试生成器
        
        Args:
            api_key: DeepSeek API密钥，如果为None则使用现有配置
            base_url: API基础URL，如果为None则使用现有配置
        """
        # 优先使用现有配置，然后使用传入参数，最后使用环境变量
        if deepseek_config and deepseek_config.is_configured():
            self.api_key = api_key or deepseek_config.api_key
            self.base_url = base_url or deepseek_config.base_url
            self.model = deepseek_config.model
            self.max_tokens = deepseek_config.max_tokens
            self.temperature = deepseek_config.temperature
        else:
            # 回退到独立配置
            self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
            self.base_url = base_url or "https://api.deepseek.com/v1"
            self.model = "deepseek-coder"
            self.max_tokens = 4000
            self.temperature = 0.3
        
        if not self.api_key:
            logger.warning("未设置DEEPSEEK_API_KEY环境变量，AI测试生成功能将不可用")
    
    async def generate_test_file(self, source_file_path: str, project_path: str) -> Dict[str, Any]:
        """
        为源代码文件生成测试文件
        
        Args:
            source_file_path: 源代码文件路径
            project_path: 项目根路径
            
        Returns:
            包含生成结果的字典
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "未设置DEEPSEEK_API_KEY环境变量",
                "test_file_path": None
            }
        
        try:
            # 读取源代码文件
            source_content = await self._read_file(source_file_path)
            if not source_content:
                return {
                    "success": False,
                    "error": f"无法读取源代码文件: {source_file_path}",
                    "test_file_path": None
                }
            
            # 生成测试文件内容
            test_content = await self._call_ai_api(source_content, source_file_path)
            if not test_content:
                return {
                    "success": False,
                    "error": "AI生成测试内容失败",
                    "test_file_path": None
                }
            
            # 清理AI生成内容中的markdown标记
            test_content = self._clean_ai_content(test_content)
            
            # 确定测试文件路径
            test_file_path = self._get_test_file_path(source_file_path, project_path)
            
            # 写入测试文件
            await self._write_file(test_file_path, test_content)
            
            return {
                "success": True,
                "test_file_path": test_file_path,
                "test_content": test_content,
                "source_file": source_file_path
            }
            
        except Exception as e:
            logger.error(f"生成测试文件时发生错误: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_file_path": None
            }
    
    async def _read_file(self, file_path: str) -> Optional[str]:
        """异步读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            return None
    
    async def _write_file(self, file_path: str, content: str) -> bool:
        """异步写入文件内容"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"写入文件失败 {file_path}: {e}")
            return False
    
    def _get_test_file_path(self, source_file_path: str, project_path: str) -> str:
        """根据源代码文件路径生成测试文件路径"""
        # 获取相对于项目路径的文件名
        rel_path = os.path.relpath(source_file_path, project_path)
        
        # 如果是Python文件，生成对应的测试文件名
        if rel_path.endswith('.py'):
            # 移除.py扩展名，添加test_前缀
            base_name = os.path.basename(rel_path)[:-3]  # 移除.py
            if not base_name.startswith('test_'):
                test_name = f"test_{base_name}.py"
            else:
                test_name = f"{base_name}.py"
            
            # 构建测试文件路径 - 确保在正确的tests目录下
            test_dir = os.path.join(project_path, "tests")
            return os.path.join(test_dir, test_name)
        
        # 非Python文件，生成通用测试文件名
        base_name = os.path.basename(rel_path)
        test_name = f"test_{base_name}.py"
        test_dir = os.path.join(project_path, "tests")
        return os.path.join(test_dir, test_name)
    
    def _clean_ai_content(self, content: str) -> str:
        """清理AI生成内容中的markdown标记和其他格式问题"""
        if not content:
            return content
        
        # 移除开头的markdown代码块标记
        lines = content.split('\n')
        cleaned_lines = []
        
        # 跳过开头的markdown标记
        skip_start = False
        for line in lines:
            # 如果遇到```python或```标记，跳过
            if line.strip().startswith('```'):
                if not skip_start:
                    skip_start = True
                    continue
                else:
                    # 遇到结束标记，停止处理
                    break
            
            # 如果还没有开始跳过，但遇到了非空行，开始处理
            if not skip_start and line.strip():
                skip_start = True
            
            # 只有在开始跳过后才添加行
            if skip_start:
                cleaned_lines.append(line)
        
        # 移除结尾的markdown标记
        while cleaned_lines and cleaned_lines[-1].strip().startswith('```'):
            cleaned_lines.pop()
        
        # 移除末尾的空行
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    async def _call_ai_api(self, source_content: str, source_file_path: str) -> Optional[str]:
        """调用DeepSeek API生成测试内容"""
        try:
            # 构建提示词
            prompt = self._build_prompt(source_content, source_file_path)
            
            # 准备API请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的Python测试工程师，擅长编写高质量的单元测试。请根据提供的源代码生成完整的测试文件。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            # 发送API请求
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=120)  # 增加超时时间
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(f"API请求失败: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error(f"调用AI API时发生错误: {e}")
            return None
    
    def _build_prompt(self, source_content: str, source_file_path: str) -> str:
        """构建AI提示词"""
        filename = os.path.basename(source_file_path)
        module_name = filename[:-3] if filename.endswith('.py') else filename
        
        # 限制源代码长度，避免API调用超时
        if len(source_content) > 2000:
            source_content = source_content[:2000] + "\n# ... (代码已截断)"
        
        prompt = f"""为Python文件 {filename} 生成unittest测试：

{source_content}

要求：
1. 生成完整的Python测试文件
2. 测试所有函数，包含正常和异常情况
3. 只返回纯Python代码，不要包含任何markdown标记（如```python或```）
4. 确保代码语法正确，可以直接运行
5. 使用unittest框架
6. 包含必要的import语句

重要：模块导入设置
- 测试文件位于 tests/tests/ 目录下
- 被测试文件位于 tests/ 目录下
- 必须在文件开头添加以下导入路径设置：
```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import {module_name}
```

7. 环境变量测试注意事项：
- 如果测试环境变量，使用 os.getenv() 直接获取，不要依赖模块变量
- 例如：api_key = os.getenv("API_KEY", "") 而不是 module.API_KEY

8. 确保所有函数调用语法正确，避免重复调用如 ast.literal_ast.literal_ast.literal_eval

只返回Python代码，不要其他内容。"""
        return prompt.strip()

    async def cleanup_test_file(self, test_file_path: str) -> bool:
        """清理生成的测试文件"""
        try:
            if os.path.exists(test_file_path):
                os.remove(test_file_path)
                logger.info(f"已清理测试文件: {test_file_path}")
                return True
        except Exception as e:
            logger.error(f"清理测试文件失败 {test_file_path}: {e}")
        return False
