import json
from tqdm import tqdm

# 读取JSON文件
with open('conversations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 假设data是一个列表，每个元素是一个对话
md_content = ''
for i, conv in tqdm(enumerate(data, 1), total=len(data), desc="转换进度"):
    md_content += f'## 对话 {i}\n'
    title = conv.get('title', '无标题')
    create_time = conv.get('create_time', 0)
    md_content += f'### 标题: {title}\n'
    md_content += f'### 创建时间: {create_time}\n\n'
    # 假设对话内容在mapping字段中
    mapping = conv.get('mapping', {})
    for node_id, node in mapping.items():
        message = node.get('message')
        if message:
            author = message.get('author', {})
            role = author.get('role')
            content = message.get('content', {})
            parts = content.get('parts', [])
            if role and parts:
                md_content += f'#### {role.capitalize()}\n'
                md_content += f'{parts[0]}\n\n'

# 写入Markdown文件
with open('conversations.md', 'w', encoding='utf-8') as f:
    f.write(md_content)