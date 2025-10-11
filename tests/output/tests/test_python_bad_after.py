import sys
import os
import unittest
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import test_python_bad_after


class TestGetApiKey(unittest.TestCase):
    
    def test_get_api_key_exists(self):
        """测试存在API_KEY环境变量的情况"""
        with patch.dict(os.environ, {'API_KEY': 'test_api_key_123'}):
            result = test_python_bad_after.get_api_key()
            self.assertEqual(result, 'test_api_key_123')
    
    def test_get_api_key_not_exists(self):
        """测试不存在API_KEY环境变量的情况"""
        with patch.dict(os.environ, clear=True):
            result = test_python_bad_after.get_api_key()
            self.assertEqual(result, '')


class TestGetSecretPassword(unittest.TestCase):
    
    def test_get_secret_password_exists(self):
        """测试存在SECRET_PASSWORD环境变量的情况"""
        with patch.dict(os.environ, {'SECRET_PASSWORD': 'my_secret_pass'}):
            result = test_python_bad_after.get_secret_password()
            self.assertEqual(result, 'my_secret_pass')
    
    def test_get_secret_password_not_exists(self):
        """测试不存在SECRET_PASSWORD环境变量的情况"""
        with patch.dict(os.environ, clear=True):
            result = test_python_bad_after.get_secret_password()
            self.assertEqual(result, '')


class TestBadFunction(unittest.TestCase):
    
    def test_bad_function(self):
        """测试bad_function返回正确的结果"""
        result = test_python_bad_after.bad_function()
        self.assertEqual(result, 3)


class TestSafeEval(unittest.TestCase):
    
    def test_safe_eval_valid_expression(self):
        """测试有效的数学表达式"""
        test_cases = [
            ("2 + 3", "5"),
            ("10 - 5", "5"),
            ("3 * 4", "12"),
            ("15 / 3", "5.0"),
            ("(2 + 3) * 4", "20")
        ]
        
        for expression, expected in test_cases:
            with self.subTest(expression=expression):
                result = test_python_bad_after.safe_eval(expression)
                self.assertEqual(result, expected)
    
    def test_safe_eval_invalid_input_type(self):
        """测试非字符串输入"""
        with self.assertRaises(ValueError):
            test_python_bad_after.safe_eval(123)
    
    def test_safe_eval_unsafe_characters(self):
        """测试包含不安全字符的表达式"""
        unsafe_expressions = [
            "import os",
            "__import__('os')",
            "eval('1+1')",
            "2 + '3'",
            "print('hello')"
        ]
        
        for expression in unsafe_expressions:
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    test_python_bad_after.safe_eval(expression)
    
    def test_safe_eval_syntax_error(self):
        """测试语法错误的表达式"""
        result = test_python_bad_after.safe_eval("2 + ")
        self.assertTrue(result.startswith("计算错误:"))


class TestProcessUserData(unittest.TestCase):
    
    def test_process_user_data_valid(self):
        """测试有效的用户数据处理"""
        test_cases = [
            ("hello", "HELLO"),
            ("Hello World", "HELLO WORLD"),
            ("123abc", "123ABC"),
            ("", ""),
            ("   test   ", "   TEST   ")
        ]
        
        for input_data, expected in test_cases:
            with self.subTest(input_data=input_data):
                result = test_python_bad_after.process_user_data(input_data)
                self.assertEqual(result, expected)
    
    def test_process_user_data_invalid_type(self):
        """测试非字符串输入"""
        with self.assertRaises(TypeError):
            test_python_bad_after.process_user_data(123)
        
        with self.assertRaises(TypeError):
            test_python_bad_after.process_user_data(None)
    
    def test_process_user_data_empty_string(self):
        """测试空字符串输入"""
        with self.assertRaises(ValueError):
            test_python_bad_after.process_user_data("   ")


class TestDivideNumbers(unittest.TestCase):
    
    def test_divide_numbers_valid(self):
        """测试有效的除法运算"""
        test_cases = [
            (10, 2, 5.0),
            (15, 3, 5.0),
            (7.5, 2.5, 3.0),
            (-10, 2, -5.0),
            (0, 5, 0.0)
        ]
        
        for a, b, expected in test_cases:
            with self.subTest(a=a, b=b):
                result = test_python_bad_after.divide_numbers(a, b)
                self.assertEqual(result, expected)
    
    def test_divide_numbers_by_zero(self):
        """测试除数为零的情况"""
        with self.assertRaises(ZeroDivisionError):
            test_python_bad_after.divide_numbers(10, 0)
    
    def test_divide_numbers_invalid_type(self):
        """测试非数字输入"""
        with self.assertRaises(TypeError):
            test_python_bad_after.divide_numbers("10", 2)
        
        with self.assertRaises(TypeError):
            test_python_bad_after.divide_numbers(10, "2")
        
        with self.assertRaises(TypeError):
            test_python_bad_after.divide_numbers(None, 2)


class TestGlobalState(unittest.TestCase):
    
    def setUp(self):
        """在每个测试前重置全局状态"""
        test_python_bad_after.GlobalState._state = "global"
    
    def test_get_state_default(self):
        """测试获取默认状态"""
        result = test_python_bad_after.GlobalState.get_state()
        self.assertEqual(result, "global")
    
    def test_set_state_valid(self):
        """测试设置有效的状态值"""
        test_python_bad_after.GlobalState.set_state("new_state")
        result = test_python_bad_after.GlobalState.get_state()
        self.assertEqual(result, "new_state")
    
    def test_set_state_invalid_type(self):
        """测试设置非字符串状态值"""
        with self.assertRaises(TypeError):
            test_python_bad_after.GlobalState.set_state(123)
        
        with self.assertRaises(TypeError):
            test_python_bad_after.GlobalState.set_state(None)


if __name__ == '__main__':
    unittest.main()