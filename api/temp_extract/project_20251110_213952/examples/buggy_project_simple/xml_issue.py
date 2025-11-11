import xml.etree.ElementTree as ET


def parse_xml(path: str):
    # 直接解析外部 XML（可能触发 XXE 相关规则）
    return ET.parse(path)  # xml_parse: medium


