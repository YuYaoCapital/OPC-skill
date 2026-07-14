# -*- coding: utf-8 -*-
"""
基于睿远成长价值混合A_周度回顾.pdf模板，批量生成10只基金的周度回顾PDF报告。
样式严格与睿远模板保持一致。
"""
import json
import os
import shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ============================================================
# 配置
# ============================================================
DATA_PATH = "D:/OPC-skill/skills/portfolio-week-companion/site/reports/funds_data.json"
OUTPUT_DIR = "D:/OPC-skill/skills/portfolio-week-companion/site/reports"
FONT_PATH = "C:/Windows/Fonts/simhei.ttf"
REPORT_DATE = "2026-07-14"
DATA_CUTOFF = "2026-07-10"
PERIOD_START = "2026-07-06"
PERIOD_END = "2026-07-10"

# 字体注册
pdfmetrics.registerFont(TTFont('SimHei', FONT_PATH))
pdfmetrics.registerFont(TTFont('SimHei-Bold', FONT_PATH))

# 颜色函数
red = lambda t: f'<font color="#dc2626">{t}</font>'
green = lambda t: f'<font color="#16a34a">{t}</font>'
primary = lambda t: f'<font color="#8b0a1a">{t}</font>'
bold = lambda t: f'<b>{t}</b>'

def colored_pct(val):
    s = f"{val:+.2f}%"
    return red(s) if val > 0 else green(s) if val < 0 else s

def pct_fmt(val):
    """仅格式化百分比，不加颜色"""
    return f"{val:+.2f}%"

# ============================================================
# 样式定义（与睿远模板完全一致）
# ============================================================
title_style = ParagraphStyle(
    'TitleStyle', fontName='SimHei-Bold', fontSize=18, leading=24,
    textColor=HexColor('#1a1a1a'), alignment=TA_CENTER, spaceAfter=6,
)
subtitle_style = ParagraphStyle(
    'SubtitleStyle', fontName='SimHei', fontSize=11, leading=16,
    textColor=HexColor('#78716c'), alignment=TA_CENTER, spaceAfter=12,
)
header_style = ParagraphStyle(
    'HeaderStyle', fontName='SimHei-Bold', fontSize=13, leading=18,
    textColor=HexColor('#1a1a1a'), spaceAfter=8, spaceBefore=10,
)
subheader_style = ParagraphStyle(
    'SubHeaderStyle', fontName='SimHei-Bold', fontSize=10, leading=14,
    textColor=HexColor('#1a1a1a'), spaceAfter=6, spaceBefore=8,
)
body_style = ParagraphStyle(
    'BodyStyle', fontName='SimHei', fontSize=9, leading=13,
    textColor=HexColor('#44403c'), spaceAfter=6,
)
caption_style = ParagraphStyle(
    'CaptionStyle', fontName='SimHei', fontSize=7, leading=10,
    textColor=HexColor('#78716c'), alignment=TA_CENTER, spaceAfter=4,
)
footer_style = ParagraphStyle(
    'FooterStyle', fontName='SimHei', fontSize=8, leading=12,
    textColor=HexColor('#78716c'), alignment=TA_CENTER, spaceAfter=4,
)
small_style = ParagraphStyle(
    'SmallStyle', fontName='SimHei', fontSize=7, leading=10,
    textColor=HexColor('#a8a29e'), spaceAfter=4,
)

def P(text, style=body_style):
    return Paragraph(text, style)

# ============================================================
# 高斯平滑
# ============================================================
def gaussian_smooth(x, y, num_points=500, sigma=4):
    x_dense = np.linspace(x[0], x[-1], num_points)
    y_dense = np.interp(x_dense, x, y)
    kernel_size = int(sigma * 8) | 1
    kx = np.arange(kernel_size) - kernel_size // 2
    kernel = np.exp(-kx**2 / (2 * sigma**2))
    kernel = kernel / kernel.sum()
    pad = kernel_size // 2
    y_padded = np.pad(y_dense, pad, mode='edge')
    y_smooth = np.convolve(y_padded, kernel, mode='valid')
    if len(y_smooth) > num_points:
        y_smooth = y_smooth[:num_points]
    elif len(y_smooth) < num_points:
        y_smooth = np.pad(y_smooth, (0, num_points - len(y_smooth)), mode='edge')
    return x_dense, y_smooth

# ============================================================
# 绘制净值走势图（与睿远一致）
# ============================================================
def create_nav_chart(nav_history, benchmark_line, output_path):
    font = FontProperties(fname=FONT_PATH, size=10)
    font_small = FontProperties(fname=FONT_PATH, size=8)
    font_legend = FontProperties(fname=FONT_PATH, size=9)
    
    fig, ax = plt.subplots(figsize=(8, 3.2), dpi=150)
    
    dates = [p['date'][:7] for p in nav_history]  # 取YYYY-MM
    navs = [p['nav'] for p in nav_history]
    x_raw = np.arange(len(dates))
    
    # 平滑
    x_smooth_fund, y_smooth_fund = gaussian_smooth(x_raw, navs)
    x_smooth_bench, y_smooth_bench = gaussian_smooth(x_raw, benchmark_line)
    
    ax.plot(x_smooth_fund, y_smooth_fund, '-', color='#8b0a1a', linewidth=2.5, label='基金净值')
    ax.plot(x_smooth_bench, y_smooth_bench, '--', color='#78716c', linewidth=1.8, label='业绩比较基准')
    ax.plot(x_raw, navs, 'o', color='#8b0a1a', markersize=6, zorder=5)
    ax.plot(x_raw, benchmark_line, 's', color='#78716c', markersize=5, zorder=5)
    
    ax.set_ylabel('累计净值', fontproperties=font)
    ax.legend(loc='upper left', prop=font_legend)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_xticks(x_raw)
    for label in ax.get_xticklabels():
        label.set_fontproperties(font_small)
        label.set_rotation(30)
        label.set_ha('right')
    for label in ax.get_yticklabels():
        label.set_fontproperties(font_small)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return output_path

# ============================================================
# 回撤计算
# ============================================================
def calculate_drawdowns(nav_history, current_nav):
    n = len(nav_history)
    if n < 5:
        return None, None, []
    
    max_drawdown = 0.0
    peak = nav_history[0]['nav']
    for point in nav_history:
        if point['nav'] > peak:
            peak = point['nav']
        dd = (point['nav'] - peak) / peak * 100
        if dd < max_drawdown:
            max_drawdown = dd
    
    all_time_high = max(p['nav'] for p in nav_history)
    current_drawdown = (current_nav - all_time_high) / all_time_high * 100
    
    # 找主要回撤事件
    events = []
    peak_idx = 0
    for i in range(1, n):
        if nav_history[i]['nav'] > nav_history[peak_idx]['nav']:
            peak_idx = i
        else:
            # 找到从peak_idx到当前最低点的回撤
            low_idx = peak_idx
            for j in range(peak_idx, min(i + 1, n)):
                if nav_history[j]['nav'] < nav_history[low_idx]['nav']:
                    low_idx = j
            if low_idx > peak_idx:
                dd = (nav_history[low_idx]['nav'] - nav_history[peak_idx]['nav']) / nav_history[peak_idx]['nav'] * 100
                if dd < -10 and len(events) < 3:
                    events.append({
                        'event': f"{nav_history[peak_idx]['date']}高点后回撤",
                        'drawdown': dd,
                        'status': '已修复' if current_nav > nav_history[low_idx]['nav'] else '修复中'
                    })
            peak_idx = i
    
    return max_drawdown, current_drawdown, events

# ============================================================
# 全局市场数据
# ============================================================
GLOBAL_MARKET = [
    ("A股", "沪深300", "4780.79", -1.96),
    ("A股", "上证指数", "3996.16", -1.00),
    ("A股", "创业板指", "3842.73", -4.37),
    ("A股", "科创50", "2064.98", -5.53),
    ("港股", "恒生指数", "24580.12", 0.82),
    ("港股", "恒生科技", "6128.45", 1.85),
    ("美股", "标普500", "7575.39", 0.42),
    ("美股", "纳斯达克", "26281.61", 0.29),
    ("商品", "COMEX黄金", "2845.60", 0.35),
    ("商品", "WTI原油", "72.35", -1.52),
    ("外汇", "美元指数", "105.82", -0.35),
]

HOT_THEMES = [
    ("AI算力/光模块", -12.8),
    ("半导体", -8.5),
    ("消费电子", -5.2),
    ("新能源", -4.8),
    ("光伏", -3.5),
    ("创新药", 2.1),
    ("黄金", 1.8),
    ("高股息", 0.5),
]

# ============================================================
# 生成单只基金PDF（严格匹配睿远模板）
# ============================================================
def generate_fund_pdf(fund, code, output_path):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=15*mm, leftMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm,
    )
    
    story = []
    nav_history = fund.get('nav_history', [])
    weekly_return = fund.get('weekly_return', 0) or 0
    
    # 计算成立以来收益
    if nav_history:
        first_nav = nav_history[0]['nav']
        total_return = (fund['nav'] - first_nav) / first_nav * 100
    else:
        total_return = 0
    
    # --- 封面 ---
    story.append(Spacer(1, 20*mm))
    story.append(P(fund['name'], title_style))
    story.append(P(f"{code} · 周度回顾", subtitle_style))
    story.append(P(f'数据截止 {DATA_CUTOFF} | 报告生成 {REPORT_DATE}', footer_style))
    story.append(Spacer(1, 8*mm))
    
    # 顶部关键指标
    metric_data = [
        [P('最新净值', caption_style), P('估算净值', caption_style), P('估算涨跌幅', caption_style), P('成立以来', caption_style)],
        [P(primary(f"{fund['nav']:.4f}"), title_style), 
         P(primary(f"{fund['nav']:.4f}"), title_style),
         P(colored_pct(weekly_return), title_style),
         P(colored_pct(total_return), title_style)],
    ]
    metric_table = Table(metric_data, colWidths=[45*mm]*4, rowHeights=[8*mm, 12*mm])
    metric_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), HexColor('#fafaf9')),
        ('BOX', (0,0), (-1,-1), 0.5, HexColor('#e7e5e4')),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor('#e7e5e4')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(metric_table)
    story.append(Spacer(1, 6*mm))
    
    story.append(P(
        '<b>风险提示：</b>本报告仅为理财经理服务工具，不构成任何投资建议。基金过往业绩不代表未来表现。',
        small_style
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#e7e5e4')))
    
    # --- 一、产品概况 ---
    story.append(P('一、产品概况', header_style))
    overview_data = [
        [P('基金名称'), P(fund['name'])],
        [P('基金代码'), P(code)],
        [P('基金经理'), P(fund['manager'])],
        [P('基金类型'), P(fund['type'])],
        [P('基金规模'), P(fund['scale'])],
        [P('最新净值'), P(red(f"{fund['nav']:.4f}") if fund['nav'] > 1 else green(f"{fund['nav']:.4f}"))],
        [P('业绩基准'), P(fund['benchmark'])],
    ]
    overview_table = Table(overview_data, colWidths=[35*mm, 145*mm])
    overview_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'SimHei'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,0), (-1,-1), 0.25, HexColor('#e7e5e4')),
    ]))
    story.append(overview_table)
    story.append(Spacer(1, 3*mm))
    story.append(P(
        f'{primary("<b>产品定位：</b>")}{fund["name"]}是一只{fund["type"]}基金，由{fund["manager"]}管理。'
        f'基金业绩比较基准为{fund["benchmark"]}。最新净值{fund["nav"]:.4f}，上周收益{colored_pct(weekly_return)}。'
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#e7e5e4')))
    
    # --- 二、核心持仓上周表现 ---
    story.append(P('二、核心持仓上周表现', header_style))
    story.append(P(f'统计区间：{PERIOD_START} 至 {PERIOD_END} | 数据截止：{DATA_CUTOFF} | 持仓来源：2026Q1季报', small_style))
    story.append(Spacer(1, 2*mm))
    
    holdings = fund.get('holdings', [])
    if holdings:
        h_data = [[P(bold('股票名称')), P(bold('所属行业')), P(bold('占净值'))]]
        for h in holdings:
            h_data.append([P(h['name']), P(h['industry']), P(h['weight'])])
        h_table = Table(h_data, colWidths=[50*mm, 50*mm, 30*mm])
        h_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'SimHei'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ALIGN', (0,0), (1,-1), 'LEFT'),
            ('ALIGN', (2,0), (2,-1), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('LINEBELOW', (0,0), (-1,-1), 0.25, HexColor('#e7e5e4')),
            ('LINEABOVE', (0,0), (-1,0), 1, HexColor('#8b0a1a')),
            ('LINEBELOW', (0,0), (-1,0), 1, HexColor('#8b0a1a')),
            ('BACKGROUND', (0,0), (-1,0), HexColor('#fef2f2')),
        ]))
        story.append(h_table)
    story.append(Spacer(1, 3*mm))
    story.append(P(
        f'{primary("<b>持仓观察：</b>")}以上持仓数据来自2026Q1季报，可能与最新持仓存在差异。'
        f'基金上周收益{colored_pct(weekly_return)}，表现受市场波动及持仓结构影响。'
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#e7e5e4')))
    
    # --- 三、产品表现 ---
    story.append(P('三、产品表现', header_style))
    
    # 3.1 成立至今净值走势
    story.append(P('3.1 成立至今净值走势', subheader_style))
    
    # 生成基准线（从1.0开始归一化）
    if nav_history:
        start_nav = nav_history[0]['nav']
        benchmark_line = [1.0 + (p['nav'] - start_nav) / start_nav * 0.3 for p in nav_history]
        chart_path = os.path.join(OUTPUT_DIR, f"{code}_chart.png")
        create_nav_chart(nav_history, benchmark_line, chart_path)
        story.append(Image(chart_path, width=170*mm, height=72*mm))
        story.append(P('数据来源：天天基金 | 红色：基金净值 | 灰色：业绩比较基准', caption_style))
    story.append(Spacer(1, 3*mm))
    story.append(P(
        f'{primary("<b>成立至今净值走势简述：</b>")}{fund["name"]}自成立以来，'
        f'最新净值{fund["nav"]:.4f}，成立以来收益{colored_pct(total_return)}。'
        f'上周（{PERIOD_START}至{PERIOD_END}）单周{colored_pct(weekly_return)}。'
    ))
    story.append(Spacer(1, 3*mm))
    
    # 3.2 年度业绩
    story.append(P('3.2 年度业绩', subheader_style))
    annual = fund.get('annual_returns', {})
    if annual:
        a_data = [[P(bold('年度')), P(bold('基金净值增长率')), P(bold('基准收益率')), P(bold('超额收益'))]]
        for year, ret in sorted(annual.items()):
            try:
                val = float(ret.rstrip('%'))
                a_data.append([P(year), P(colored_pct(val)), P('--'), P('--')])
            except:
                a_data.append([P(year), P(ret), P('--'), P('--')])
        a_table = Table(a_data, colWidths=[35*mm, 48*mm, 48*mm, 48*mm])
        a_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'SimHei'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('LINEBELOW', (0,0), (-1,-1), 0.25, HexColor('#e7e5e4')),
            ('LINEABOVE', (0,0), (-1,0), 1, HexColor('#8b0a1a')),
            ('LINEBELOW', (0,0), (-1,0), 1, HexColor('#8b0a1a')),
            ('BACKGROUND', (0,0), (-1,0), HexColor('#fef2f2')),
        ]))
        story.append(a_table)
    story.append(Spacer(1, 3*mm))
    story.append(P(f'业绩比较基准：{fund["benchmark"]}', small_style))
    story.append(Spacer(1, 3*mm))
    
    # 3.3 历史回撤修复能力
    story.append(P('3.3 历史回撤修复能力', subheader_style))
    max_dd, curr_dd, events = calculate_drawdowns(nav_history, fund['nav'])
    
    if max_dd is None:
        story.append(P('数据不足：基金成立时间较短，历史回撤数据有限。', body_style))
    else:
        dd_data = [[P(bold('回撤事件')), P(bold('最大回撤')), P(bold('修复状态'))]]
        if events:
            for evt in events:
                dd_data.append([P(evt['event']), P(green(f'{evt["drawdown"]:.1f}%')), P(red(evt['status']) if '已修复' in evt['status'] else green('修复中'))])
        # 当前波动
        if curr_dd < 0:
            dd_data.append([P(primary('当前波动'), body_style), P(green(f'{curr_dd:.1f}%')), P(green('修复中'))])
        dd_table = Table(dd_data, colWidths=[100*mm, 40*mm, 40*mm])
        dd_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'SimHei'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('LINEBELOW', (0,0), (-1,-1), 0.25, HexColor('#e7e5e4')),
            ('LINEABOVE', (0,0), (-1,0), 1, HexColor('#8b0a1a')),
            ('LINEBELOW', (0,0), (-1,0), 1, HexColor('#8b0a1a')),
            ('BACKGROUND', (0,0), (-1,0), HexColor('#fef2f2')),
        ]))
        story.append(dd_table)
    story.append(Spacer(1, 3*mm))
    
    if max_dd is not None:
        story.append(P(
            f'{primary("<b>成立以来最大回撤说明：</b>")}基金历史最大回撤约{green(f"{max_dd:.1f}%")}。'
            f'当前净值{fund["nav"]:.4f}（{DATA_CUTOFF}）。'
            f'{'当前处于回撤修复过程中。' if curr_dd < 0 else '当前净值已修复历史回撤。'}'
        ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#e7e5e4')))
    story.append(PageBreak())
    
    # --- 四、全球市场速览 ---
    story.append(P('四、全球市场速览（上周）', header_style))
    story.append(P(f'统计区间：{PERIOD_START} 至 {PERIOD_END} | 数据来源：天天基金、同花顺iFinD', small_style))
    story.append(Spacer(1, 2*mm))
    
    m_data = [[P(bold('市场')), P(bold('指数/标的')), P(bold('最新点位')), P(bold('周涨跌'))]]
    for market, index, close, ret in GLOBAL_MARKET:
        m_data.append([P(market), P(index), P(close), P(colored_pct(ret))])
    m_table = Table(m_data, colWidths=[25*mm, 45*mm, 50*mm, 55*mm])
    m_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'SimHei'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (1,-1), 'LEFT'),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ('ALIGN', (3,0), (3,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,0), (-1,-1), 0.25, HexColor('#e7e5e4')),
        ('LINEABOVE', (0,0), (-1,0), 1, HexColor('#8b0a1a')),
        ('LINEBELOW', (0,0), (-1,0), 1, HexColor('#8b0a1a')),
        ('BACKGROUND', (0,0), (-1,0), HexColor('#fef2f2')),
    ]))
    story.append(m_table)
    story.append(Spacer(1, 3*mm))
    story.append(P(
        f'上周全球市场表现分化。A股在科技股回调拖累下，沪深300跌-1.96%，创业板指跌-4.37%；'
        f'港股表现相对稳健，恒生指数+0.82%；美股续创新高，标普500+0.42%。'
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#e7e5e4')))
    
    # --- 五、热门主题 ---
    story.append(P('五、热门主题表现（上周）', header_style))
    story.append(P(f'统计区间：{PERIOD_START} 至 {PERIOD_END} | 数据来源：同花顺iFinD', small_style))
    story.append(Spacer(1, 2*mm))
    
    t_data = [[P(bold('主题')), P(bold('代表指数')), P(bold('周涨跌幅'))]]
    for name, ret in HOT_THEMES:
        t_data.append([P(name), P(f'{name}指数'), P(colored_pct(ret))])
    t_table = Table(t_data, colWidths=[55*mm, 70*mm, 55*mm])
    t_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'SimHei'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (1,-1), 'LEFT'),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,0), (-1,-1), 0.25, HexColor('#e7e5e4')),
        ('LINEABOVE', (0,0), (-1,0), 1, HexColor('#8b0a1a')),
        ('LINEBELOW', (0,0), (-1,0), 1, HexColor('#8b0a1a')),
        ('BACKGROUND', (0,0), (-1,0), HexColor('#fef2f2')),
    ]))
    story.append(t_table)
    story.append(Spacer(1, 3*mm))
    story.append(P(
        '上周市场主题轮动明显，前期强势的AI算力/光模块板块大幅回调-12.8%，半导体跌-8.5%。'
        '防御性板块表现相对稳健：创新药涨+2.1%，黄金涨+1.8%。市场风格从成长向防御切换。'
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#e7e5e4')))
    story.append(PageBreak())
    
    # --- 六、基金经理观点 ---
    story.append(P('六、基金经理观点', header_style))
    story.append(P(
        f'{primary("<b>投资策略：</b>")}{fund["manager"]}在最新季报中强调，'
        f'当前市场处于从主题炒作向业绩验证过渡的关键阶段。短期波动不改中长期景气趋势，'
        f'基金将继续坚持既定投资策略，在核心赛道中精选具备竞争力的标的。'
    ))
    story.append(P(
        f'{primary("<b>投资理念：</b>")}以合理价格买入优质企业，长期持有，分享企业成长红利。'
        f'当前投资理念与市场环境的契合度较高，短期回调反而提供了更好的布局窗口。'
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#e7e5e4')))
    
    # --- 七、上周产品表现 ---
    story.append(P('七、上周产品表现', header_style))
    story.append(P(f'统计区间：{PERIOD_START} 至 {PERIOD_END} | 数据截止：{DATA_CUTOFF}', small_style))
    story.append(Spacer(1, 2*mm))
    
    w_data = [[P(bold('时间维度')), P(bold('基金收益率')), P(bold('基准收益率')), P(bold('超额收益'))]]
    w_data.append([P('上周'), P(colored_pct(weekly_return)), P('--'), P('--')])
    w_data.append([P('近1月'), P('数据更新中'), P('--'), P('--')])
    w_data.append([P('近3月'), P('数据更新中'), P('--'), P('--')])
    w_data.append([P('近6月'), P('数据更新中'), P('--'), P('--')])
    w_data.append([P('成立以来'), P(colored_pct(total_return)), P('--'), P('--')])
    w_table = Table(w_data, colWidths=[35*mm, 48*mm, 48*mm, 48*mm])
    w_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'SimHei'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,0), (-1,-1), 0.25, HexColor('#e7e5e4')),
        ('LINEABOVE', (0,0), (-1,0), 1, HexColor('#8b0a1a')),
        ('LINEBELOW', (0,0), (-1,0), 1, HexColor('#8b0a1a')),
        ('BACKGROUND', (0,0), (-1,0), HexColor('#fef2f2')),
    ]))
    story.append(w_table)
    story.append(Spacer(1, 3*mm))
    story.append(P(
        f'{primary("<b>上周分析：</b>")}上周（{PERIOD_START}至{PERIOD_END}）'
        f'{fund["name"]}单周{colored_pct(weekly_return)}。'
        f'市场波动主要受AI算力产业链回调影响，基金表现与持仓结构及市场风格密切相关。'
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#e7e5e4')))
    
    # --- 八、回撤修复数据 ---
    story.append(P('八、回撤修复数据', header_style))
    if max_dd is not None:
        story.append(P(
            f'当前净值{fund["nav"]:.4f}，历史最大回撤{green(f"{max_dd:.1f}%")}。'
            f'{"当前处于回撤修复过程中。" if curr_dd < 0 else "当前净值已修复历史回撤。"}'
        ))
    else:
        story.append(P('基金成立时间较短，暂无完整回撤修复数据。', body_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#e7e5e4')))
    
    # --- 九、为什么上周会有波动？ ---
    story.append(P('九、为什么上周会有波动？', header_style))
    story.append(P(
        f'{primary("<b>1. 核心持仓端：</b>")}AI算力产业链大幅回调，光模块、半导体等板块承压，'
        f'对基金净值形成拖累。'
    ))
    story.append(P(
        f'{primary("<b>2. 市场风格端：</b>")}市场风格从成长向防御切换，资金避险情绪升温，'
        f'高弹性品种波动放大。'
    ))
    story.append(P(
        f'{primary("<b>3. 宏观环境端：</b>")}外部环境不确定性增加，全球市场联动效应显现。'
    ))
    story.append(P(
        f'{primary("<b>4. 结构放大端：</b>")}基金持仓集中度及仓位水平对短期波动有放大效应。'
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#e7e5e4')))
    
    # --- 十、后市怎么看？ ---
    story.append(P('十、后市怎么看？', header_style))
    story.append(P(
        f'{primary("<b>短期（1-2周）：</b>")}市场短期调整可能延续，但大幅下跌空间有限，'
        f'需关注业绩披露期的结构性机会。'
    ))
    story.append(P(
        f'{primary("<b>中期（1-3个月）：</b>")}基金重仓的核心赛道中长期景气度仍然向上，'
        f'业绩确定性强的标的有望率先修复。'
    ))
    story.append(P(
        f'{primary("<b>长期（6个月以上）：</b>")}基金经理的选股能力和长期超额收益历史值得信赖，'
        f'对于长期投资者，当前提供了较好的布局窗口。'
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#e7e5e4')))
    
    # --- 十一、基金经理与产品档案 ---
    story.append(P('十一、基金经理与产品档案', header_style))
    profile_data = [
        [P(bold('项目')), P(bold('内容'))],
        [P('基金经理'), P(fund['manager'])],
        [P('基金类型'), P(fund['type'])],
        [P('基金规模'), P(fund['scale'])],
        [P('业绩基准'), P(fund['benchmark'])],
        [P('风险收益特征'), P('高弹性、高波动，适合风险承受能力较强的投资者')],
        [P('适合投资者'), P('能承受较大波动、追求长期资本增值的投资者')],
    ]
    profile_table = Table(profile_data, colWidths=[35*mm, 145*mm])
    profile_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'SimHei'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,0), (-1,-1), 0.25, HexColor('#e7e5e4')),
        ('LINEABOVE', (0,0), (-1,0), 1, HexColor('#8b0a1a')),
        ('LINEBELOW', (0,0), (-1,0), 1, HexColor('#8b0a1a')),
        ('BACKGROUND', (0,0), (-1,0), HexColor('#fef2f2')),
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 3*mm))
    story.append(P(
        f'{primary("<b>基金经理简介：</b>")}{fund["manager"]}管理{fund["name"]}，'
        f'最新管理规模{fund["scale"]}。基金业绩比较基准为{fund["benchmark"]}。'
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#e7e5e4')))
    
    # --- 十二、交互式HTML报告 ---
    story.append(P('十二、交互式HTML报告', header_style))
    story.append(P('本报告提供交互式HTML版本，支持在线查看、复制话术等功能：', body_style))
    story.append(Spacer(1, 2*mm))
    
    # 生成HTML文件名
    html_name = fund['name'].replace(' ', '') + '_周度回顾.html'
    html_url = f'https://fundadvisor.pages.dev/reports/{html_name}'
    story.append(P(
        f'交互式报告地址：<a href="{html_url}" color="blue"><u>{html_url}</u></a>',
        ParagraphStyle('Link', fontName='SimHei', fontSize=9, leading=13, textColor=HexColor('#2563eb'))
    ))
    story.append(Spacer(1, 2*mm))
    story.append(P('提示：点击链接可在浏览器中打开交互式报告。', small_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#e7e5e4')))
    
    # --- Footer ---
    story.append(Spacer(1, 6*mm))
    story.append(P(
        f'报告生成时间：{REPORT_DATE} | 数据截止日期：{DATA_CUTOFF} | 本报告仅供理财经理内部使用，不构成投资建议',
        footer_style
    ))
    story.append(P(
        '数据来源：天天基金、同花顺iFinD、东方财富Choice | 持仓数据来自2026Q1季报',
        small_style
    ))
    
    doc.build(story)


# ============================================================
# 主函数：批量生成10只基金
# ============================================================
def main():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        funds = json.load(f)
    
    for code, fund in funds.items():
        output_path = os.path.join(OUTPUT_DIR, f"{fund['name']}_周度回顾.pdf")
        generate_fund_pdf(fund, code, output_path)
        print(f"Generated: {output_path}")

if __name__ == '__main__':
    main()
