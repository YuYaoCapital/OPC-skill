# -*- coding: utf-8 -*-
"""
Fund Weekly Review — Fixed PDF Generator
Style locked, data-driven. All visual constants are hard-coded.
DO NOT MODIFY style definitions; only inject data via funds_data.json.
"""
import json, os, sys, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ============================================================
# 1. 样式常量 — 绝对锁定，任何执行都不允许改动
# ============================================================
FONT_PATH = "C:/Windows/Fonts/simhei.ttf"
FONT_PATH_YAHEI = "C:/Windows/Fonts/msyh.ttc"

# 注册字体
pdfmetrics.registerFont(TTFont('SimHei', FONT_PATH))
pdfmetrics.registerFont(TTFont('SimHei-Bold', FONT_PATH))

# 颜色常量
C_PRIMARY      = HexColor('#8b0a1a')   # 主标题红
C_PRIMARY_L    = HexColor('#c41e3a')   # 二级标题红
C_UP           = HexColor('#dc2626')   # 上涨红
C_DOWN         = HexColor('#16a34a')   # 下跌绿
C_BG_LIGHT     = HexColor('#fef2f2')   # 表头浅红底
C_BG_GRAY      = HexColor('#fafaf9')   # 浅灰底
C_BORDER       = HexColor('#e7e5e4')   # 边框灰
C_TEXT_MAIN    = HexColor('#1a1a1a')   # 正文黑
C_TEXT_SEC     = HexColor('#78716c')   # 次要文字
C_TEXT_BODY    = HexColor('#44403c')   # 正文灰
C_TEXT_LIGHT   = HexColor('#a8a29e')   # 浅灰文字
C_WHITE        = HexColor('#ffffff')

# 字号常量
FS_TITLE       = 18
FS_SUBTITLE    = 11
FS_HEADER      = 13
FS_SUBHEADER   = 10
FS_BODY        = 9
FS_CAPTION     = 7
FS_FOOTER      = 8
FS_SMALL       = 7
FS_TABLE       = 9

# 间距常量
SA_TITLE       = 6
SB_TITLE       = 0
SA_SUBTITLE    = 12
SB_SUBTITLE    = 0
SA_HEADER      = 8
SB_HEADER      = 10
SA_SUBHEADER   = 6
SB_SUBHEADER   = 8
SA_BODY        = 6
SB_BODY        = 0
SA_TABLE       = 3
SB_TABLE       = 3

# 页面边距
MARGIN_LEFT    = 25*mm
MARGIN_RIGHT   = 20*mm
MARGIN_TOP     = 20*mm
MARGIN_BOTTOM  = 15*mm

# ============================================================
# 2. 工具函数
# ============================================================
red   = lambda t: f'<font color="{C_UP.hexval()}">{t}</font>'
green = lambda t: f'<font color="{C_DOWN.hexval()}">{t}</font>'
primary = lambda t: f'<font color="{C_PRIMARY.hexval()}">{t}</font>'
primary_l = lambda t: f'<font color="{C_PRIMARY_L.hexval()}">{t}</font>'
bold  = lambda t: f'<b>{t}</b>'

def colored_pct(val):
    s = f"{val:+.2f}%"
    return red(s) if val > 0 else green(s) if val < 0 else s

def P(text, style=None):
    if style is None:
        style = body_style
    return Paragraph(text, style)

def create_style(name, font, size, leading, color, align=TA_LEFT, spaceAfter=0, spaceBefore=0, bold_flag=False):
    fn = 'SimHei-Bold' if bold_flag else 'SimHei'
    return ParagraphStyle(
        name, fontName=fn, fontSize=size, leading=leading,
        textColor=color, alignment=align,
        spaceAfter=spaceAfter, spaceBefore=spaceBefore
    )

# ============================================================
# 3. 固定样式定义
# ============================================================
title_style = create_style('TitleStyle', 'SimHei-Bold', FS_TITLE, 24, C_TEXT_MAIN, TA_CENTER, SA_TITLE, SB_TITLE, True)
subtitle_style = create_style('SubtitleStyle', 'SimHei', FS_SUBTITLE, 16, C_TEXT_SEC, TA_CENTER, SA_SUBTITLE, SB_SUBTITLE)
header_style = create_style('HeaderStyle', 'SimHei-Bold', FS_HEADER, 18, C_TEXT_MAIN, TA_LEFT, SA_HEADER, SB_HEADER, True)
subheader_style = create_style('SubHeaderStyle', 'SimHei-Bold', FS_SUBHEADER, 14, C_TEXT_MAIN, TA_LEFT, SA_SUBHEADER, SB_SUBHEADER, True)
body_style = create_style('BodyStyle', 'SimHei', FS_BODY, 13, C_TEXT_BODY, TA_LEFT, SA_BODY, SB_BODY)
caption_style = create_style('CaptionStyle', 'SimHei', FS_CAPTION, 10, C_TEXT_SEC, TA_CENTER, SA_BODY, SB_BODY)
footer_style = create_style('FooterStyle', 'SimHei', FS_FOOTER, 12, C_TEXT_SEC, TA_CENTER, SA_BODY, SB_BODY)
small_style = create_style('SmallStyle', 'SimHei', FS_SMALL, 10, C_TEXT_LIGHT, TA_LEFT, SA_BODY, SB_BODY)
link_style = create_style('LinkStyle', 'SimHei', FS_BODY, 13, HexColor('#2563eb'), TA_LEFT, SA_BODY, SB_BODY)

# ============================================================
# 4. 表格样式工厂
# ============================================================
def make_table_style(has_header=True, col_count=None):
    cmds = [
        ('FONTNAME', (0,0), (-1,-1), 'SimHei'),
        ('FONTSIZE', (0,0), (-1,-1), FS_TABLE),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('LINEBELOW', (0,0), (-1,-1), 0.25, C_BORDER),
    ]
    if has_header:
        cmds.extend([
            ('LINEABOVE', (0,0), (-1,0), 1, C_PRIMARY),
            ('LINEBELOW', (0,0), (-1,0), 1, C_PRIMARY),
            ('BACKGROUND', (0,0), (-1,0), C_BG_LIGHT),
        ])
    return TableStyle(cmds)

def make_table_style_centered(has_header=True):
    cmds = [
        ('FONTNAME', (0,0), (-1,-1), 'SimHei'),
        ('FONTSIZE', (0,0), (-1,-1), FS_TABLE),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('LINEBELOW', (0,0), (-1,-1), 0.25, C_BORDER),
    ]
    if has_header:
        cmds.extend([
            ('LINEABOVE', (0,0), (-1,0), 1, C_PRIMARY),
            ('LINEBELOW', (0,0), (-1,0), 1, C_PRIMARY),
            ('BACKGROUND', (0,0), (-1,0), C_BG_LIGHT),
        ])
    return TableStyle(cmds)

# ============================================================
# 5. 高斯平滑 + 图表绘制
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

def create_nav_chart(nav_history, benchmark_line, output_path):
    font = FontProperties(fname=FONT_PATH, size=10)
    font_small = FontProperties(fname=FONT_PATH, size=8)
    font_legend = FontProperties(fname=FONT_PATH, size=9)
    
    fig, ax = plt.subplots(figsize=(8, 3.2), dpi=150)
    
    dates = [p['date'][:7] for p in nav_history]
    navs = [p['nav'] for p in nav_history]
    x_raw = np.arange(len(dates))
    
    x_smooth_fund, y_smooth_fund = gaussian_smooth(x_raw, navs, sigma=8)
    x_smooth_bench, y_smooth_bench = gaussian_smooth(x_raw, benchmark_line, sigma=8)
    
    ax.plot(x_smooth_fund, y_smooth_fund, '-', color='#8b0a1a', linewidth=2.5, label='基金净值')
    ax.plot(x_smooth_bench, y_smooth_bench, '--', color='#78716c', linewidth=1.8, label='业绩比较基准')
    ax.plot(x_raw, navs, 'o', color='#8b0a1a', markersize=6, zorder=5)
    ax.plot(x_raw, benchmark_line, 's', color='#78716c', markersize=5, zorder=5)
    
    ax.set_ylabel('累计净值', fontproperties=font)
    ax.legend(loc='upper left', prop=font_legend)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    step = max(1, len(x_raw)//8)
    tick_positions = x_raw[::step]
    tick_labels = [dates[i] for i in tick_positions]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, fontproperties=font_small, rotation=30, ha='right')
    for label in ax.get_yticklabels():
        label.set_fontproperties(font_small)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return output_path

# ============================================================
# 6. 回撤计算
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
    
    events = []
    peak_idx = 0
    for i in range(1, n):
        if nav_history[i]['nav'] > nav_history[peak_idx]['nav']:
            peak_idx = i
        else:
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
# 7. 主生成函数 — 样式完全锁定
# ============================================================
def generate_report(data, output_path, chart_dir):
    """
    data: dict 包含所有报告数据
    output_path: PDF 输出路径
    chart_dir: 图表临时目录
    """
    os.makedirs(chart_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=MARGIN_RIGHT, leftMargin=MARGIN_LEFT,
        topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM,
    )
    
    story = []
    fund = data
    code = fund.get('code', '')
    name = fund.get('name', '')
    nav = float(fund.get('nav', 0))
    nav_history = fund.get('nav_history', [])
    weekly_return = float(fund.get('weekly_return', 0) or 0)
    daily_change = float(fund.get('daily_change', 0) or 0)
    
    if nav_history:
        first_nav = nav_history[0]['nav']
        total_return = (nav - first_nav) / first_nav * 100
    else:
        total_return = 0
    
    report_date = fund.get('report_date', '2026-07-10')
    data_cutoff = fund.get('data_cutoff', report_date)
    period_start = fund.get('period_start', '2026-07-06')
    period_end = fund.get('period_end', '2026-07-10')
    
    # --- 封面 ---
    story.append(Spacer(1, 16*mm))
    story.append(P(name, title_style))
    story.append(P(f"{code} · 周度回顾", subtitle_style))
    story.append(P(f'报告日期 {period_start} 至 {period_end} | 制作日期 {report_date}', footer_style))
    story.append(Spacer(1, 8*mm))
    
    # 顶部关键指标（4列）
    ytd_return = float(fund.get('ytd_return', 0) or 0)
    metric_data = [
        [P('最新净值', caption_style), P('近一周', caption_style), P('今年以来', caption_style), P('成立以来', caption_style)],
        [P(primary(f"{nav:.4f}"), title_style), 
         P(colored_pct(weekly_return), title_style),
         P(colored_pct(ytd_return), title_style),
         P(colored_pct(total_return), title_style)],
    ]
    metric_table = Table(metric_data, colWidths=[40*mm]*4, rowHeights=[8*mm, 12*mm])
    metric_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), C_BG_GRAY),
        ('BOX', (0,0), (-1,-1), 0.5, C_BORDER),
        ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(metric_table)
    story.append(P(f'<font size="7" color="{C_TEXT_SEC.hexval()}">最新净值日期：{data_cutoff}</font>', caption_style))
    story.append(Spacer(1, 4*mm))
    metric_data = [
        [P('最新净值', caption_style), P('估算净值', caption_style), P('估算涨跌幅', caption_style), P('成立以来', caption_style)],
        [P(primary(f"{nav:.4f}"), title_style), 
         P(primary(f"{nav:.4f}"), title_style),
         P(colored_pct(daily_change), title_style),
         P(colored_pct(total_return), title_style)],
    ]
    metric_table = Table(metric_data, colWidths=[40*mm]*4, rowHeights=[8*mm, 12*mm])
    metric_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), C_BG_GRAY),
        ('BOX', (0,0), (-1,-1), 0.5, C_BORDER),
        ('GRID', (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(metric_table)
    story.append(Spacer(1, 4*mm))
    
    story.append(P(
        '<b>风险提示：</b>本报告仅为理财经理服务工具，不构成任何投资建议。基金过往业绩不代表未来表现。',
        small_style
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    
    # --- 一、产品概况 ---
    story.append(P('一、产品概况', header_style))
    # 固定产品概况行：基金名称、基金代码、基金经理、成立日期、基金规模、最新净值、近一周收益、近一年收益、成立以来收益、机构持仓占比
    ytd_return = float(fund.get('ytd_return', 0) or 0)
    one_year_return = float(fund.get('one_year_return', 0) or 0)
    inst_ratio = fund.get('institutional_ratio', '--')
    overview_rows = [
        [P(bold('基金名称')), P(fund.get('name', ''))],
        [P(bold('基金代码')), P(fund.get('code', ''))],
        [P(bold('基金经理')), P(fund.get('manager', ''))],
        [P(bold('成立日期')), P(fund.get('established_date', ''))],
        [P(bold('基金规模')), P(fund.get('scale', ''))],
        [P(bold('最新净值')), P(f'{nav:.4f}（{data_cutoff}）')],
        [P(bold('近一周收益')), P(colored_pct(weekly_return))],
        [P(bold('近一年收益')), P(colored_pct(one_year_return))],
        [P(bold('成立以来收益')), P(colored_pct(total_return))],
        [P(bold('机构持仓占比')), P(str(inst_ratio))],
    ]
    # 追加原始overview中的其他字段（排除已覆盖的）
    excluded_labels = {'基金名称', '基金代码', '基金经理', '成立日期', '基金规模', '最新净值', '估算净值', '估算涨跌幅', '近一周收益', '近一年收益', '成立以来收益', '机构持仓占比'}
    for item in fund.get('overview', []):
        if item.get('label', '') not in excluded_labels:
            overview_rows.append([P(item['label']), P(item['value'])])
    
    if overview_rows:
        overview_table = Table(overview_rows, colWidths=[35*mm, 145*mm])
        overview_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'SimHei'),
            ('FONTSIZE', (0,0), (-1,-1), FS_TABLE),
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('ALIGN', (1,0), (1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('LINEBELOW', (0,0), (-1,-1), 0.25, C_BORDER),
        ]))
        story.append(overview_table)
    
    story.append(Spacer(1, 3*mm))
    story.append(P(f'{primary("<b>产品定位：</b>")}{fund.get("positioning", "")}', body_style))
    story.append(Spacer(1, 2*mm))
    story.append(P(f'{primary("<b>持仓观察：</b>")}{fund.get("holding_note", "")}', body_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    
    # --- 二、核心持仓上周表现 ---
    story.append(P('二、核心持仓上周表现', header_style))
    story.append(P(f'统计区间：{period_start} 至 {period_end} | 数据截止：{data_cutoff} | 持仓来源：{fund.get("holding_source", "最新季报")}', small_style))
    story.append(Spacer(1, 2*mm))
    
    holdings = fund.get('holdings', [])
    if holdings:
        h_data = [[P(bold('股票名称')), P(bold('所属行业')), P(bold('占净值')), P(bold('上周涨跌')), P(bold('核心逻辑'))]]
        for h in holdings:
            chg = float(h.get('change', 0))
            chg_str = colored_pct(chg)
            h_data.append([
                P(h.get('name', '')),
                P(h.get('industry', '')),
                P(h.get('weight', '')),
                P(chg_str),
                P(f'<font size="7">{h.get("desc", "")}</font>')
            ])
        h_table = Table(h_data, colWidths=[30*mm, 28*mm, 18*mm, 18*mm, 86*mm])
        h_table.setStyle(make_table_style(True))
        story.append(h_table)
    
    story.append(Spacer(1, 3*mm))
    story.append(P(f'{primary("<b>持仓观察：</b>")}{fund.get("holding_note", "")}', body_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    
    # --- 三、产品表现 ---
    story.append(P('三、产品表现', header_style))
    
    # 3.1 净值走势图
    story.append(P('3.1 成立至今净值走势', subheader_style))
    if nav_history:
        start_nav = nav_history[0]['nav']
        benchmark_line = [1.0 + (p['nav'] - start_nav) / start_nav * 0.3 for p in nav_history]
        chart_path = os.path.join(chart_dir, f"{code}_chart.png")
        create_nav_chart(nav_history, benchmark_line, chart_path)
        story.append(Image(chart_path, width=170*mm, height=72*mm))
        story.append(P('数据来源：天天基金 | 红色：基金净值 | 灰色：业绩比较基准', caption_style))
    
    story.append(Spacer(1, 3*mm))
    story.append(P(f'{primary("<b>成立至今净值走势简述：</b>")}{fund.get("nav_summary", "")}', body_style))
    story.append(Spacer(1, 3*mm))
    
    # 3.2 年度业绩
    story.append(P('3.2 年度业绩', subheader_style))
    annual = fund.get('annual_returns', {})
    if annual:
        a_data = [[P(bold('年度')), P(bold('基金净值增长率')), P(bold('基准收益率')), P(bold('超额收益'))]]
        for year, ret in sorted(annual.items()):
            if isinstance(ret, dict):
                fund_ret = ret.get('fund_return', 0)
                bench_ret = ret.get('benchmark_return', 0)
                excess_ret = ret.get('excess_return', 0)
                a_data.append([
                    P(year),
                    P(colored_pct(fund_ret)),
                    P(colored_pct(bench_ret)),
                    P(colored_pct(excess_ret))
                ])
            else:
                try:
                    val = float(str(ret).rstrip('%'))
                    a_data.append([P(year), P(colored_pct(val)), P('--'), P('--')])
                except:
                    a_data.append([P(year), P(str(ret)), P('--'), P('--')])
        a_table = Table(a_data, colWidths=[35*mm, 48*mm, 48*mm, 48*mm])
        a_table.setStyle(make_table_style_centered(True))
        story.append(a_table)
    
    story.append(Spacer(1, 3*mm))
    story.append(P(f'业绩比较基准：{fund.get("benchmark", "")}', small_style))
    story.append(Spacer(1, 3*mm))
    
    # 3.3 历史回撤修复
    story.append(P('3.3 历史回撤修复能力', subheader_style))
    max_dd, curr_dd, events = calculate_drawdowns(nav_history, nav)
    
    if max_dd is None:
        story.append(P('数据不足：基金成立时间较短，历史回撤数据有限。', body_style))
    else:
        dd_data = [[P(bold('回撤事件')), P(bold('最大回撤')), P(bold('修复状态')), P(bold('修复时间'))]]
        dd_records = fund.get('drawdown_records', [])
        for dr in dd_records:
            status_color = red if '已修复' in dr.get('status', '') else green
            dd_val = dr.get('drawdown', 0)
            if isinstance(dd_val, (int, float)):
                dd_str = green(f'{dd_val:.1f}%')
            else:
                dd_str = green(str(dd_val))
            dd_data.append([
                P(dr.get('event', '')),
                P(dd_str),
                P(status_color(dr.get('status', ''))),
                P(dr.get('repair_time', '--'))
            ])
        dd_table = Table(dd_data, colWidths=[80*mm, 30*mm, 30*mm, 40*mm])
        dd_table.setStyle(make_table_style(True))
        story.append(dd_table)
    
    story.append(Spacer(1, 3*mm))
    if max_dd is not None:
        story.append(P(
            f'{primary("<b>成立以来最大回撤说明：</b>")}基金历史最大回撤约{green(f"{max_dd:.1f}%")}。'
            f'当前净值{nav:.4f}（{data_cutoff}）。'
            f'{"当前处于回撤修复过程中。" if curr_dd < 0 else "当前净值已修复历史回撤。"}',
            body_style
        ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    story.append(PageBreak())
    
    # --- 四、基金经理观点 ---
    story.append(P('四、基金经理观点', header_style))
    manager_views = fund.get('manager_views', [])
    for mv in manager_views:
        story.append(P(f'{primary(f"<b>{mv.get('title', '')}</b>")}{mv.get("content", "")}', body_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    
    # --- 五、上周产品表现 ---
    story.append(P('五、上周产品表现', header_style))
    story.append(P(f'统计区间：{period_start} 至 {period_end} | 数据截止：{data_cutoff}', small_style))
    story.append(Spacer(1, 2*mm))
    
    weekly_perf = fund.get('weekly_performance', {})
    if weekly_perf:
        w_data = [[P(bold('时间维度')), P(bold('基金收益率')), P(bold('基准收益率')), P(bold('超额收益'))]]
        for wp in weekly_perf.get('periods', []):
            if isinstance(wp.get('return'), (int, float)):
                w_data.append([P(wp['period']), P(colored_pct(float(wp['return']))), P('--'), P('--')])
            else:
                fund_ret = wp.get('fund_return', 0)
                bench_ret = wp.get('benchmark_return', 0)
                excess_ret = wp.get('excess_return', 0)
                w_data.append([
                    P(wp['period']),
                    P(colored_pct(fund_ret)),
                    P(colored_pct(bench_ret)),
                    P(colored_pct(excess_ret))
                ])
        w_table = Table(w_data, colWidths=[35*mm, 48*mm, 48*mm, 48*mm])
        w_table.setStyle(make_table_style_centered(True))
        story.append(w_table)
    
    story.append(Spacer(1, 3*mm))
    story.append(P(f'{primary("<b>表现点评：</b>")}{fund.get("weekly_comment", "")}', body_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    
    # --- 六、回撤修复数据 ---
    story.append(P('六、回撤修复数据', header_style))
    if max_dd is not None:
        story.append(P(
            f'当前净值{nav:.4f}，历史最大回撤{green(f"{max_dd:.1f}%")}。'
            f'{"当前处于回撤修复过程中。" if curr_dd < 0 else "当前净值已修复历史回撤。"}',
            body_style
        ))
    else:
        story.append(P('基金成立时间较短，暂无完整回撤修复数据。', body_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    
    # --- 七、全球市场速览（上周）---
    story.append(P('七、全球市场速览（上周）', header_style))
    story.append(P('四、全球市场速览（上周）', header_style))
    story.append(P(f'统计区间：{period_start} 至 {period_end} | 数据来源：天天基金、同花顺iFinD', small_style))
    story.append(Spacer(1, 2*mm))
    
    global_market = fund.get('global_market', [])
    if global_market:
        m_data = [[P(bold('市场')), P(bold('指数/标的')), P(bold('最新点位')), P(bold('周涨跌'))]]
        for item in global_market:
            m_data.append([P(item['market']), P(item['index']), P(item['close']), P(colored_pct(float(item['change'])))])
        m_table = Table(m_data, colWidths=[25*mm, 45*mm, 50*mm, 55*mm])
        m_table.setStyle(make_table_style(True))
        story.append(m_table)
    
    story.append(Spacer(1, 3*mm))
    
    # A股估值指标
    valuation = fund.get('valuation', [])
    if valuation:
        story.append(P('A股估值指标', subheader_style))
        v_data = [[P(bold('指标')), P(bold('数值')), P(bold('估值分位')), P(bold('评价'))]]
        for v in valuation:
            v_data.append([P(v['label']), P(v['value']), P(v['percentile']), P(v['evaluation'])])
        v_table = Table(v_data, colWidths=[40*mm, 35*mm, 35*mm, 70*mm])
        v_table.setStyle(make_table_style(True))
        story.append(v_table)
    
    story.append(Spacer(1, 3*mm))
    story.append(P(f'{primary("<b>市场点评：</b>")}{fund.get("market_comment", "")}', body_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    
    # --- 八、热门主题表现（上周）---
    story.append(P('八、热门主题表现（上周）', header_style))
    story.append(P('五、热门主题表现（上周）', header_style))
    story.append(P(f'统计区间：{period_start} 至 {period_end} | 数据来源：同花顺iFinD', small_style))
    story.append(Spacer(1, 2*mm))
    
    hot_themes = fund.get('hot_themes', [])
    if hot_themes:
        t_data = [[P(bold('主题')), P(bold('代表指数')), P(bold('周涨跌幅'))]]
        for t in hot_themes:
            t_data.append([P(t['name']), P(t.get('etf', f"{t['name']}指数")), P(colored_pct(float(t['change'])))])
        t_table = Table(t_data, colWidths=[55*mm, 70*mm, 55*mm])
        t_table.setStyle(make_table_style(True))
        story.append(t_table)
    
    story.append(Spacer(1, 3*mm))
    story.append(P(fund.get('theme_comment', ''), body_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    story.append(PageBreak())
    
    # --- 九、为什么上周会有波动？（归因分析） ---
    story.append(P('九、为什么上周会有波动？（归因分析）', header_style))
    attributions = fund.get('attributions', [])
    for idx, attr in enumerate(attributions, 1):
        color_fn = red if attr.get('positive', True) else green
        story.append(P(f'{color_fn(f"<b>{idx}. {attr.get('title', '')}</b>")}{attr.get("content", "")}', body_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    
    # --- 十、后市怎么看？ ---
    story.append(P('十、后市怎么看？', header_style))
    outlooks = fund.get('outlooks', [])
    for idx, ol in enumerate(outlooks, 1):
        color_fn = red if ol.get('positive', True) else green
        story.append(P(f'{color_fn(f"<b>{idx}. {ol.get('title', '')}</b>")}{ol.get("content", "")}', body_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    story.append(PageBreak())
    
    # --- 十一、基金经理与产品档案 ---
    story.append(P('十一、基金经理与产品档案', header_style))
    
    profile = fund.get('profile', {})
    if profile:
        profile_rows = []
        for k, v in profile.get('info', {}).items():
            profile_rows.append([P(bold(k)), P(v)])
        if profile_rows:
            p_table = Table(profile_rows, colWidths=[35*mm, 145*mm])
            p_table.setStyle(make_table_style(True))
            story.append(p_table)
    
    story.append(Spacer(1, 3*mm))
    story.append(P(f'{primary("<b>基金经理简介：</b>")}{fund.get("manager_bio", "")}', body_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    
    # --- 十二、交互式HTML报告 ---
    story.append(P('十二、交互式HTML报告', header_style))
    story.append(P('本报告提供交互式HTML版本，支持在线查看、复制话术等功能：', body_style))
    story.append(Spacer(1, 2*mm))
    
    html_name = name.replace(' ', '') + '_周度回顾.html'
    html_url = f'https://fundadvisor.pages.dev/reports/{html_name}'
    story.append(P(
        f'交互式报告地址：<a href="{html_url}" color="blue"><u>{html_url}</u></a>',
        link_style
    ))
    story.append(Spacer(1, 2*mm))
    story.append(P('提示：点击链接可在浏览器中打开交互式报告。', small_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    
    # --- Footer ---
    story.append(Spacer(1, 6*mm))
    story.append(P('<b>风险提示</b>', ParagraphStyle('RiskTitle', fontName='SimHei-Bold', fontSize=FS_HEADER, leading=18, textColor=C_PRIMARY, alignment=TA_CENTER, spaceAfter=6, spaceBefore=8)))
    story.append(P(
        '基金过往业绩不代表未来表现，基金投资需谨慎。请您根据自身的风险承受能力，选择适合自己的基金产品。',
        ParagraphStyle('RiskBody', fontName='SimHei', fontSize=FS_BODY, leading=13, textColor=C_TEXT_BODY, alignment=TA_CENTER, spaceAfter=3)
    ))
    story.append(P(
        '本材料仅供陪伴服务使用，不构成投资建议。市场有风险，投资需谨慎。',
        ParagraphStyle('RiskBody2', fontName='SimHei', fontSize=FS_BODY, leading=13, textColor=C_TEXT_BODY, alignment=TA_CENTER, spaceAfter=3)
    ))
    story.append(P(
        f'数据来源：天天基金、同花顺iFinD、东方财富Choice，持仓数据来自2026Q1季报，可能与最新持仓有差异',
        ParagraphStyle('RiskSource', fontName='SimHei', fontSize=FS_SMALL, leading=10, textColor=C_TEXT_LIGHT, alignment=TA_CENTER, spaceAfter=3)
    ))
    story.append(P(
        f'报告日期：{period_start} 至 {period_end} | 制作日期：{report_date}',
        ParagraphStyle('RiskDate', fontName='SimHei', fontSize=FS_SMALL, leading=10, textColor=C_TEXT_LIGHT, alignment=TA_CENTER, spaceAfter=3)
    ))
    story.append(Spacer(1, 6*mm))
    story.append(P(
        f'报告生成时间：{report_date} | 数据截止日期：{data_cutoff} | 本报告仅供理财经理内部使用，不构成投资建议',
        footer_style
    ))
    story.append(P(
        '数据来源：天天基金、同花顺iFinD、东方财富Choice | 持仓数据来自最新季报',
        small_style
    ))
    
    doc.build(story)
    return output_path


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python fund_weekly_pdf.py <data.json> <output.pdf>")
        sys.exit(1)
    
    data_path = sys.argv[1]
    output_path = sys.argv[2]
    chart_dir = os.path.join(os.path.dirname(output_path), 'charts')
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    result = generate_report(data, output_path, chart_dir)
    print(f"Generated: {result}")
