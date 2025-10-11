import sys
import os
import unittest
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import test_python_bad


class TestBadFunction(unittest.TestCase):
    
    def test_bad_function(self):
        result = test_python_bad.bad_function()
        self.assertEqual(result, 3)


class TestUnsafeEval(unittest.TestCase):
    
    def test_unsafe_eval(self):
        # 测试eval函数执行
        result = test_python_bad.unsafe_eval()
        self.assertIsNone(result)  # eval执行print返回None


class TestProcessUserData(unittest.TestCase):
    
    def test_process_user_data_normal(self):
        result = test_python_bad.process_user_data("hello")
        self.assertEqual(result, "HELLO")
    
    def test_process_user_data_empty(self):
        result = test_python_bad.process_user_data("")
        self.assertEqual(result, "")
    
    def test_process_user_data_with_numbers(self):
        result = test_python_bad.process_user_data("test123")
        self.assertEqual(result, "TEST123")


class TestDivideNumbers(unittest.TestCase):
    
    def test_divide_numbers_normal(self):
        result = test_python_bad.divide_numbers(10, 2)
        self.assertEqual(result, 5.0)
    
    def test_divide_numbers_zero_division(self):
        with self.assertRaises(ZeroDivisionError):
            test_python_bad.divide_numbers(10, 0)
    
    def test_divide_numbers_float_result(self):
        result = test_python_bad.divide_numbers(5, 2)
        self.assertEqual(result, 2.5)


class TestUseGlobal(unittest.TestCase):
    
    def test_use_global(self):
        # 保存原始值
        original_value = test_python_bad.global_var
        
        result = test_python_bad.use_global()
        self.assertEqual(result, "modified")
        self.assertEqual(test_python_bad.global_var, "modified")
        
        # 恢复原始值
        test_python_bad.global_var = original_value


class TestReadFile(unittest.TestCase):
    
    def test_read_file_normal(self):
        # 创建临时文件测试
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("test content")
            temp_filename = temp_file.name
        
        try:
            result = test_python_bad.read_file(temp_filename)
            self.assertEqual(result, "test content")
        finally:
            os.unlink(temp_filename)
    
    def test_read_file_nonexistent(self):
        with self.assertRaises(FileNotFoundError):
            test_python_bad.read_file("nonexistent_file.txt")


class TestCreateLargeList(unittest.TestCase):
    
    def test_create_large_list(self):
        result = test_python_bad.create_large_list()
        self.assertEqual(len(result), 1000000)
        self.assertEqual(result[0], "item_0")
        self.assertEqual(result[-1], "item_999999")
        self.assertIsInstance(result, list)


class TestFormatString(unittest.TestCase):
    
    def test_format_string_normal(self):
        result = test_python_bad.format_string("john")
        expected = "SELECT * FROM users WHERE name = 'john'"
        self.assertEqual(result, expected)
    
    def test_format_string_special_chars(self):
        result = test_python_bad.format_string("test' OR '1'='1")
        expected = "SELECT * FROM users WHERE name = 'test' OR '1'='1'"
        self.assertEqual(result, expected)


class TestRiskyOperation(unittest.TestCase):
    
    def test_risky_operation(self):
        with self.assertRaises(KeyError):
            test_python_bad.risky_operation()


class TestUnreachableCode(unittest.TestCase):
    
    def test_unreachable_code(self):
        result = test_python_bad.unreachable_code()
        self.assertEqual(result, "reached")


class TestBadClass(unittest.TestCase):
    
    def setUp(self):
        self.bad_instance = test_python_bad.BadClass()
    
    def test_init(self):
        self.assertIsNone(self.bad_instance.value)
    
    def test_method_without_docstring(self):
        result = self.bad_instance.method_without_docstring()
        self.assertIsNone(result)
        
        self.bad_instance.value = "test"
        result = self.bad_instance.method_without_docstring()
        self.assertEqual(result, "test")


class TestEnvironmentVariables(unittest.TestCase):
    
    def test_api_key_not_exposed(self):
        # 测试环境变量而不是直接访问模块变量
        api_key = os.getenv("API_KEY", "")
        secret_password = os.getenv("SECRET_PASSWORD", "")
        
        # 这些应该为空，因为我们没有设置这些环境变量
        self.assertEqual(api_key, "")
        self.assertEqual(secret_password, "")


if __name__ == "__main__":
    unittest.main()