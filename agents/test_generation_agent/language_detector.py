"""
语言检测器
检测项目使用的编程语言，复用BugDetectionAgent的检测逻辑
"""

import os
from pathlib import Path
from typing import List, Set
from enum import Enum


class Language(Enum):
    """支持的编程语言枚举"""
    PYTHON = "python"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    GO = "go"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    UNKNOWN = "unknown"


class LanguageDetector:
    """语言检测器 - 检测项目使用的编程语言"""
    
    # 文件扩展名到语言的映射
    EXTENSION_MAP = {
        ".py": Language.PYTHON,
        ".pyw": Language.PYTHON,
        ".pyi": Language.PYTHON,
        ".java": Language.JAVA,
        ".cpp": Language.CPP,
        ".cc": Language.CPP,
        ".cxx": Language.CPP,
        ".c": Language.C,
        ".h": Language.C,
        ".hpp": Language.CPP,
        ".hxx": Language.CPP,
        ".go": Language.GO,
        ".js": Language.JAVASCRIPT,
        ".jsx": Language.JAVASCRIPT,
        ".ts": Language.TYPESCRIPT,
        ".tsx": Language.TYPESCRIPT,
    }
    
    # 项目配置文件到语言的映射
    CONFIG_FILES = {
        "setup.py": Language.PYTHON,
        "pyproject.toml": Language.PYTHON,
        "requirements.txt": Language.PYTHON,
        "Pipfile": Language.PYTHON,
        "pom.xml": Language.JAVA,
        "build.gradle": Language.JAVA,
        "build.gradle.kts": Language.JAVA,
        "CMakeLists.txt": Language.CPP,
        "Makefile": Language.C,
        "go.mod": Language.GO,
        "go.sum": Language.GO,
        "package.json": Language.JAVASCRIPT,
        "tsconfig.json": Language.TYPESCRIPT,
    }
    
    def detect_languages(self, project_path: str) -> List[Language]:
        """
        检测项目使用的所有语言
        
        Args:
            project_path: 项目根路径
            
        Returns:
            检测到的语言列表
        """
        project = Path(project_path)
        if not project.exists():
            return [Language.UNKNOWN]
        
        detected = set()
        
        # 1. 检查配置文件（最准确的方法）
        for config_file, lang in self.CONFIG_FILES.items():
            if (project / config_file).exists():
                detected.add(lang)
        
        # 2. 扫描源代码文件（统计各语言文件数量）
        file_count_by_lang = {}
        for ext, lang in self.EXTENSION_MAP.items():
            count = len(list(project.rglob(f"*{ext}")))
            if count > 0:
                file_count_by_lang[lang] = file_count_by_lang.get(lang, 0) + count
                detected.add(lang)
        
        # 3. 如果通过配置文件检测到语言，优先使用配置文件的结果
        # 如果只通过文件扩展名检测到，也使用
        if detected:
            return list(detected)
        
        # 4. 如果都没有检测到，尝试基于文件内容的启发式检测
        return self._detect_by_content(project_path)
    
    def _detect_by_content(self, project_path: str) -> List[Language]:
        """
        基于文件内容的启发式检测（备用方法）
        复用BugDetectionAgent的检测逻辑
        """
        project = Path(project_path)
        detected = set()
        
        # 扫描前几个源文件，读取内容特征
        source_files = []
        for ext in [".py", ".java", ".cpp", ".c", ".go", ".js", ".ts"]:
            files = list(project.rglob(f"*{ext}"))[:3]  # 每个扩展名最多检查3个文件
            source_files.extend(files)
        
        for file_path in source_files[:10]:  # 最多检查10个文件
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(1024)  # 只读取前1KB
                    
                    # 基于内容特征检测（复用BugDetectionAgent的逻辑）
                    if "package " in content and "import " in content and "class " in content:
                        detected.add(Language.JAVA)
                    elif "#include" in content and ("int main" in content or "void main" in content):
                        detected.add(Language.C)
                    elif "#include" in content and ("std::" in content or "using namespace" in content):
                        detected.add(Language.CPP)
                    elif "def " in content or ("import " in content and "from " in content):
                        detected.add(Language.PYTHON)
                    elif "function " in content or "var " in content or "let " in content or "const " in content:
                        if "interface " in content or "type " in content:
                            detected.add(Language.TYPESCRIPT)
                        else:
                            detected.add(Language.JAVASCRIPT)
                    elif "package " in content and "func " in content:
                        detected.add(Language.GO)
            except Exception:
                continue
        
        return list(detected) if detected else [Language.UNKNOWN]
    
    def get_primary_language(self, project_path: str) -> Language:
        """
        获取项目的主要语言（文件数量最多的）
        
        Args:
            project_path: 项目根路径
            
        Returns:
            主要语言
        """
        languages = self.detect_languages(project_path)
        if not languages or languages == [Language.UNKNOWN]:
            return Language.UNKNOWN
        
        # 统计各语言的文件数量
        project = Path(project_path)
        lang_counts = {}
        
        for lang in languages:
            count = 0
            for ext, mapped_lang in self.EXTENSION_MAP.items():
                if mapped_lang == lang:
                    count += len(list(project.rglob(f"*{ext}")))
            lang_counts[lang] = count
        
        # 返回文件数量最多的语言
        if lang_counts:
            return max(lang_counts.items(), key=lambda x: x[1])[0]
        
        return languages[0] if languages else Language.UNKNOWN

