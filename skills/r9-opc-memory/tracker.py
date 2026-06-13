#!/usr/bin/env python3
"""OPC 董事长指令跟踪表维护。"""

import json
import re
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path('/Users/r9/.kimi/skills/r9-opc-memory')
TRACKER_FILE = SKILL_DIR / 'tracker_data.json'

def load_tracker():
    if TRACKER_FILE.exists():
        with open(TRACKER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'version': '1.0', 'items': []}

def save_tracker(data):
    data['last_updated'] = datetime.now().isoformat()
    with open(TRACKER_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # 自动同步生成 PDF
    try:
        from tracker_pdf import generate_tracker_pdf
        generate_tracker_pdf()
    except Exception as e:
        print(f"[tracker] PDF 同步生成失败：{e}")

def extract_tasks_from_text(text):
    """从文本中提取可能的董事长指令。"""
    tasks = []
    patterns = [
        r'(?:给我|帮我|你|请|需要|必须|要求).{2,30}(?:完成|提交|生成|整理|推进|组织|跟踪|评估|确认)',
        r'(?:在|于)\d{4}年\d{1,2}月\d{1,2}日(?:前|之前|收盘前).{2,40}(?:完成|提交|生成|整理|更新)',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            tasks.append(match.group(0).strip())
    return list(set(tasks))

def add_task(content, owner, deadline, deliverable=''):
    """添加新的董事长指令。"""
    data = load_tracker()
    new_id = len(data['items']) + 1
    item = {
        'id': new_id,
        'content': content,
        'owner': owner,
        'deadline': deadline,
        'status': '待启动',
        'deliverable': deliverable,
        'note': '',
        'created_at': datetime.now().strftime('%Y-%m-%d')
    }
    data['items'].append(item)
    save_tracker(data)
    return item

def update_task_status(task_id_or_keyword, new_status):
    """更新指令状态。"""
    data = load_tracker()
    updated = []
    for item in data['items']:
        if str(item['id']) == str(task_id_or_keyword) or task_id_or_keyword in item['content']:
            item['status'] = new_status
            item['updated_at'] = datetime.now().strftime('%Y-%m-%d')
            updated.append(item)
    save_tracker(data)
    return updated

def get_open_tasks():
    """获取未完成的指令。"""
    data = load_tracker()
    return [item for item in data['items'] if item['status'] not in ['已完成', '已取消']]

if __name__ == '__main__':
    data = load_tracker()
    if not data['items']:
        add_task('6月13日收盘前提交《风格切换持续性专题简报》', 'Atlas', '2026-06-13', '专题简报最终版')
        add_task('组织L2高权益客户集中再平衡', 'Mira+Orion', '2026-06-20', '再平衡方案+客户陪伴话术')
        add_task('推进数据接入从L2半自动化到L3自动化', 'Vega', '2026-07-11', '数据接入升级报告')
        print("跟踪表已初始化")
    print(f"当前未完成任务：{len(get_open_tasks())}")
