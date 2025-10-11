#!/usr/bin/env python3
"""
创建正确的测试文件 - 只测试模块级别函数
"""

import os
import sys

# 禁用日志
import logging
logging.disable(logging.CRITICAL)

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents', 'test_validation_agent'))

def create_correct_test():
    """创建正确的测试文件"""
    try:
        print("导入模拟AI测试生成器...")
        from mock_ai_test_generator import MockAITestGenerator
        
        print("创建模拟生成器实例...")
        generator = MockAITestGenerator()
        
        # 检查目标文件
        target_file = "tests/output/test_python_bad_after.py"
        if not os.path.exists(target_file):
            print(f"❌ 目标文件不存在: {target_file}")
            return False
            
        print(f"✅ 目标文件存在: {target_file}")
        
        # 读取源文件内容
        with open(target_file, 'r', encoding='utf-8') as f:
            source_content = f.read()
        
        # 提取模块级别的函数
        module_functions = []
        lines = source_content.split('\n')
        
        in_class = False
        for line in lines:
            line = line.strip()
            
            # 检查是否进入类定义
            if line.startswith('class '):
                in_class = True
                continue
            
            # 检查是否退出类定义（下一个非缩进行）
            if in_class and line and not line.startswith('    ') and not line.startswith('class '):
                in_class = False
            
            # 匹配模块级别的函数定义（不是类方法）
            if line.startswith('def ') and '(' in line and not line.startswith('    def ') and not in_class:
                func_name = line.split('def ')[1].split('(')[0].strip()
                if not func_name.startswith('_'):  # 跳过私有函数
                    module_functions.append(func_name)
        
        print(f"✅ 找到模块级别函数: {module_functions}")
        
        # 生成测试内容
        test_content = f'''"""
AI自动生成的测试文件 - 为 test_python_bad_after.py 生成
这是由AI测试生成器自动创建的单元测试文件
测试目标: test_python_bad_after.py
生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import unittest
import sys
import os

# 添加源代码路径到sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
source_dir = os.path.join(os.path.dirname(current_dir), "output")
sys.path.insert(0, source_dir)

try:
    # 尝试导入被测试的模块
    import test_python_bad_after as source_module
except ImportError as e:
    print(f"警告: 无法导入模块 test_python_bad_after: {{e}}")
    source_module = None


class AIGeneratedTestTest_Python_Bad_After(unittest.TestCase):
    """AI生成的测试类 - 测试 test_python_bad_after.py 中的函数"""
    
    def setUp(self):
        """测试前的设置"""
        if source_module is None:
            self.skipTest("无法导入源代码模块")
    
    def tearDown(self):
        """测试后的清理"""
        pass
'''
        
        # 为每个模块级别函数生成测试方法
        for func_name in module_functions:
            test_content += f'''
    def test_{func_name}(self):
        """测试函数 {func_name}"""
        if source_module is None:
            self.skipTest("无法导入源代码模块")
        
        # 测试函数存在
        self.assertTrue(
            hasattr(source_module, "{func_name}"),
            f"模块缺少函数 {{func_name}}"
        )
        
        # 测试函数可调用
        func = getattr(source_module, "{func_name}")
        self.assertTrue(callable(func), f"函数 {{func_name}} 不可调用")
        
        # 这里可以添加具体的功能测试
        # 根据函数签名调整参数
        try:
            # 示例：测试函数调用（需要根据实际函数调整）
            # result = func(...)
            # self.assertIsNotNone(result)
            pass
        except Exception as e:
            # 某些函数可能需要特定参数，这是正常的
            pass
'''
        
        test_content += f'''
    def test_module_import(self):
        """测试模块导入"""
        self.assertIsNotNone(source_module, "模块导入失败")
    
    def test_module_has_functions(self):
        """测试模块包含预期的函数"""
        if source_module is None:
            self.skipTest("无法导入源代码模块")
        
        # 检查模块是否包含预期的函数
        expected_functions = {module_functions}
        
        for func_name in expected_functions:
            self.assertTrue(
                hasattr(source_module, func_name),
                f"模块缺少函数 {{func_name}}"
            )


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
'''
        
        # 写入测试文件
        test_file_path = "tests/ai_test_python_bad_after_correct.py"
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"✅ 测试文件已创建: {test_file_path}")
        print(f"📄 测试文件大小: {len(test_content)} 字符")
        
        return True
        
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 开始创建正确的测试文件...")
    
    success = create_correct_test()
    
    if success:
        print("\n🎉 测试文件创建成功!")
    else:
        print("\n💥 测试文件创建失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()
