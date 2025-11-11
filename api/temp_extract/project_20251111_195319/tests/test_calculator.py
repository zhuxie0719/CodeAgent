import pytest

from src.calculator import add, divide


def test_add_passes():
    assert add(2, 3) == 5


def test_divide_by_zero_fails():
    # 故意设计为失败：应该抛出异常，但我们断言返回值
    # 这将触发失败，验证测试失败能被集成并回传
    assert divide(10, 0) == 0


