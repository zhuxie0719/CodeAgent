import yaml
import json
import pickle


def load_stuff(s: str):
    # 动态反序列化/解析：高风险
    data = yaml.load(s)  # yaml_load: high（应使用 safe_load）
    obj = pickle.loads(s)  # pickle: high
    return json.loads(s)  # json_loads: medium


def open_file(name: str) -> str:
    # 打开文件未关闭
    f = open(name, "r", encoding="utf-8")  # file_not_closed: high
    return f.read()


def recurse(n: int) -> int:
    # 递归无终止条件
    return recurse(n - 1) + 1  # recursion_no_base_case: high


def compute(a: int, b: int) -> int:
    # 除零错误
    return a // (b - b)  # division_by_zero: high


