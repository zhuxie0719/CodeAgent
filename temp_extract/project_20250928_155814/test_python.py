# 存在多种缺陷的示例代码
def calculate_average(numbers):
    # 缺陷1：未处理空列表情况
    total = sum(numbers)
    # 缺陷2：整除可能导致结果不准确
    return total / len(numbers)


def process_data(data):
    # 缺陷3：未判断数据类型，可能传入非列表参数
    result = []
    for item in data:
        # 缺陷4：未处理字符串转整数失败的情况
        result.append(int(item) * 2)
    return result


def read_config(config_path):
    # 缺陷5：未处理文件不存在的异常
    with open(config_path, 'r') as f:
        # 缺陷6：未关闭文件（虽然with会自动关闭，但这里模拟逻辑缺陷）
        config = f.read()
    # 缺陷7：假设配置一定是JSON格式但未验证
    import json
    return json.loads(config)


class DataProcessor:
    def __init__(self, threshold):
        # 缺陷8：未验证threshold的有效性
        self.threshold = threshold

    def process(self, value):
        # 缺陷9：可能导致除零错误
        return value / self.threshold if value else 0


if __name__ == "__main__":
    # 缺陷10：测试用例不完整，未覆盖异常场景
    avg = calculate_average([1, 2, 3])
    print(f"Average: {avg}")
    
    processed = process_data(["4", "5", "6"])
    print(f"Processed: {processed}")
    
    config = read_config("config.json")
    print(f"Config: {config}")
    
    processor = DataProcessor(5)
    print(f"Processed value: {processor.process(10)}")
