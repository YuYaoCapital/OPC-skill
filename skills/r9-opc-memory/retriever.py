#!/usr/bin/env python3
"""OPC 记忆检索：在本地归档和 JSON 索引中检索历史信息。"""

import json
import re
import sys
from pathlib import Path

OPC_ROOT = Path('/Users/r9/OPC')
SKILL_DIR = Path('/Users/r9/.kimi/skills/r9-opc-memory')
INDEX_FILE = SKILL_DIR / 'memory_index.json'

def load_index():
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('items', [])
    return []

def tokenize(text):
    """分词：中文单字、英文单词、连续数字、下划线分隔。"""
    text = str(text).lower()
    tokens = []
    # 中文单字
    tokens.extend(re.findall(r'[\u4e00-\u9fa5]', text))
    # 英文单词、数字段、下划线分隔段
    for part in re.findall(r'[a-z0-9_]+', text):
        for sub in part.split('_'):
            # 进一步拆分字母和数字
            for sub2 in re.findall(r'[a-z]+|[0-9]+', sub):
                if len(sub2) >= 2 or sub2.isdigit():
                    tokens.append(sub2)
    return tokens

def compact(text):
    """去掉所有非字母数字字符，形成紧凑字符串。"""
    return re.sub(r'[^a-z0-9\u4e00-\u9fa5]', '', str(text).lower())

def search(query, top_n=5):
    """根据关键词检索归档记录。"""
    items = load_index()
    query_tokens = tokenize(query)
    query_compact = compact(query)
    if not query_tokens and not query_compact:
        return []
    
    results = []
    for item in items:
        score = 0
        filename = item.get('filename', '')
        category = item.get('category', '')
        keywords = ' '.join(item.get('keywords', []))
        summary = item.get('summary', '')
        
        searchable_text = ' '.join([filename, category, keywords, summary])
        searchable_tokens = tokenize(searchable_text)
        
        # token 匹配
        for token in query_tokens:
            if token in searchable_tokens:
                score += 1
        
        # 紧凑字符串匹配文件名
        if query_compact and query_compact in compact(filename):
            score += 3
        
        # 紧凑字符串匹配摘要/关键词
        if query_compact and query_compact in compact(summary + keywords):
            score += 1
        
        if score > 0:
            results.append((score, item))
    
    # 按分数降序，时间倒序
    results.sort(key=lambda x: (-x[0], x[1].get('date', '')))
    return results[:top_n]

def answer_question(question):
    """回答历史检索问题。"""
    results = search(question, top_n=3)
    if not results:
        return "未在 OPC 本地归档中找到相关信息。请检查关键词或确认该内容已被归档。"
    
    lines = []
    lines.append("——检索结果——")
    for i, (score, item) in enumerate(results, 1):
        date = item.get('date', '未知日期')
        title = item.get('filename', '未命名')
        category = item.get('category', '')
        summary = item.get('summary', '')[:80]
        full_path = OPC_ROOT.parent / item.get('path', '')
        lines.append(f"{i}. [{date}] {title}（{category}）")
        lines.append(f"   摘要：{summary}...")
        lines.append(f"   路径：{full_path}")
        lines.append('')
    
    return '\n'.join(lines)

if __name__ == '__main__':
    query = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else '风格切换'
    print(answer_question(query))
