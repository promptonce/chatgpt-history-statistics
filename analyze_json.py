import json
from typing import Any
import os
from pathlib import Path
from datetime import datetime
import jieba
from collections import Counter

def format_size(size_bytes):
    """将字节转换为人类可读的格式"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def format_timestamp(timestamp):
    """将时间戳转换为可读格式"""
    if not timestamp:
        return "未知时间"
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(timestamp)

def get_safe_timestamp(message):
    """安全地获取消息的时间戳"""
    try:
        return float(message.get('create_time', 0)) or 0
    except:
        return 0

def print_first_conversation(conversations: list) -> None:
    """打印第一个对话的内容"""
    try:
        if not conversations:
            print("对话列表为空")
            return
            
        first_conv = conversations[0]
        print("\n=== 第一个对话的信息 ===")
        print(f"标题: {first_conv.get('title', '无标题')}")
        print(f"创建时间: {format_timestamp(first_conv.get('create_time', 0))}")
        print(f"更新时间: {format_timestamp(first_conv.get('update_time', 0))}")
        
        # 获取对话内容
        mapping = first_conv.get('mapping', {})
        if not mapping:
            print("未找到对话内容")
            return
            
        # 找到所有消息节点
        messages = []
        for node_id, node in mapping.items():
            message = node.get('message')
            if message:
                author = message.get('author', {})
                role = author.get('role')
                content = message.get('content', {})
                parts = content.get('parts', [])
                
                if role and parts:
                    messages.append({
                        'role': role,
                        'content': parts[0],
                        'create_time': get_safe_timestamp(message)
                    })
        
        # 按时间排序
        messages.sort(key=lambda x: x['create_time'])
        
        print("\n=== 对话内容 ===")
        for i, msg in enumerate(messages, 1):
            role = "用户" if msg['role'] == "user" else "助手"
            print(f"\n[{i}] {role} ({format_timestamp(msg['create_time'])}):")
            print(msg['content'])
                    
    except Exception as e:
        print(f"处理对话内容时出错：{str(e)}")
        raise  # 为了调试，显示完整的错误信息

def analyze_json_structure(data: Any, prefix: str = "", max_list_items: int = 3) -> None:
    """分析 JSON 数据的结构并打印信息"""
    if isinstance(data, dict):
        print(f"{prefix}字典包含 {len(data)} 个键值对")
        for key, value in data.items():
            print(f"{prefix}键 '{key}' 的值类型是: {type(value).__name__}")
            analyze_json_structure(value, prefix + "  ", max_list_items)
    elif isinstance(data, list):
        print(f"{prefix}列表包含 {len(data)} 个元素")
        if data:
            print(f"{prefix}前 {min(max_list_items, len(data))} 个元素的类型是:")
            for i in range(min(max_list_items, len(data))):
                print(f"{prefix}  [{i}]: {type(data[i]).__name__}")
            if data and isinstance(data[0], (dict, list)):
                print(f"{prefix}第一个元素的详细结构:")
                analyze_json_structure(data[0], prefix + "  ", max_list_items)
    else:
        if isinstance(data, str):
            preview = data[:50] + "..." if len(data) > 50 else data
            print(f"{prefix}字符串值 (长度: {len(data)}): {preview}")
        else:
            print(f"{prefix}值类型: {type(data).__name__}, 值: {data}")

def analyze_time_patterns(conversations: list) -> None:
    """分析对话的时间分布规律"""
    try:
        if not conversations:
            print("对话列表为空")
            return
            
        # 统计每天的小时分布
        hour_distribution = [0] * 24
        # 统计每周的天数分布
        day_distribution = [0] * 7
        # 统计每月的天数分布
        month_distribution = [0] * 31
        
        for conv in conversations:
            create_time = conv.get('create_time', 0)
            if create_time:
                dt = datetime.fromtimestamp(create_time)
                # 统计小时分布
                hour_distribution[dt.hour] += 1
                # 统计星期分布 (0是周一，6是周日)
                day_distribution[dt.weekday()] += 1
                # 统计日期分布
                month_distribution[dt.day - 1] += 1
        
        print("\n=== 对话时间分布分析 ===")
        
        print("\n1. 24小时分布:")
        for hour in range(24):
            print(f"{hour:02d}:00 - {hour:02d}:59: {hour_distribution[hour]}次")
            
        print("\n2. 星期分布:")
        weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        for i, count in enumerate(day_distribution):
            print(f"{weekdays[i]}: {count}次")
            
        print("\n3. 日期分布:")
        for day in range(31):
            if month_distribution[day] > 0:
                print(f"{day + 1}日: {month_distribution[day]}次")
                
    except Exception as e:
        print(f"分析时间分布时出错：{str(e)}")

def analyze_word_frequency(conversations: list) -> None:
    """分析用户提问的词频"""
    try:
        if not conversations:
            print("对话列表为空")
            return
            
        # 收集所有用户消息
        all_user_messages = []
        for conv in conversations:
            mapping = conv.get('mapping', {})
            for node_id, node in mapping.items():
                message = node.get('message')
                if message and message.get('author', {}).get('role') == 'user':
                    content = message.get('content', {})
                    if isinstance(content, dict):
                        parts = content.get('parts', [''])
                        if parts and isinstance(parts, list) and parts[0]:
                            text = str(parts[0])
                            if any('\u4e00' <= char <= '\u9fff' for char in text):
                                all_user_messages.append(text)
        
        # 分词并统计词频
        words = []
        for message in all_user_messages:
            try:
                words.extend(jieba.lcut(str(message)))
            except Exception as e:
                print(f"分词时出错：{str(e)}")
                continue
        
        # 定义停用词
        stop_words = {
            '的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着',
            '没有', '看', '好', '自己', '这', '那', '啊', '呢', '吧', '吗', '啦', '么', '哦', '哈', '嗯', '呀', '哎', '噢', '喔', '对', '嘿',
            '把', '给', '让', '但', '但是', '而', '而且', '或者', '所以', '因为', '如果', '虽然', '这个', '那个', '这样', '那样', '这些', '那些',
            '什么', '怎么', '为什么', '如何', '哪里', '谁', '什么时候', '多少', '几', '怎样', '为', '向', '从', '与', '及', '以', '并', '等',
            '中', '内', '外', '前', '后', '下', '时', '里', '中', '年', '月', '日', '点', '分', '秒'
        }
        
        # 判断是否为中文词
        def is_chinese_word(word):
            return all('\u4e00' <= char <= '\u9fff' for char in word)
        
        # 过滤词汇
        word_counts = Counter([
            word for word in words 
            if len(word) > 1  # 过滤单字
            and word not in stop_words  # 过滤停用词
            and is_chinese_word(word)  # 只保留纯中文词
        ])
        
        # 打印前50个最常见的词
        print("\n=== 用户提问词频分析 ===")
        print("\n前50个最常见的中文词：")
        for word, count in word_counts.most_common(50):
            print(f"{word}: {count}次")
            
    except Exception as e:
        print(f"分析词频时出错：{str(e)}")

def main():
    json_path = Path("conversations.json")
    
    try:
        # 获取文件大小
        file_size = json_path.stat().st_size
        print(f"=== conversations.json 文件信息 ===")
        print(f"文件大小: {format_size(file_size)}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            conversations = json.load(f)
            print_first_conversation(conversations)
            analyze_time_patterns(conversations)
            analyze_word_frequency(conversations)
            
    except FileNotFoundError:
        print(f"错误：找不到文件 {json_path}")
    except json.JSONDecodeError:
        print("错误：JSON 格式无效")
    except Exception as e:
        print(f"发生错误：{str(e)}")

if __name__ == "__main__":
    main() 