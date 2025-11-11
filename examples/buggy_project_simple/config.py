import os
import datetime

# 环境变量未设置默认值
API_KEY = os.getenv("API_KEY")  # missing_env_default: medium

# 时区未明确
NOW = datetime.datetime.now()  # timezone_handling: low



