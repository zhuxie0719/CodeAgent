"""
AGENT特定配置
"""

from typing import Dict, Any


# 代码分析AGENT配置
CODE_ANALYSIS_CONFIG = {
    "analyze_interval": 60,  # 分析间隔（秒）
    "max_file_size": 10 * 1024 * 1024,  # 最大文件大小（字节）
    "supported_extensions": [".py", ".js", ".html", ".css"],
    "exclude_patterns": [
        "*/__pycache__/*",
        "*/node_modules/*",
        "*/venv/*",
        "*/env/*",
        "*.pyc",
        "*.pyo"
    ],
    "complexity_threshold": 10,  # 复杂度阈值
    "maintainability_threshold": 0.8  # 可维护性阈值
}

# 缺陷检测AGENT配置
BUG_DETECTION_CONFIG = {
    "scan_interval": 300,  # 扫描间隔（秒）
    "severity_levels": ["error", "warning", "info"],
    "max_issues_per_file": 100,
    "tools": {
        "pylint": {
            "enabled": True,
            "args": ["--disable=C0114,C0116,C0103"]
        },
        "flake8": {
            "enabled": True,
            "args": ["--max-line-length=88", "--ignore=E203,W503"]
        },
        "bandit": {
            "enabled": True,
            "args": ["-r", "-f", "json", "-ll"]
        }
    }
}

# 修复执行AGENT配置
FIX_EXECUTION_CONFIG = {
    "auto_fix_enabled": True,
    "backup_enabled": True,
    "max_fix_attempts": 3,
    "fix_strategies": {
        "code_style": ["black", "isort"],
        "security": ["bandit_fixes"],
        "refactor": ["rope", "2to3"]
    },
    "validation_required": True
}

# 测试验证AGENT配置
TEST_VALIDATION_CONFIG = {
    "min_coverage": 80,  # 最小测试覆盖率
    "test_timeout": 300,  # 测试超时时间（秒）
    "parallel_tests": True,
    "test_types": ["unit", "integration", "performance"],
    "coverage_tools": ["pytest-cov", "coverage.py"]
}

# 性能优化AGENT配置
PERFORMANCE_OPTIMIZATION_CONFIG = {
    "monitor_interval": 60,  # 监控间隔（秒）
    "cpu_threshold": 80,  # CPU使用率阈值
    "memory_threshold": 80,  # 内存使用率阈值
    "disk_threshold": 90,  # 磁盘使用率阈值
    "optimization_strategies": [
        "caching",
        "database_optimization",
        "code_optimization",
        "resource_cleanup"
    ]
}

# 代码质量AGENT配置
CODE_QUALITY_CONFIG = {
    "check_interval": 1800,  # 检查间隔（秒）
    "quality_metrics": {
        "maintainability_index": 0.8,
        "cyclomatic_complexity": 10,
        "code_duplication": 0.05,
        "test_coverage": 0.8
    },
    "documentation_required": True,
    "type_hints_required": True
}

# 所有AGENT配置的映射
AGENT_CONFIGS = {
    "code_analysis_agent": CODE_ANALYSIS_CONFIG,
    "bug_detection_agent": BUG_DETECTION_CONFIG,
    "fix_execution_agent": FIX_EXECUTION_CONFIG,
    "test_validation_agent": TEST_VALIDATION_CONFIG,
    "performance_optimization_agent": PERFORMANCE_OPTIMIZATION_CONFIG,
    "code_quality_agent": CODE_QUALITY_CONFIG
}
