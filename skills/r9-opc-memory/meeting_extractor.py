#!/usr/bin/env python3
"""OPC 会议纪要提取：从对话文本中提取关键要素。"""

import re
from datetime import datetime

def extract_meeting_elements(text):
    """从对话文本中提取会议纪要要素。"""
    elements = {
        'theme': '',
        'date': datetime.now().strftime('%Y年%m月%d日'),
        'participants': [],
        'conclusions': [],
        'decisions': [],
        'todos': [],
        'next_topics': []
    }
    
    # 简单提取主题：找第一段或包含"关于"的句子
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if lines:
        first = lines[0]
        if '关于' in first or '会议' in first:
            elements['theme'] = first[:60]
    
    # 提取参会人
    participant_patterns = [
        r'参会(?:人员|人|者)[：:\s]*([^\n]+)',
        r'出席[：:\s]*([^\n]+)',
    ]
    for pattern in participant_patterns:
        match = re.search(pattern, text)
        if match:
            elements['participants'] = [p.strip() for p in match.group(1).split('、') if p.strip()]
            break
    
    # 提取结论
    conclusion_keywords = ['核心结论', '结论', '判断']
    for line in lines:
        for kw in conclusion_keywords:
            if kw in line and len(line) > 10:
                elements['conclusions'].append(line.strip())
                break
    
    # 提取待办
    todo_keywords = ['待办', 'TODO', 'todo', '需要', '负责人', '截止时间']
    for line in lines:
        for kw in todo_keywords:
            if kw in line and len(line) > 10:
                elements['todos'].append(line.strip())
                break
    
    # 去重
    elements['conclusions'] = list(set(elements['conclusions']))[:5]
    elements['todos'] = list(set(elements['todos']))[:10]
    
    return elements

def format_minutes(elements):
    """格式化会议纪要文本。"""
    lines = []
    lines.append(f"会 议 纪 要")
    lines.append(f"——{elements['theme']}——")
    lines.append('')
    lines.append(f"会议时间：{elements['date']}")
    
    if elements['participants']:
        lines.append(f"参会人员：{'、'.join(elements['participants'])}")
    else:
        lines.append("参会人员：R9、Luce 及 OPC 各 Agent 角色")
    
    lines.append('')
    lines.append("一、核心结论")
    if elements['conclusions']:
        for i, c in enumerate(elements['conclusions'], 1):
            lines.append(f"{i}. {c}")
    else:
        lines.append("（本次讨论未形成明确结论性表述）")
    
    lines.append('')
    lines.append("二、决议事项")
    if elements['decisions']:
        for i, d in enumerate(elements['decisions'], 1):
            lines.append(f"{i}. {d}")
    else:
        lines.append("（本次讨论未形成正式决议）")
    
    lines.append('')
    lines.append("三、待办任务")
    if elements['todos']:
        for i, t in enumerate(elements['todos'], 1):
            lines.append(f"{i}. {t}")
    else:
        lines.append("（暂无新增待办）")
    
    if elements['next_topics']:
        lines.append('')
        lines.append("四、下次会议议题")
        for i, t in enumerate(elements['next_topics'], 1):
            lines.append(f"{i}. {t}")
    
    return '\n'.join(lines)

if __name__ == '__main__':
    sample = """
    今天讨论了两个问题：一是风格切换是否持续，二是有色金属怎么理解。
    核心结论：当前处于高切低再平衡的早期阶段，尚未构成全面风格反转。
    待办任务：Atlas 在6月13日收盘前提交风格切换简报最终版；Mira 组织 L2 客户集中陪伴。
    """
    elements = extract_meeting_elements(sample)
    print(format_minutes(elements))
