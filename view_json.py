import json

def print_structure(obj, level=0):
    """打印对象的基本结构"""
    indent = "  " * level
    if isinstance(obj, dict):
        print(f"{indent}字典包含 {len(obj)} 个键:")
        for key in list(obj.keys())[:3]:  # 只显示前3个键
            print(f"{indent}- {key}")
            if level < 2:  # 限制递归深度
                print_structure(obj[key], level + 1)
    elif isinstance(obj, list):
        print(f"{indent}列表包含 {len(obj)} 个元素")
        if obj and level < 2:  # 只显示第一个元素的结构
            print(f"{indent}第一个元素:")
            print_structure(obj[0], level + 1)

try:
    with open('conversations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        print("=== JSON 文件基本结构 ===")
        print_structure(data)
except Exception as e:
    print(f"发生错误：{str(e)}") 