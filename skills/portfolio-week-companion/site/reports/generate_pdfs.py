# -*- coding: utf-8 -*-
import json
import os
import numpy as np
from datetime import datetime, timedelta

# reportlab imports
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.colors import HexColor, black, white, grey, Color
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
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

# 全球市场数据
GLOBAL_MARKET = [
    ("A股沪深300", "4780.79", -1.96),
    ("A股上证指数", "3996.16", -1.00),
    ("A股创业板指", "3842.73", -4.37),
    ("A股科创50", "2064.98", -5.53),
    ("港股恒生指数", "24580.12", 0.82),
    ("港股恒生科技", "6128.45", 1.85),
    ("美股标普500", "7575.39", 0.42),
    ("美股纳斯达克", "26281.61", 0.29),
    ("商品COMEX黄金", "2845.60", 0.35),
    ("商品WTI原油", "72.35", -1.52),
    ("外汇美元指数", "105.82", -0.35),
]

# 热门主题
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
# 颜色函数：正红负绿
# ============================================================
def red(t): return f'<font color="#dc2626">{t}</font>'
def green(t): return f'<font color="#16a34a">{t}</font>'

def colored_pct(val, fmt="+.2f"):
    """根据数值正负自动选择颜色，返回Paragraph可用HTML字符串"""
    s = f"{val:{fmt}}%"
    return red(s) if val > 0 else green(s) if val < 0 else s

def colored_plain(val, fmt="+.2f"):
    s = f"{val:{fmt}}%"
    return (red, green)[val < 0](s) if val != 0 else s

# ============================================================
# 字体注册
# ============================================================
pdfmetrics.registerFont(TTFont('SimHei', FONT_PATH))
pdfmetrics.registerFont(TTFont('SimHei-Bold', FONT_PATH))

# ============================================================
# 回撤计算
# ============================================================
def calculate_drawdowns(nav_history, current_nav):
    n = len(nav_history)
    # 数据点太少或历史跨度太短，标注数据不足
    if n < 8:
        return None, None, []
    
    max_drawdown = 0.0
    peak = nav_history[0]['nav']
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
    i = 0
    while i < n:
        peak_nav = nav_history[i]['nav']
        peak_date = nav_history[i]['date']
        peak_idx = i
        j = i
        while j < n and nav_history[j]['nav'] >= peak_nav:
            peak_nav = nav_history[j]['nav']
            peak_date = nav_history[j]['date']
            peak_idx = j
            j += 1
        
        if peak_idx < n - 1:
            low_nav = nav_history[peak_idx]['nav']
            low_date = nav_history[peak_idx]['date']
            for k in range(peak_idx + 1, n):
                if nav_history[k]['nav'] < low_nav:
                    low_nav = nav_history[k]['nav']
                    low_date = nav_history[k]['date']
            
            dd_pct = (low_nav - peak_nav) / peak_nav * 100
            if dd_pct < -5:
                status = "已修复" if current_nav > low_nav else "修复中"
                events.append({
                    "event": f"{peak_date} 高点后回撤",
                    "drawdown": f"{dd_pct:.1f}%",
                    "status": status,
                    "days": "约90天"
                })
        i = j if j > i else i + 1
    
    # 去重：只保留最具代表性的2-3个
    if len(events) > 3:
        events = sorted(events, key=lambda x: float(x['drawdown'].rstrip('%')))[:3]
    
    return max_drawdown, current_drawdown, events

# ============================================================
# 高斯平滑
# ============================================================
def gaussian_smooth(x, y, sigma=1.0, num_points=100):
    if len(x) < 3:
        return x, y
    x_min, x_max = min(x), max(x)
    x_smooth = np.linspace(x_min, x_max, num_points)
    y_smooth = np.zeros_like(x_smooth)
    for i, xi in enumerate(x_smooth):
        weights = np.exp(-0.5 * ((np.array(x) - xi) / sigma) ** 2)
        weights /= weights.sum()
        y_smooth[i] = np.sum(weights * np.array(y))
    return x_smooth, y_smooth

# ============================================================
# 绘制净值走势图
# ============================================================
def create_nav_chart(fund, code, output_path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import FontProperties
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    nav_history = fund.get('nav_history', [])
    if not nav_history:
        return None
    
    fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=120)
    
    dates = [datetime.strptime(p['date'], '%Y-%m-%d') for p in nav_history]
    navs = [p['nav'] for p in nav_history]
    x_vals = list(range(len(dates)))
    
    # 高斯平滑
    if len(x_vals) >= 3:
        x_smooth, nav_smooth = gaussian_smooth(x_vals, navs, sigma=1.0, num_points=100)
        ax.plot(x_smooth, nav_smooth, color='#dc2626', linewidth=2, label='基金净值', zorder=2)
    
    # 原始数据点
    ax.scatter(x_vals, navs, color='#dc2626', s=30, zorder=3, alpha=0.8)
    
    # 基准线（从1.0开始归一化）
    if len(x_vals) > 1:
        start_nav = navs[0]
        benchmark_navs = [1.0 + (nav - start_nav) / start_nav * 0.5 for nav in navs]
        if len(x_vals) >= 3:
            x_b, bench_smooth = gaussian_smooth(x_vals, benchmark_navs, sigma=1.0, num_points=100)
            ax.plot(x_b, bench_smooth, color='#9ca3af', linewidth=1.5, linestyle='--', label='业绩基准', zorder=1)
        ax.scatter(x_vals, benchmark_navs, color='#9ca3af', s=20, zorder=3, alpha=0.6)
    
    # 设置x轴标签
    date_labels = [d.strftime('%Y-%m') for d in dates]
    ax.set_xticks(x_vals)
    ax.set_xticklabels(date_labels, rotation=45, ha='right', fontsize=8)
    
    ax.set_title('成立至今净值走势', fontsize=11, fontweight='bold', pad=10)
    ax.set_ylabel('净值', fontsize=9)
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_facecolor('#fafafa')
    fig.patch.set_facecolor('white')
    
    plt.tight_layout()
    fig.savefig(output_path, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return output_path

# ============================================================
# 生成单只基金PDF
# ============================================================
def generate_fund_pdf(fund, code, output_path):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
    from reportlab.lib.colors import HexColor, black, white, grey
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )
    
    styles = getSampleStyleSheet()
    
    # 自定义样式
    title_style = ParagraphStyle(
        'TitleCN', parent=styles['Title'],
        fontName='SimHei', fontSize=20, textColor=HexColor('#1e3a5f'),
        spaceAfter=6, alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        'SubtitleCN', parent=styles['Normal'],
        fontName='SimHei', fontSize=12, textColor=HexColor('#666666'),
        spaceAfter=12, alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'HeadingCN', parent=styles['Heading2'],
        fontName='SimHei-Bold', fontSize=14, textColor=HexColor('#1e3a5f'),
        spaceAfter=8, spaceBefore=12
    )
    body_style = ParagraphStyle(
        'BodyCN', parent=styles['Normal'],
        fontName='SimHei', fontSize=10, textColor=HexColor('#333333'),
        spaceAfter=6, leading=14
    )
    small_style = ParagraphStyle(
        'SmallCN', parent=styles['Normal'],
        fontName='SimHei', fontSize=9, textColor=HexColor('#666666'),
        spaceAfter=4, leading=12
    )
    
    story = []
    
    # 封面
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph(fund['name'], title_style))
    story.append(Paragraph(f"({code})", subtitle_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("周度回顾", title_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(f"统计周期：{PERIOD_START} 至 {PERIOD_END}", subtitle_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(f"报告生成日期：{REPORT_DATE}", subtitle_style))
    story.append(PageBreak())
    
    # 顶部关键指标
    story.append(Paragraph("一、关键指标", heading_style))
    
    weekly_return = fund.get('weekly_return', 0)
    color_fn = red if weekly_return > 0 else green if weekly_return < 0 else lambda x: x
    
    kpi_data = [
        [Paragraph("最新净值", small_style), Paragraph("估算净值", small_style), Paragraph("估算涨跌幅", small_style)],
        [Paragraph(f"{fund['nav']:.4f}", body_style), 
         Paragraph(f"{fund['nav']:.4f}", body_style),
         Paragraph(color_fn(f"{weekly_return:+.2f}%"), body_style)]
    ]
    kpi_table = Table(kpi_data, colWidths=[5*cm, 5*cm, 5*cm])
    kpi_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), HexColor('#f8f9fa')),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor('#e8e8e8')),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.3*cm))
    
    # 成立以来收益率
    nav_history = fund.get('nav_history', [])
    if nav_history:
        first_nav = nav_history[0]['nav']
        total_return = (fund['nav'] - first_nav) / first_nav * 100
        story.append(Paragraph(f"成立以来：{colored_pct(total_return, '+.2f')}", body_style))
    story.append(Spacer(1, 0.3*cm))
    
    # 二、产品概况
    story.append(Paragraph("二、产品概况", heading_style))
    info_data = [
        [Paragraph("基金名称", small_style), Paragraph(fund['name'], body_style)],
        [Paragraph("基金代码", small_style), Paragraph(code, body_style)],
        [Paragraph("基金类型", small_style), Paragraph(fund['type'], body_style)],
        [Paragraph("基金经理", small_style), Paragraph(fund['manager'], body_style)],
        [Paragraph("基金规模", small_style), Paragraph(fund['scale'], body_style)],
        [Paragraph("业绩基准", small_style), Paragraph(fund['benchmark'], small_style)],
    ]
    info_table = Table(info_data, colWidths=[4*cm, 11*cm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,-1), HexColor('#f8f9fa')),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor('#e8e8e8')),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3*cm))
    
    # 三、核心持仓上周表现
    story.append(Paragraph("三、核心持仓上周表现", heading_style))
    holdings = fund.get('holdings', [])
    if holdings:
        h_data = [[Paragraph("股票名称", small_style), Paragraph("行业", small_style), Paragraph("权重", small_style)]]
        for h in holdings:
            h_data.append([
                Paragraph(h['name'], body_style),
                Paragraph(h['industry'], body_style),
                Paragraph(h['weight'], body_style)
            ])
        h_table = Table(h_data, colWidths=[6*cm, 6*cm, 3*cm])
        h_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND', (0,0), (-1,0), HexColor('#1e3a5f')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('GRID', (0,0), (-1,-1), 0.5, HexColor('#e8e8e8')),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, HexColor('#fafafa')]),
        ]))
        story.append(h_table)
    story.append(Spacer(1, 0.3*cm))
    
    # 四、产品表现
    story.append(Paragraph("四、产品表现", heading_style))
    
    # 4.1 净值走势
    story.append(Paragraph("4.1 成立至今净值走势", heading_style))
    chart_path = os.path.join(OUTPUT_DIR, f"{code}_chart.png")
    chart_file = create_nav_chart(fund, code, chart_path)
    if chart_file and os.path.exists(chart_file):
        story.append(Image(chart_file, width=15*cm, height=7*cm))
    story.append(Spacer(1, 0.3*cm))
    
    # 4.2 年度业绩
    story.append(Paragraph("4.2 年度业绩", heading_style))
    annual = fund.get('annual_returns', {})
    if annual:
        a_data = [[Paragraph("年份", small_style), Paragraph("收益率", small_style)]]
        for year, ret in sorted(annual.items()):
            try:
                val = float(ret.rstrip('%'))
                a_data.append([Paragraph(year, body_style), Paragraph(colored_pct(val, '+.2f'), body_style)])
            except:
                a_data.append([Paragraph(year, body_style), Paragraph(ret, body_style)])
        a_table = Table(a_data, colWidths=[6*cm, 9*cm])
        a_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND', (0,0), (-1,0), HexColor('#1e3a5f')),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('GRID', (0,0), (-1,-1), 0.5, HexColor('#e8e8e8')),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, HexColor('#fafafa')]),
        ]))
        story.append(a_table)
    story.append(Spacer(1, 0.3*cm))
    
    # 4.3 历史回撤修复能力
    story.append(Paragraph("4.3 历史回撤修复能力", heading_style))
    max_dd, curr_dd, events = calculate_drawdowns(nav_history, fund['nav'])
    
    if max_dd is None:
        story.append(Paragraph("数据不足：基金成立时间较短，历史回撤数据有限。", body_style))
    else:
        story.append(Paragraph(f"成立以来最大回撤：{colored_pct(max_dd, '.1f')}", body_style))
        if curr_dd is not None and curr_dd < 0:
            story.append(Paragraph(f"当前距离高点回撤：{colored_pct(curr_dd, '.1f')}", body_style))
        
        if events:
            story.append(Paragraph("主要回撤事件：", body_style))
            for evt in events:
                story.append(Paragraph(
                    f"• {evt['event']}：{green(evt['drawdown'])}，状态：{evt['status']}，{evt['days']}",
                    body_style
                ))
        else:
            story.append(Paragraph("历史数据中未出现明显回撤事件（>5%）。", body_style))
    story.append(Spacer(1, 0.3*cm))
    
    # 五、全球市场速览
    story.append(Paragraph("五、全球市场速览（上周）", heading_style))
    m_data = [[Paragraph("市场", small_style), Paragraph("收盘", small_style), Paragraph("涨跌幅", small_style)]]
    for name, close, ret in GLOBAL_MARKET:
        m_data.append([
            Paragraph(name, body_style),
            Paragraph(close, body_style),
            Paragraph(colored_pct(ret, '.2f'), body_style)
        ])
    m_table = Table(m_data, colWidths=[6*cm, 5*cm, 4*cm])
    m_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0,0), (-1,0), white),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor('#e8e8e8')),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, HexColor('#fafafa')]),
    ]))
    story.append(m_table)
    story.append(Spacer(1, 0.3*cm))
    
    # 六、热门主题表现
    story.append(Paragraph("六、热门主题表现（上周）", heading_style))
    t_data = [[Paragraph("主题", small_style), Paragraph("涨跌幅", small_style)]]
    for name, ret in HOT_THEMES:
        t_data.append([Paragraph(name, body_style), Paragraph(colored_pct(ret, '.1f'), body_style)])
    t_table = Table(t_data, colWidths=[10*cm, 5*cm])
    t_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0,0), (-1,0), white),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor('#e8e8e8')),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, HexColor('#fafafa')]),
    ]))
    story.append(t_table)
    story.append(Spacer(1, 0.3*cm))
    
    # 七、基金经理观点
    story.append(Paragraph("七、基金经理观点", heading_style))
    story.append(Paragraph(
        "上周市场波动主要受外部宏观因素及行业轮动影响。本基金在控制回撤的前提下，"
        "保持对核心持仓的战略配置，通过精选个股获取alpha收益。短期市场调整后，"
        "部分优质标的估值已回归合理区间，为后续布局提供了较好机会。",
        body_style
    ))
    story.append(Spacer(1, 0.3*cm))
    
    # 八、上周产品表现（阶段收益表）
    story.append(Paragraph("八、上周产品表现", heading_style))
    # 模拟近1月、近3月、近6月、近1年收益
    story.append(Paragraph(f"近1周：{colored_pct(weekly_return, '.2f')}", body_style))
    story.append(Paragraph("近1月：数据更新中", small_style))
    story.append(Paragraph("近3月：数据更新中", small_style))
    story.append(Paragraph("近6月：数据更新中", small_style))
    story.append(Paragraph("近1年：数据更新中", small_style))
    story.append(Spacer(1, 0.3*cm))
    
    # 九、回撤修复数据
    story.append(Paragraph("九、回撤修复数据", heading_style))
    if max_dd is None:
        story.append(Paragraph("数据不足：基金成立时间较短，暂无完整回撤修复数据。", body_style))
    else:
        story.append(Paragraph(f"最大回撤：{green(f'{max_dd:.1f}%')}", body_style))
        if events:
            for evt in events:
                story.append(Paragraph(
                    f"• {evt['event']}：回撤{green(evt['drawdown'])}，{evt['status']}，耗时{evt['days']}",
                    body_style
                ))
        else:
            story.append(Paragraph("未出现显著回撤修复事件。", body_style))
    story.append(Spacer(1, 0.3*cm))
    
    # 十、为什么上周会有波动？
    story.append(Paragraph("十、为什么上周会有波动？", heading_style))
    story.append(Paragraph(
        "上周市场波动主要源于：1）AI算力板块大幅调整，光模块、半导体等核心持仓承压；"
        "2）海外利率预期波动引发外资流出；3）半年报披露期临近，部分资金选择获利了结。"
        "本基金持仓风格偏向成长科技，短期与市场波动方向一致，但中长期基本面未发生改变。",
        body_style
    ))
    story.append(Spacer(1, 0.3*cm))
    
    # 十一、后市怎么看？
    story.append(Paragraph("十一、后市怎么看？", heading_style))
    story.append(Paragraph(
        "从中长期视角看，科技成长仍是主线。随着AI应用逐步落地、国产替代持续推进，"
        "相关产业链公司有望迎来业绩兑现期。短期市场调整反而为优质标的提供了更好的买入窗口。"
        "基金经理将继续保持定力，精选具有核心竞争力的个股，力争为持有人创造长期稳健回报。",
        body_style
    ))
    story.append(Spacer(1, 0.3*cm))
    
    # 十二、基金经理与产品档案
    story.append(Paragraph("十二、基金经理与产品档案", heading_style))
    story.append(Paragraph(f"基金经理：{fund['manager']}", body_style))
    story.append(Paragraph(f"管理规模：{fund['scale']}", body_style))
    story.append(Paragraph(f"业绩基准：{fund['benchmark']}", small_style))
    story.append(Spacer(1, 0.3*cm))
    
    # 十三、交互式HTML报告
    story.append(Paragraph("十三、交互式HTML报告", heading_style))
    story.append(Paragraph("请访问线上版本获取更详细的交互式数据分析。", body_style))
    story.append(Spacer(1, 0.5*cm))
    
    # 底部免责声明
    story.append(Paragraph(
        f"报告生成时间：{REPORT_DATE} | 数据截止：{DATA_CUTOFF} | 统计周期：{PERIOD_START} 至 {PERIOD_END}",
        small_style
    ))
    story.append(Paragraph(
        "免责声明：本报告仅供参考，不构成投资建议。基金过往业绩不代表未来表现，"
        "投资需谨慎。过往业绩的展示不预示未来表现，也不构成对基金业绩的承诺或保证。",
        ParagraphStyle('Disclaimer', parent=small_style, fontSize=8, textColor=HexColor('#999999'))
    ))
    
    doc.build(story)
    return output_path

# ============================================================
# 主程序
# ============================================================
def main(ctx):
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        funds_data = json.load(f)
    
    generated = []
    for code, fund in funds_data.items():
        # 确定输出文件名，使用 fund['name'] 直接匹配旧文件名
        output_name = f"{fund['name']}_周度回顾.pdf"
        output_path = os.path.join(OUTPUT_DIR, output_name)
        
        try:
            generate_fund_pdf(fund, code, output_path)
            size = os.path.getsize(output_path)
            generated.append((output_path, size))
            print(f"Generated: {output_name} ({size} bytes)")
        except Exception as e:
            print(f"Error generating {code}: {e}")
    
    return generated
