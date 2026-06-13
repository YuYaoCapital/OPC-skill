#!/usr/bin/env python3
"""OPC 自动归档脚本：判断文件类型并分类保存到 OPC 目录结构。"""

import os
import re
import shutil
import json
from datetime import datetime
from pathlib import Path

OPC_ROOT = Path('/Users/r9/OPC')
SKILL_DIR = Path('/Users/r9/.kimi/skills/r9-opc-memory')
INDEX_FILE = SKILL_DIR / 'memory_index.json'

# 分类规则：关键词 -> 目录
CATEGORY_RULES = {
    '会议纪要': '00_公司治理/会议纪要',
    '投决会': '00_公司治理/会议纪要',
    '对话纪要': '00_公司治理/会议纪要',
    '决策记录': '00_公司治理/决策记录',
    '商业模式': '00_公司治理/决策记录',
    '建设进度': '00_公司治理/决策记录',
    '运营启动': '00_公司治理/决策记录',
    '人员配置': '00_公司治理/决策记录',
    '岗位职责': '01_投研策略',
    '投研策略': '01_投研策略',
    '协同手册': '01_投研策略',
    '研究报告': '01_投研策略/研究报告',
    '专题简报': '01_投研策略/研究报告',
    '风格切换': '01_投研策略/研究报告',
    '市场点评': '01_投研策略/研究报告',
    '每日资本市场': '04_运营技术/数据接入',
    '资本市场简报': '04_运营技术/数据接入',
    '客户分层': '02_投顾服务/客户分层',
    '陪伴内容': '02_投顾服务/陪伴内容',
    '客户方案': '02_投顾服务/客户方案',
    '一周工作': '02_投顾服务',
    'AI助手': '02_投顾服务',
    '边界手册': '02_投顾服务',
    '员工介绍': '05_人力资源/员工档案',
    '员工档案': '05_人力资源/员工档案',
    '合规': '03_合规风控/合规制度',
    '牌照': '03_合规风控/牌照资料',
    '审核': '03_合规风控/审核记录',
    '数据接入': '04_运营技术/数据接入',
    '系统文档': '04_运营技术/系统文档',
    '自动化': '04_运营技术/自动化脚本',
    '公司介绍': '00_公司治理/决策记录',
    '横纵分析': '01_投研策略/研究报告',
    '理财经理': '02_投顾服务',
    'Skills': '90_Skills',
    'skill': '90_Skills',
    '指令跟踪': '00_公司治理',
}

def load_index():
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'version': '1.0', 'last_updated': '', 'items': []}

def save_index(index):
    index['last_updated'] = datetime.now().isoformat()
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

def classify_file(filename):
    """根据文件名关键词判断分类目录。"""
    fn_lower = filename.lower()
    for keyword, category in CATEGORY_RULES.items():
        if keyword.lower() in fn_lower:
            return category
    return '00_公司治理/待分类'

def generate_summary(filename):
    """根据文件名生成简单摘要。"""
    name = Path(filename).stem.replace('OPC_', '')
    name = re.sub(r'_\d{8}', '', name)
    name = re.sub(r'_v\d+$', '', name)
    name = name.replace('_', ' ')
    return f"OPC公司文件：{name}"

def get_keywords(filename):
    """提取文件名中命中的分类关键词。"""
    fn_lower = filename.lower()
    return [k for k in CATEGORY_RULES.keys() if k.lower() in fn_lower]

def is_already_archived(src_path):
    """检查 OPC 中是否已存在同名/同内容的文件。"""
    src = Path(src_path)
    category = classify_file(src.name)
    dest_dir = OPC_ROOT / category
    base_name = src.stem
    base_name = re.sub(r'_v\d+$', '', base_name)
    
    # 检查目标目录中是否存在相同基础名称的文件
    for existing in dest_dir.glob(f'{base_name}*'):
        if existing.is_file():
            if existing.stat().st_size == src.stat().st_size:
                return True
    return False

def archive_file(src_path, move=False):
    """归档单个文件。"""
    src = Path(src_path)
    if not src.exists():
        return {'success': False, 'error': f'文件不存在: {src_path}'}
    
    # 如果文件已经在 OPC 目录内，只索引不复制
    is_inside_opc = OPC_ROOT in src.resolve().parents
    
    category = classify_file(src.name)
    dest_dir = OPC_ROOT / category
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    if is_inside_opc:
        # 只更新索引
        dest = src
    else:
        # 检查是否已归档
        if is_already_archived(src_path):
            return {'success': True, 'path': str(dest_dir / src.name), 'category': category, 'note': '已存在相同内容，跳过复制'}
        
        dest = dest_dir / src.name
        version = 1
        while dest.exists():
            stem = src.stem
            stem = re.sub(r'_v\d+$', '', stem)
            new_name = f"{stem}_v{version}{src.suffix}"
            dest = dest_dir / new_name
            version += 1
        
        if move:
            shutil.move(str(src), str(dest))
        else:
            shutil.copy2(str(src), str(dest))
    
    # 更新索引：避免重复条目
    index = load_index()
    existing_ids = {item['path'] for item in index['items']}
    relative_path = str(dest.relative_to(OPC_ROOT.parent))
    if relative_path in existing_ids:
        return {'success': True, 'path': str(dest), 'category': category, 'note': '索引已存在'}
    
    item = {
        'id': f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{re.sub(r'_v\\d+$', '', src.stem)}",
        'filename': dest.name,
        'path': relative_path,
        'category': category.replace('/', ' > '),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'type': src.suffix.upper().lstrip('.'),
        'summary': generate_summary(dest.name),
        'keywords': get_keywords(dest.name),
        'related_tasks': []
    }
    index['items'].append(item)
    save_index(index)
    
    return {'success': True, 'path': str(dest), 'category': category}

def scan_and_archive(source_dir, pattern='OPC_*'):
    """扫描目录并归档匹配文件。"""
    results = []
    for path in Path(source_dir).glob(pattern):
        if path.is_file():
            # 跳过已归档目录中的文件
            if 'OPC/' in str(path):
                continue
            # 跳过 skill 包 zip，避免自我归档循环
            if path.suffix.lower() == '.zip' and 'skills' in path.name.lower():
                continue
            result = archive_file(path, move=False)
            results.append(result)
    return results

def main():
    """默认归档入口：扫描用户主目录和桌面。"""
    results = []
    results.extend(scan_and_archive('/Users/r9'))
    results.extend(scan_and_archive('/Users/r9/Desktop'))
    
    success = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]
    
    print(f"归档完成：成功 {len(success)}，失败 {len(failed)}")
    for r in success[:5]:
        note = r.get('note', '')
        print(f"  ✓ {r['path']} {note}")
    for r in failed:
        print(f"  ✗ {r.get('error')}")

if __name__ == '__main__':
    main()
