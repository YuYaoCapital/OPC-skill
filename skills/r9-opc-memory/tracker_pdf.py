#!/usr/bin/env python3
"""生成 OPC 董事长指令跟踪表 PDF。"""

from fpdf import FPDF
from pathlib import Path
from datetime import datetime
import json

OPC_ROOT = Path('/Users/r9/OPC')
DESKTOP = Path('/Users/r9/Desktop')
TRACKER_JSON = Path('/Users/r9/.kimi/skills/r9-opc-memory/tracker_data.json')
FONT_HEI = '/System/Library/Fonts/STHeiti Light.ttc'
FONT_SONG = '/System/Library/Fonts/Supplemental/Songti.ttc'

class TrackerPDF(FPDF):
    def __init__(self):
        super().__init__(unit='mm', format='A4', orientation='L')
        self.add_font('Hei', '', FONT_HEI)
        self.add_font('Song', '', FONT_SONG)
        self.set_auto_page_break(True, margin=15)
        self.add_page()
        self.set_margins(10, 10, 10)
    
    def header(self):
        self.set_font('Hei', '', 16)
        self.cell(0, 10, 'OPC 董事长指令跟踪表', new_x='LMARGIN', new_y='NEXT', align='C')
        self.set_font('Song', '', 10)
        self.cell(0, 6, f'更新日期：{datetime.now().strftime("%Y年%m月%d日")}', new_x='LMARGIN', new_y='NEXT', align='C')
        self.ln(3)

def load_items():
    if TRACKER_JSON.exists():
        with open(TRACKER_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('items', [])
    return []

def generate_tracker_pdf(output_path=None):
    if output_path is None:
        output_path = OPC_ROOT / '00_公司治理/OPC_董事长指令跟踪表.pdf'
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    items = load_items()
    pdf = TrackerPDF()
    
    # 表头
    headers = ['序号', '指令内容', '负责人', '截止时间', '状态', '交付物', '备注']
    col_widths = [12, 75, 25, 25, 22, 45, 50]
    
    pdf.set_font('Hei', '', 10)
    pdf.set_fill_color(220, 220, 220)
    for h, w in zip(headers, col_widths):
        pdf.cell(w, 8, h, border=1, fill=True, align='C')
    pdf.ln()
    
    # 数据行
    pdf.set_font('Song', '', 9)
    status_colors = {
        '已完成': (200, 255, 200),
        '进行中': (255, 255, 200),
        '待启动': (240, 240, 240),
        '待决策': (255, 220, 200),
    }
    
    for item in items:
        row = [
            str(item.get('id', '')),
            item.get('content', ''),
            item.get('owner', ''),
            item.get('deadline', ''),
            item.get('status', ''),
            item.get('deliverable', ''),
            item.get('note', ''),
        ]
        status = item.get('status', '')
        fill_color = status_colors.get(status, (255, 255, 255))
        pdf.set_fill_color(*fill_color)
        
        # 计算行高
        max_lines = 1
        for text, w in zip(row, col_widths):
            lines = len(str(text)) / max(1, (w / 2.2)) + 1
            max_lines = max(max_lines, lines)
        row_h = max(7, min(max_lines * 4.5, 20))
        
        x_start = pdf.get_x()
        y_start = pdf.get_y()
        for text, w in zip(row, col_widths):
            pdf.multi_cell(w, row_h / max_lines, str(text), border=1, fill=True, align='L')
            x_start += w
            pdf.set_xy(x_start, y_start)
        pdf.ln(row_h)
    
    pdf.output(str(output_path))
    
    # 同时备份桌面
    desktop_path = DESKTOP / 'OPC_董事长指令跟踪表.pdf'
    pdf.output(str(desktop_path))
    
    return output_path, desktop_path

if __name__ == '__main__':
    paths = generate_tracker_pdf()
    print(f"指令跟踪表已生成：\n  {paths[0]}\n  {paths[1]}")
