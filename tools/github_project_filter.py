"""
智能文件过滤器
用于GitHub开源项目的文件过滤和分类
"""

import os
import re
from typing import Dict, List, Set, Tuple
from pathlib import Path

class GitHubProjectFilter:
    """GitHub开源项目智能过滤器"""
    
    def __init__(self):
        # 环境文件和目录模式
        self.environment_patterns = {
            # Python环境
            'python': {
                'dirs': {
                    '__pycache__', '*.pyc', '*.pyo', '*.pyd', '.pytest_cache',
                    '.mypy_cache', '.coverage', 'htmlcov', '.tox', '.venv',
                    'venv', 'env', '.env', 'node_modules', '.git', '.svn',
                    '.hg', '.bzr', 'build', 'dist', '*.egg-info', '.eggs'
                },
                'files': {
                    '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.dylib',
                    '*.exe', '*.bin', '*.log', '*.tmp', '*.temp', '*.cache',
                    '*.pid', '*.lock', '*.swp', '*.swo', '*~', '.DS_Store',
                    'Thumbs.db', 'desktop.ini', '.coverage', '.pytest_cache',
                    'coverage.xml', 'htmlcov', '.tox', '.mypy_cache'
                },
                'extensions': {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib', '.exe'}
            },
            
            # JavaScript/Node.js环境
            'javascript': {
                'dirs': {
                    'node_modules', '.npm', '.yarn', 'dist', 'build', 'coverage',
                    '.nyc_output', '.next', '.nuxt', 'out', '.cache', '.parcel-cache'
                },
                'files': {
                    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
                    '*.log', '*.tmp', '*.cache', '.DS_Store', 'Thumbs.db'
                },
                'extensions': {'.log', '.tmp', '.cache'}
            },
            
            # Java环境
            'java': {
                'dirs': {
                    'target', 'build', 'out', '.gradle', '.mvn', 'bin',
                    '.classpath', '.project', '.settings'
                },
                'files': {
                    '*.class', '*.jar', '*.war', '*.ear', '*.log', '*.tmp',
                    '.DS_Store', 'Thumbs.db'
                },
                'extensions': {'.class', '.jar', '.war', '.ear', '.log', '.tmp'}
            },
            
            # C/C++环境
            'cpp': {
                'dirs': {
                    'build', 'bin', 'obj', 'Debug', 'Release', '.vs', '.vscode',
                    'CMakeFiles', 'cmake-build-*'
                },
                'files': {
                    '*.o', '*.obj', '*.exe', '*.dll', '*.so', '*.dylib',
                    '*.log', '*.tmp', '.DS_Store', 'Thumbs.db'
                },
                'extensions': {'.o', '.obj', '.exe', '.dll', '.so', '.dylib', '.log', '.tmp'}
            },
            
            # 通用环境文件
            'common': {
                'dirs': {
                    '.git', '.svn', '.hg', '.bzr', '.idea', '.vscode', '.vs',
                    'logs', 'log', 'tmp', 'temp', 'cache', '.cache', 'backup',
                    'backups', 'old', 'archive', 'archives'
                },
                'files': {
                    '.gitignore', '.gitattributes', '.gitmodules', '.gitkeep',
                    '.dockerignore', '.eslintignore', '.prettierignore',
                    '*.log', '*.tmp', '*.temp', '*.cache', '*.pid', '*.lock',
                    '.DS_Store', 'Thumbs.db', 'desktop.ini', '.directory'
                },
                'extensions': {'.log', '.tmp', '.temp', '.cache', '.pid', '.lock'}
            }
        }
        
        # 第三方库和框架模式
        self.third_party_patterns = {
            # Python第三方库
            'python_libs': {
                'dirs': {
                    'site-packages', 'lib', 'lib64', 'include', 'share',
                    'django', 'flask', 'requests', 'numpy', 'pandas', 'matplotlib',
                    'scipy', 'sklearn', 'tensorflow', 'torch', 'keras', 'pytorch',
                    'opencv', 'pillow', 'beautifulsoup4', 'selenium', 'scrapy'
                },
                'files': {
                    'requirements.txt', 'setup.py', 'setup.cfg', 'pyproject.toml',
                    'Pipfile', 'Pipfile.lock', 'poetry.lock', 'environment.yml'
                }
            },
            
            # JavaScript第三方库
            'javascript_libs': {
                'dirs': {
                    'node_modules', 'bower_components', 'vendor', 'libs',
                    'jquery', 'react', 'vue', 'angular', 'bootstrap', 'lodash',
                    'moment', 'axios', 'express', 'koa', 'next', 'nuxt'
                },
                'files': {
                    'package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
                    'bower.json', 'composer.json', 'webpack.config.js', 'gulpfile.js'
                }
            },
            
            # Java第三方库
            'java_libs': {
                'dirs': {
                    'lib', 'libs', 'jars', 'maven', 'gradle', 'ivy',
                    'spring', 'hibernate', 'apache', 'commons', 'guava'
                },
                'files': {
                    'pom.xml', 'build.gradle', 'gradle.properties', 'ivy.xml',
                    'Mavenfile', 'build.xml'
                }
            }
        }
        
        # 项目配置文件模式
        self.config_patterns = {
            'config_files': {
                '.env', '.env.local', '.env.development', '.env.production',
                'config.json', 'config.yaml', 'config.yml', 'settings.py',
                'settings.json', 'app.config', 'web.config', 'application.properties',
                'application.yml', 'application.yaml', 'babel.config.js',
                'jest.config.js', 'karma.conf.js', 'protractor.conf.js',
                'tsconfig.json', 'jsconfig.json', 'eslintrc.js', '.eslintrc.json',
                'prettierrc', '.prettierrc.json', 'editorconfig', '.editorconfig',
                'gitignore', '.gitignore', 'dockerignore', '.dockerignore',
                'dockerfile', 'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml'
            }
        }
        
        # 文档和资源文件模式
        self.documentation_patterns = {
            'docs': {
                'dirs': {
                    'docs', 'documentation', 'doc', 'wiki', 'help', 'manual',
                    'guides', 'tutorials', 'examples', 'samples', 'demo'
                },
                'files': {
                    'README.md', 'README.rst', 'README.txt', 'README',
                    'CHANGELOG.md', 'CHANGELOG.rst', 'CHANGELOG.txt', 'CHANGELOG',
                    'LICENSE', 'LICENSE.md', 'LICENSE.txt', 'COPYING',
                    'AUTHORS', 'CONTRIBUTORS', 'CONTRIBUTING.md', 'CONTRIBUTING.rst',
                    'CONTRIBUTING.txt', 'CONTRIBUTING', 'CODE_OF_CONDUCT.md',
                    'SECURITY.md', 'SUPPORT.md', 'MAINTAINERS', 'MAINTAINERS.md'
                },
                'extensions': {'.md', '.rst', '.txt', '.pdf', '.doc', '.docx'}
            },
            
            'assets': {
                'dirs': {
                    'assets', 'static', 'public', 'resources', 'media', 'images',
                    'img', 'icons', 'fonts', 'css', 'styles', 'js', 'scripts'
                },
                'files': {
                    '*.png', '*.jpg', '*.jpeg', '*.gif', '*.svg', '*.ico',
                    '*.css', '*.scss', '*.sass', '*.less', '*.styl',
                    '*.js', '*.jsx', '*.ts', '*.tsx', '*.vue', '*.svelte'
                },
                'extensions': {
                    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp',
                    '.css', '.scss', '.sass', '.less', '.styl',
                    '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte'
                }
            }
        }
    
    def detect_project_type(self, project_path: str) -> str:
        """检测项目类型"""
        indicators = {
            'python': 0,
            'javascript': 0,
            'java': 0,
            'cpp': 0,
            'go': 0,
            'rust': 0,
            'php': 0,
            'ruby': 0,
            'csharp': 0
        }
        
        # 检查关键文件
        key_files = {
            'python': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile'],
            'javascript': ['package.json', 'yarn.lock', 'pnpm-lock.yaml'],
            'java': ['pom.xml', 'build.gradle', 'gradle.properties'],
            'cpp': ['CMakeLists.txt', 'Makefile', 'configure', 'autogen.sh'],
            'go': ['go.mod', 'go.sum', 'Gopkg.toml'],
            'rust': ['Cargo.toml', 'Cargo.lock'],
            'php': ['composer.json', 'composer.lock'],
            'ruby': ['Gemfile', 'Gemfile.lock', 'Rakefile'],
            'csharp': ['*.csproj', '*.sln', 'packages.config']
        }
        
        # 检查文件扩展名
        extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx'],
            'java': ['.java'],
            'cpp': ['.c', '.cpp', '.cc', '.cxx', '.h', '.hpp'],
            'go': ['.go'],
            'rust': ['.rs'],
            'php': ['.php'],
            'ruby': ['.rb'],
            'csharp': ['.cs']
        }
        
        try:
            for root, dirs, files in os.walk(project_path):
                # 检查关键文件
                for file in files:
                    for lang, key_file_list in key_files.items():
                        if any(file == key_file or file.endswith(key_file.replace('*', '')) 
                               for key_file in key_file_list):
                            indicators[lang] += 2
                
                # 检查文件扩展名
                for file in files:
                    for lang, ext_list in extensions.items():
                        if any(file.endswith(ext) for ext in ext_list):
                            indicators[lang] += 1
                
                # 限制遍历深度，避免在大型项目中消耗过多时间
                if len(root.split(os.sep)) - len(project_path.split(os.sep)) > 3:
                    dirs.clear()
        
        except Exception as e:
            print(f"检测项目类型时出错: {e}")
        
        # 返回得分最高的语言
        if indicators:
            return max(indicators, key=indicators.get)
        return 'unknown'
    
    def should_analyze_file(self, file_path: str, project_type: str = 'unknown') -> Tuple[bool, str]:
        """
        判断文件是否应该被分析
        
        Returns:
            (should_analyze, reason)
        """
        file_path = file_path.replace('\\', '/')
        file_name = os.path.basename(file_path)
        file_dir = os.path.dirname(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # 优先检查：是否为源码目录下的文件（应该保留）
        # 源码目录模式：src/, lib/（但不是第三方库安装位置）
        if self._is_source_directory_file(file_path, project_type):
            # 即使是源码目录，也要检查环境文件和文档
            if self._is_environment_file(file_path, file_name, file_dir, file_ext, project_type):
                return False, "环境文件"
            if self._is_documentation_file(file_path, file_name, file_ext):
                return False, "文档文件"
            if self._is_asset_file(file_path, file_name, file_ext):
                return False, "资源文件"
            # 源码目录下的源代码文件应该分析
            if file_ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb', '.cs']:
                return True, "源码目录下的源代码文件"
        
        # 检查环境文件
        if self._is_environment_file(file_path, file_name, file_dir, file_ext, project_type):
            return False, "环境文件"
        
        # 检查第三方库（排除源码目录）
        if self._is_third_party_file(file_path, file_name, file_dir, project_type):
            return False, "第三方库文件"
        
        # 检查配置文件
        if self._is_config_file(file_name, file_ext):
            return False, "配置文件"
        
        # 检查文档文件
        if self._is_documentation_file(file_path, file_name, file_ext):
            return False, "文档文件"
        
        # 检查资源文件
        if self._is_asset_file(file_path, file_name, file_ext):
            return False, "资源文件"
        
        return True, "源代码文件"
    
    def _is_environment_file(self, file_path: str, file_name: str, file_dir: str, 
                           file_ext: str, project_type: str) -> bool:
        """检查是否为环境文件"""
        # 检查通用环境模式
        for pattern_type, patterns in self.environment_patterns.items():
            if pattern_type == 'common':
                # 检查目录
                for dir_pattern in patterns['dirs']:
                    if self._match_pattern(file_dir, dir_pattern) or \
                       self._match_pattern(file_path, f"*/{dir_pattern}/*"):
                        return True
                
                # 检查文件
                for file_pattern in patterns['files']:
                    if self._match_pattern(file_name, file_pattern):
                        return True
                
                # 检查扩展名
                if file_ext in patterns['extensions']:
                    return True
        
        # 检查特定语言的环境模式
        if project_type in self.environment_patterns:
            patterns = self.environment_patterns[project_type]
            
            # 检查目录
            for dir_pattern in patterns['dirs']:
                if self._match_pattern(file_dir, dir_pattern) or \
                   self._match_pattern(file_path, f"*/{dir_pattern}/*"):
                    return True
            
            # 检查文件
            for file_pattern in patterns['files']:
                if self._match_pattern(file_name, file_pattern):
                    return True
            
            # 检查扩展名
            if file_ext in patterns['extensions']:
                return True
        
        return False
    
    def _is_source_directory_file(self, file_path: str, project_type: str) -> bool:
        """
        检查是否为源码目录下的文件
        源码目录：src/, lib/（但不包括第三方库安装位置如 site-packages, node_modules）
        """
        # 明确的第三方库安装路径模式（这些不应该被视为源码目录）
        third_party_install_paths = [
            'site-packages',
            'node_modules',
            'lib/python',
            'lib64/python',
            'Lib/site-packages',
            'venv',
            '.venv',
            'env',
            '.env'
        ]
        
        # 检查是否在明确的第三方库安装路径中
        for path_pattern in third_party_install_paths:
            if path_pattern in file_path.lower():
                return False
        
        # 源码目录模式：src/, lib/（在项目根目录下）
        source_dir_patterns = [
            r'^src/',
            r'^lib/',
            r'/[^/]+/src/',  # 如 flask-2.0.0/src/
            r'/[^/]+/lib/',  # 如 myproject/lib/
        ]
        
        import re
        for pattern in source_dir_patterns:
            if re.search(pattern, file_path):
                return True
        
        return False
    
    def _is_third_party_file(self, file_path: str, file_name: str, file_dir: str, 
                           project_type: str) -> bool:
        """检查是否为第三方库文件"""
        # 如果已经在源码目录中，不视为第三方库
        if self._is_source_directory_file(file_path, project_type):
            return False
        
        # 检查特定语言的第三方库模式
        lib_key = f"{project_type}_libs"
        if lib_key in self.third_party_patterns:
            patterns = self.third_party_patterns[lib_key]
            
            # 检查目录（但排除源码目录）
            for dir_pattern in patterns['dirs']:
                # 只有当路径不包含 src/ 或 lib/（源码目录）时才视为第三方库
                if 'src/' in file_path or '/src/' in file_path:
                    continue
                if 'lib/' in file_path or '/lib/' in file_path:
                    # 检查是否为第三方库安装位置
                    if 'site-packages' in file_path or 'node_modules' in file_path:
                        if self._match_pattern(file_dir, dir_pattern) or \
                           self._match_pattern(file_path, f"*/{dir_pattern}/*"):
                            return True
                else:
                    if self._match_pattern(file_dir, dir_pattern) or \
                       self._match_pattern(file_path, f"*/{dir_pattern}/*"):
                        return True
            
            # 检查文件
            for file_pattern in patterns['files']:
                if self._match_pattern(file_name, file_pattern):
                    return True
        
        return False
    
    def _is_config_file(self, file_name: str, file_ext: str) -> bool:
        """检查是否为配置文件"""
        # 检查配置文件名
        if file_name in self.config_patterns['config_files']:
            return True
        
        # 检查配置文件扩展名
        config_extensions = {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf'}
        if file_ext in config_extensions:
            # 进一步检查是否为项目配置文件
            config_keywords = ['config', 'setting', 'conf', 'cfg', 'ini']
            if any(keyword in file_name.lower() for keyword in config_keywords):
                return True
        
        return False
    
    def _is_documentation_file(self, file_path: str, file_name: str, file_ext: str) -> bool:
        """检查是否为文档文件"""
        # 检查文档目录
        for dir_pattern in self.documentation_patterns['docs']['dirs']:
            if self._match_pattern(file_path, f"*/{dir_pattern}/*"):
                return True
        
        # 检查文档文件
        if file_name in self.documentation_patterns['docs']['files']:
            return True
        
        # 检查文档扩展名
        if file_ext in self.documentation_patterns['docs']['extensions']:
            return True
        
        return False
    
    def _is_asset_file(self, file_path: str, file_name: str, file_ext: str) -> bool:
        """检查是否为资源文件"""
        # 检查资源目录
        for dir_pattern in self.documentation_patterns['assets']['dirs']:
            if self._match_pattern(file_path, f"*/{dir_pattern}/*"):
                return True
        
        # 检查资源文件
        for file_pattern in self.documentation_patterns['assets']['files']:
            if self._match_pattern(file_name, file_pattern):
                return True
        
        # 检查资源扩展名
        if file_ext in self.documentation_patterns['assets']['extensions']:
            return True
        
        return False
    
    def _match_pattern(self, text: str, pattern: str) -> bool:
        """匹配模式"""
        try:
            # 将glob模式转换为正则表达式
            regex_pattern = pattern.replace('*', '.*').replace('?', '.')
            return bool(re.match(regex_pattern, text, re.IGNORECASE))
        except Exception:
            return False
    
    def filter_project_files(self, project_path: str) -> Dict[str, List[str]]:
        """
        过滤项目文件
        
        Returns:
            {
                'analyze_files': [...],      # 需要分析的文件
                'skip_files': [...],         # 跳过的文件
                'project_type': 'python',    # 项目类型
                'statistics': {...}          # 统计信息
            }
        """
        analyze_files = []
        skip_files = []
        skip_reasons = {}
        
        # 检测项目类型
        project_type = self.detect_project_type(project_path)
        
        try:
            for root, dirs, files in os.walk(project_path):
                # 跳过环境目录
                dirs[:] = [d for d in dirs if not self._is_environment_dir(d)]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, project_path)
                    
                    should_analyze, reason = self.should_analyze_file(rel_path, project_type)
                    
                    if should_analyze:
                        analyze_files.append(rel_path)
                    else:
                        skip_files.append(rel_path)
                        skip_reasons[rel_path] = reason
        
        except Exception as e:
            print(f"过滤项目文件时出错: {e}")
        
        # 生成统计信息
        statistics = {
            'total_files': len(analyze_files) + len(skip_files),
            'analyze_files': len(analyze_files),
            'skip_files': len(skip_files),
            'project_type': project_type,
            'skip_reasons': {}
        }
        
        # 统计跳过原因
        for reason in skip_reasons.values():
            statistics['skip_reasons'][reason] = statistics['skip_reasons'].get(reason, 0) + 1
        
        return {
            'analyze_files': analyze_files,
            'skip_files': skip_files,
            'project_type': project_type,
            'statistics': statistics
        }
    
    def _is_environment_dir(self, dir_name: str) -> bool:
        """检查是否为环境目录"""
        env_dirs = {
            '__pycache__', 'node_modules', '.git', '.svn', '.hg', '.bzr',
            'build', 'dist', 'target', 'bin', 'obj', '.vs', '.vscode',
            'venv', 'env', '.venv', '.env', '.tox', '.pytest_cache',
            '.mypy_cache', 'coverage', 'htmlcov', 'logs', 'log', 'tmp',
            'temp', 'cache', '.cache', 'backup', 'backups', 'old'
        }
        return dir_name in env_dirs

# 全局过滤器实例
github_filter = GitHubProjectFilter()
