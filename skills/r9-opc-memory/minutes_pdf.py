#!/usr/bin/env python3
"""生成 OPC 会议纪要 PDF。"""

from fpdf import FPDF
from pathlib import Path
from datetime import datetime

OPC_ROOT = Path('/Users/r9/OPC')
FONT_DIR = Path('/System/Library/Fonts/Supplemental')

def get_font_path(name):
    mapping = {
        'hei': Path('/System/Library/Fonts/STHeiti Light.ttc'),
        'song': FONT_DIR / 'Songti.ttc',
        'kai': FONT_DIR / 'Kaiti.ttc',
    }
    return mapping.get(name, FONT_DIR / 'Songti.ttc')

class MinutesPDF(FPDF):
    def __init__(self):
        super().__init__(unit='mm', format='A4')
        self._register_fonts()
        self.set_auto_page_break(True, margin=20)
        self.add_page()
        self.set_margins(15, 15, 15)
    
    def _register_fonts(self):
        self.add_font('Song', '', str(get_font_path('song')))
        self.add_font('Hei', '', str(get_font_path('hei')))
        self.set_font('Hei', '', 16)
    
    def _text(self, text, font='Song', size=11):
        """重置 x 位置并输出多行文本。"""
        self.set_x(self.l_margin)
        self.set_font(font, '', size)
        self.multi_cell(self.w - self.l_margin - self.r_margin, 6, text)
        self.ln(2)
    
    def header_title(self, title):
        self.set_font('Hei', '', 18)
        self.cell(0, 12, 'OPC 会议纪要', new_x='LMARGIN', new_y='NEXT', align='C')
        self.set_font('Hei', '', 13)
        self.cell(0, 8, f'——{title}——', new_x='LMARGIN', new_y='NEXT', align='C')
        self.ln(4)
    
    def section_title(self, title):
        self.set_x(self.l_margin)
        self.set_font('Hei', '', 12)
        self.set_fill_color(230, 230, 230)
        self.cell(self.w - self.l_margin - self.r_margin, 8, title, new_x='LMARGIN', new_y='NEXT', fill=True)
        self.ln(1)
    
    def bullet_list(self, items):
        for i, item in enumerate(items, 1):
            self._text(f'{i}. {item}', font='Song', size=11)

def generate_minutes_pdf(elements, output_path=None):
    """生成会议纪要 PDF。"""
    if output_path is None:
        date_str = datetime.now().strftime('%Y%m%d')
        title = elements.get('theme', '会议')[:20]
        output_path = OPC_ROOT / f'00_公司治理/会议纪要/{date_str}_会议纪要_{title}_v1.pdf'
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    pdf = MinutesPDF()
    pdf.header_title(elements.get('theme', 'OPC 工作会议'))
    
    participants = elements.get('participants', ['R9、Luce 及 OPC 各 Agent 角色'])
    if isinstance(participants, list):
        participants = '、'.join(participants)
    
    info_text = (
        f"会议时间：{elements.get('date', datetime.now().strftime('%Y年%m月%d日'))}\n"
        f"参会人员：{participants}"
    )
    pdf._text(info_text, font='Song', size=11)
    
    pdf.section_title('一、核心结论')
    conclusions = elements.get('conclusions', [])
    if conclusions:
        pdf.bullet_list(conclusions)
    else:
        pdf._text('（本次讨论未形成明确结论性表述）')
    
    pdf.section_title('二、决议事项')
    decisions = elements.get('decisions', [])
    if decisions:
        pdf.bullet_list(decisions)
    else:
        pdf._text('（本次讨论未形成正式决议）')
    
    pdf.section_title('三、待办任务')
    todos = elements.get('todos', [])
    if todos:
        pdf.bullet_list(todos)
    else:
        pdf._text('（暂无新增待办）')
    
    pdf.output(str(output_path))
    return output_path

if __name__ == '__main__':
    sample = {
        'theme': '风格切换与资产配置讨论',
        'date': '2026年06月13日',
        'participants': ['R9', 'Luce', 'Atlas', 'Mira'],
        'conclusions': [
            '当前处于高切低再平衡早期，尚未构成全面风格反转。',
            '有色金属受供给约束+弱美元+资金切低估值共振驱动，短期情绪过热不建议追涨。'
        ],
        'decisions': [
            'Atlas 在 6/13 收盘后生成风格切换简报终版。',
            'Mira 牵头 L2 客户集中再平衡。'
        ],
        'todos': [
            'Atlas 生成风格切换简报终版（6/13 收盘后）',
            'Mira 组织 L2 客户再平衡（6/20 前）',
            'Vega 推进数据接入 L3 自动化（7/11 前）'
        ]
    }
    path = generate_minutes_pdf(sample)
    print(f"会议纪要已生成：{path}")
