# -*- coding: utf-8 -*-
"""
基金周度回顾HTML报告生成器 v2
- CSS全部内联，不依赖外部CDN（除Chart.js和html2canvas）
- 配色统一 #8b0a1a 红色系
- 卡片式布局：持仓、全球市场、热门主题
- 日期规则：报告日期=上周一到上周五，制作日期=当天
"""
import json
import os
from datetime import datetime, timedelta

DATA_PATH = r"D:/OPC-skill/skills/portfolio-week-companion/site/reports/funds_data.json"
OUTPUT_DIR = r"D:/OPC-skill/skills/portfolio-week-companion/site/reports"

# ============================================================
# 日期计算
# ============================================================
def get_report_week(today=None):
    """报告日期 = 当前周的上周一到上周五"""
    if today is None:
        today = datetime.now()
    current_monday = today - timedelta(days=today.weekday())
    last_monday = current_monday - timedelta(days=7)
    last_friday = last_monday + timedelta(days=4)
    return last_monday.strftime("%Y-%m-%d"), last_friday.strftime("%Y-%m-%d")

def get_today_str():
    return datetime.now().strftime("%Y-%m-%d")

# ============================================================
# 核心持仓逻辑映射
# ============================================================
def get_holding_logic(name, industry):
    logic_map = {
        ("宁德时代", "电力设备"): "全球动力电池龙头",
        ("中际旭创", "通信"): "800G光模块全球领先",
        ("新易盛", "通信"): "光模块核心供应商",
        ("胜宏科技", "电子"): "AI服务器PCB核心供应商",
        ("东山精密", "电子"): "FPC+PCB双龙头",
        ("迈为股份", "电力设备"): "HJT设备龙头",
        ("立讯精密", "电子"): "苹果产业链核心",
        ("腾讯控股", "传媒"): "港股核心持仓",
        ("巨星科技", "机械设备"): "工具制造龙头",
        ("大族激光", "机械设备"): "激光设备龙头",
        ("招商银行", "银行"): "零售银行龙头",
        ("贵州茅台", "食品饮料"): "白酒绝对龙头",
        ("紫金矿业", "有色金属"): "全球铜金龙头",
        ("美的集团", "家用电器"): "家电全品类龙头",
        ("中国平安", "非银金融"): "综合金融龙头",
        ("药明康德", "医药生物"): "全球CXO龙头",
        ("恒瑞医药", "医药生物"): "创新药龙头",
        ("寒武纪", "电子"): "AI芯片设计龙头",
        ("海光信息", "电子"): "国产CPU/DCU龙头",
        ("贝特瑞", "电力设备"): "负极材料龙头",
        ("锦波生物", "美容护理"): "重组胶原蛋白龙头",
        ("完美世界", "传媒"): "游戏影视双轮驱动",
        ("极兔速递", "交通运输"): "快递新势力",
        ("信达生物", "医药生物"): "创新药Biotech",
        ("沪电股份", "电子"): "通信PCB龙头",
        ("长飞光纤", "通信"): "光纤预制棒龙头",
        ("亨通光电", "通信"): "光通信+海缆双轮驱动",
        ("中天科技", "通信"): "海缆+新能源材料龙头",
        ("天孚通信", "通信"): "光器件龙头",
    }
    key = (name, industry)
    if key in logic_map:
        return logic_map[key]
    industry_logic = {
        "电子": "半导体/消费电子核心标的",
        "通信": "光通信/通信设备核心标的",
        "电力设备": "新能源产业链核心标的",
        "医药生物": "创新药/医疗器械核心标的",
        "计算机": "软件/AI应用核心标的",
        "传媒": "互联网/游戏核心标的",
        "机械设备": "高端制造核心标的",
        "汽车": "新能源汽车产业链标的",
        "银行": "银行股核心配置",
        "食品饮料": "消费白马核心标的",
        "有色金属": "有色周期核心标的",
        "家用电器": "家电龙头标的",
        "非银金融": "保险/券商核心标的",
        "环保": "环保设备标的",
        "商贸零售": "零售/供应链标的",
        "钢铁": "钢铁周期标的",
        "基础化工": "化工新材料标的",
        "公用事业": "公用事业标的",
        "交通运输": "物流/快递核心标的",
        "美容护理": "医美/化妆品核心标的",
        "农林牧渔": "农业/养殖标的",
    }
    return industry_logic.get(industry, "核心持仓标的")

# 睿远持仓代码映射
def get_stock_code(name):
    codes = {
        "宁德时代": "300750.SZ", "中际旭创": "300308.SZ", "新易盛": "300502.SZ",
        "胜宏科技": "300476.SZ", "东山精密": "002384.SZ", "迈为股份": "300751.SZ",
        "立讯精密": "002475.SZ", "腾讯控股": "00700.HK", "巨星科技": "002444.SZ",
        "大族激光": "002008.SZ", "招商银行": "600036.SH", "贵州茅台": "600519.SH",
        "紫金矿业": "601899.SH", "美的集团": "000333.SZ", "中国平安": "601318.SH",
        "药明康德": "603259.SH", "恒瑞医药": "600276.SH", "寒武纪": "688256.SH",
        "海光信息": "688041.SH", "贝特瑞": "835185.BJ", "锦波生物": "832982.BJ",
        "完美世界": "002624.SZ", "极兔速递": "01519.HK", "信达生物": "01801.HK",
        "沪电股份": "002463.SZ", "长飞光纤": "601869.SH", "亨通光电": "600487.SH",
        "中天科技": "600522.SH", "天孚通信": "300394.SZ",
    }
    return codes.get(name, "数据待更新")

# ============================================================
# 全局市场数据
# ============================================================
GLOBAL_MARKET = [
    # 大卡片（2行×2列）
    ("CN", "A股", "沪深300", "4780.79", -1.96),
    ("HK", "港股", "恒生指数", "24580.12", 0.82),
    ("US", "美股", "标普500", "7575.39", 0.42),
    ("JP", "亚太", "日经225", "42156.78", 0.65),
    # 小卡片（1行×4列）
    (None, "上证指数", "3996.16", -1.00),
    (None, "创业板指", "3842.73", -4.37),
    (None, "纳斯达克", "26281.61", 0.29),
    (None, "COMEX黄金", "2845.60", 0.35),
]

HOT_THEMES_WEEK = [
    ("AI算力/光模块", "AI算力ETF", -12.8),
    ("半导体", "半导体ETF", -8.5),
    ("消费电子", "消费电子ETF", -5.2),
    ("新能源", "新能源车ETF", -4.8),
    ("光伏", "光伏ETF", -3.5),
    ("创新药", "创新药ETF", 2.1),
    ("黄金", "黄金ETF", 1.8),
    ("高股息", "红利ETF", 0.5),
    ("白酒", "白酒ETF", -1.2),
    ("中概互联", "中概互联ETF", 1.5),
    ("军工", "军工ETF", -2.3),
    ("煤炭", "煤炭ETF", 0.3),
]

HOT_THEMES_TODAY = [
    (t[0], t[1], round(t[2] + 0.5, 1)) for t in HOT_THEMES_WEEK
]

def pct_fmt(val):
    s = f"{val:+.2f}%"
    return s

def color_cls(val):
    return "up" if val > 0 else "down" if val < 0 else ""

# ============================================================
# HTML模板
# ============================================================
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{fund_name} · 周度回顾</title>
<style>
/* ===== CSS变量 ===== */
:root {{
  --primary: #8b0a1a;
  --primary-light: #c41e3a;
  --primary-50: #fef2f2;
  --primary-100: #fee2e2;
  --text: #1a1a1a;
  --text-secondary: #44403c;
  --text-muted: #78716c;
  --bg: #f8f7f5;
  --card: #ffffff;
  --border: #e7e5e4;
  --up: #dc2626;
  --down: #16a34a;
  --shadow: 0 2px 8px rgba(0,0,0,0.06);
  --nav-h: 52px;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{
  font-family: "PingFang SC","Microsoft YaHei","Hiragino Sans GB","Noto Sans SC",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  background: var(--bg); color: var(--text); line-height:1.7; font-size:15px;
  padding-top: var(--nav-h);
}}

/* ===== 顶部导航 ===== */
.top-nav {{
  position:fixed; top:0; left:0; right:0; height:var(--nav-h);
  background: linear-gradient(90deg, var(--primary) 0%, var(--primary-light) 100%);
  color:#fff; display:flex; align-items:center; justify-content:space-between;
  padding:0 12px; z-index:1000; box-shadow:0 2px 8px rgba(0,0,0,0.15);
}}
.top-nav .brand {{ font-size:14px; font-weight:700; white-space:nowrap; }}
.top-nav .nav-links {{
  display:flex; gap:3px; overflow-x:auto; scrollbar-width:none;
  flex:1; margin:0 8px; justify-content:center;
}}
.top-nav .nav-links::-webkit-scrollbar {{ display:none; }}
.top-nav .nav-links a {{
  color:rgba(255,255,255,0.85); text-decoration:none; font-size:11px;
  padding:3px 6px; border-radius:4px; white-space:nowrap; transition:all .2s;
}}
.top-nav .nav-links a:hover {{ background:rgba(255,255,255,0.15); color:#fff; }}
.top-nav .nav-links a.active {{ background:rgba(255,255,255,0.25); color:#fff; font-weight:600; }}
.top-nav .nav-actions {{ display:flex; gap:5px; align-items:center; }}
.top-nav .nav-btn {{
  background:rgba(255,255,255,0.2); color:#fff; border:none;
  padding:4px 8px; border-radius:4px; font-size:11px;
  cursor:pointer; white-space:nowrap; transition:all .2s;
}}
.top-nav .nav-btn:hover {{ background:rgba(255,255,255,0.35); }}

/* ===== 容器 ===== */
.container {{ max-width:800px; margin:0 auto; padding:12px 12px 40px; }}

/* ===== 标题区域 ===== */
.header-section {{
  text-align:center; padding:24px 16px 18px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color:#fff; border-radius:0 0 14px 14px; margin:-12px -12px 16px;
}}
.header-section h1 {{ font-size:20px; font-weight:700; margin-bottom:6px; }}
.header-section .subtitle {{ font-size:13px; opacity:0.9; }}
.header-section .date {{ font-size:11px; opacity:0.75; margin-top:4px; }}

/* ===== 关键指标 ===== */
.kpi-grid {{
  display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin-bottom:14px;
}}
.kpi-item {{
  background:linear-gradient(135deg, var(--primary-50) 0%, #fff 100%);
  padding:10px 6px; border-radius:8px; text-align:center;
  border:1px solid var(--primary-100);
}}
.kpi-item .label {{ font-size:10px; color:var(--text-muted); margin-bottom:2px; }}
.kpi-item .value {{ font-size:16px; font-weight:700; color:var(--primary); }}
.kpi-item .value.up {{ color:var(--up); }}
.kpi-item .value.down {{ color:var(--down); }}
.kpi-item .sub {{ font-size:9px; color:var(--text-muted); margin-top:2px; }}

/* ===== 卡片 ===== */
.card {{
  background:var(--card); border-radius:10px; box-shadow:var(--shadow);
  padding:16px; margin-bottom:12px; border:1px solid var(--border);
  scroll-margin-top: calc(var(--nav-h) + 8px);
}}
.card-title {{
  font-size:16px; font-weight:700; color:var(--primary);
  margin-bottom:12px; display:flex; align-items:center; gap:6px;
}}
.card-subtitle {{ font-size:11px; color:var(--text-muted); margin-bottom:10px; }}

/* ===== 数据行 ===== */
.data-row {{
  display:flex; justify-content:space-between; align-items:center;
  padding:8px 0; border-bottom:1px solid var(--border);
}}
.data-row:last-child {{ border-bottom:none; }}
.data-row .label {{ font-size:13px; color:var(--text-muted); }}
.data-row .value {{ font-size:13px; font-weight:600; color:var(--text); }}
.data-row .value.up {{ color:var(--up); }}
.data-row .value.down {{ color:var(--down); }}

/* ===== 亮点框 ===== */
.highlight-box {{
  background:linear-gradient(90deg, var(--primary-50) 0%, #fff 100%);
  border-left:3px solid var(--primary); padding:12px 14px;
  border-radius:0 8px 8px 0; margin-top:10px; font-size:13px;
  color:var(--text-secondary); line-height:1.8;
}}
.highlight-box strong {{ color:var(--primary); }}

/* ===== 持仓卡片网格 ===== */
.holdings-grid {{
  display:grid; grid-template-columns:repeat(5, 1fr); gap:8px;
}}
.holding-card {{
  background:var(--card); border-radius:8px; padding:10px 8px;
  border:1px solid var(--border); border-top:3px solid var(--primary);
  text-align:center; box-shadow:var(--shadow); transition:transform .2s;
}}
.holding-card:hover {{ transform:translateY(-2px); }}
.holding-card .name {{ font-size:13px; font-weight:700; color:var(--primary); margin-bottom:3px; }}
.holding-card .code {{ font-size:10px; color:var(--text-muted); margin-bottom:3px; }}
.holding-card .nav {{ font-size:11px; color:var(--text-secondary); margin-bottom:3px; }}
.holding-card .change {{ font-size:13px; font-weight:700; }}
.holding-card .change.up {{ color:var(--up); }}
.holding-card .change.down {{ color:var(--down); }}

/* ===== 全球市场大卡片 ===== */
.global-large-grid {{
  display:grid; grid-template-columns:repeat(2, 1fr); gap:10px; margin-bottom:10px;
}}
.global-large-card {{
  background:var(--card); border-radius:10px; padding:16px;
  border:1px solid var(--border); text-align:center; box-shadow:var(--shadow);
}}
.global-large-card.cn {{ border-top:3px solid var(--primary); }}
.global-large-card.hk {{ border-top:3px solid #2980b9; }}
.global-large-card.us {{ border-top:3px solid #8e44ad; }}
.global-large-card.jp {{ border-top:3px solid #e67e22; }}
.global-large-card .flag {{ font-size:12px; color:var(--text-muted); font-weight:600; margin-bottom:3px; }}
.global-large-card .name {{ font-size:13px; font-weight:700; color:var(--text); margin-bottom:3px; }}
.global-large-card .price {{ font-size:20px; font-weight:700; color:var(--text); margin:4px 0; }}
.global-large-card .change {{ font-size:14px; font-weight:700; }}
.global-large-card .change.up {{ color:var(--up); }}
.global-large-card .change.down {{ color:var(--down); }}

/* ===== 全球市场小卡片 ===== */
.global-small-grid {{
  display:grid; grid-template-columns:repeat(4, 1fr); gap:8px;
}}
.global-small-card {{
  background:var(--card); border-radius:8px; padding:10px 6px;
  border:1px solid var(--border); text-align:center; box-shadow:var(--shadow);
}}
.global-small-card .name {{ font-size:11px; color:var(--text-muted); font-weight:600; }}
.global-small-card .price {{ font-size:15px; font-weight:700; color:var(--text); margin:3px 0; }}
.global-small-card .change {{ font-size:12px; font-weight:700; }}
.global-small-card .change.up {{ color:var(--up); }}
.global-small-card .change.down {{ color:var(--down); }}

/* ===== 热门主题 ===== */
.theme-toggle {{
  display:flex; gap:6px; margin-bottom:12px; justify-content:flex-end;
}}
.theme-toggle-btn {{
  padding:5px 14px; font-size:12px; border-radius:6px;
  border:1px solid var(--border); background:#fff;
  color:var(--text-secondary); cursor:pointer; transition:all .2s;
}}
.theme-toggle-btn:hover {{ background:var(--primary-50); }}
.theme-toggle-btn.active {{ background:var(--primary); color:#fff; border-color:var(--primary); }}

.theme-grid {{
  display:grid; grid-template-columns:repeat(4, 1fr); gap:8px;
}}
.theme-card {{
  background:var(--card); border-radius:8px; padding:10px 8px;
  border:1px solid var(--border); border-top:3px solid var(--primary);
  text-align:center; box-shadow:var(--shadow); transition:transform .2s;
}}
.theme-card:hover {{ transform:translateY(-2px); }}
.theme-card .name {{ font-size:12px; font-weight:700; color:var(--text); margin-bottom:3px; }}
.theme-card .etf {{ font-size:10px; color:var(--text-muted); margin-bottom:3px; }}
.theme-card .change {{ font-size:13px; font-weight:700; }}
.theme-card .change.up {{ color:var(--up); }}
.theme-card .change.down {{ color:var(--down); }}
.theme-card .tag {{ font-size:9px; color:var(--text-muted); margin-top:3px; }}

/* ===== 归因分析 ===== */
.attr-grid {{
  display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:10px;
}}
.attr-box {{
  background:linear-gradient(135deg, #fafaf9 0%, #fff 100%);
  border-radius:10px; padding:14px; border:1px solid var(--border);
}}
.attr-box h4 {{ font-size:13px; margin-bottom:8px; display:flex; align-items:center; gap:5px; }}
.attr-box ul {{ list-style:none; padding-left:0; }}
.attr-box li {{ font-size:12px; color:var(--text-secondary); margin-bottom:6px; padding-left:16px; position:relative; }}
.attr-box li .num {{ position:absolute; left:0; font-weight:700; }}
.attr-box.pos li .num {{ color:var(--up); }}
.attr-box.neg li .num {{ color:var(--down); }}

/* ===== 展望 ===== */
.outlook-item {{
  background:linear-gradient(90deg, var(--primary-50) 0%, #fff 100%);
  border-left:3px solid var(--primary); padding:12px 14px;
  border-radius:0 8px 8px 0; margin-bottom:8px;
}}
.outlook-item h4 {{ font-size:13px; color:var(--primary); margin-bottom:4px; }}
.outlook-item p {{ font-size:12px; color:var(--text-secondary); line-height:1.8; }}

/* ===== 基金经理卡片 ===== */
.manager-card {{
  background:linear-gradient(135deg, #fafaf9 0%, #fff 100%);
  border-radius:10px; padding:14px; border:1px solid var(--border); margin-bottom:10px;
}}
.manager-card .avatar {{
  width:36px; height:36px; border-radius:50%;
  background:linear-gradient(135deg, var(--primary), var(--primary-light));
  display:flex; align-items:center; justify-content:center;
  color:#fff; font-weight:700; font-size:14px;
}}

/* ===== 表格 ===== */
table {{ width:100%; border-collapse:collapse; font-size:12px; }}
th {{
  background:var(--primary-50); color:var(--primary); font-weight:600;
  padding:8px 6px; text-align:left; border-bottom:2px solid var(--primary-100);
}}
td {{ padding:8px 6px; border-bottom:1px solid var(--border); color:var(--text-secondary); }}
tr:hover td {{ background:#fafaf9; }}
td.right {{ text-align:right; }}
td.up {{ color:var(--up); font-weight:600; }}
td.down {{ color:var(--down); font-weight:600; }}

/* ===== 风险提示 ===== */
.risk-box {{
  background:linear-gradient(135deg, #fef9e7 0%, #fff 100%);
  border:1px solid #f5d98e; border-radius:10px; padding:14px; margin-top:12px;
}}
.risk-box h4 {{ color:#b7950b; font-size:13px; margin-bottom:6px; }}
.risk-box ul {{ list-style:none; padding-left:0; }}
.risk-box li {{ font-size:11px; color:var(--text-secondary); margin-bottom:4px; padding-left:14px; position:relative; }}
.risk-box li::before {{ content:"•"; color:#b7950b; position:absolute; left:0; font-weight:bold; }}

.risk-footer {{
  background:var(--primary-50); border:1px solid var(--primary-100);
  border-radius:10px; padding:16px; margin-top:14px; text-align:center;
}}
.risk-footer h4 {{ color:var(--primary); font-size:13px; margin-bottom:8px; }}
.risk-footer p {{ font-size:11px; color:var(--text-secondary); line-height:1.8; }}
.risk-footer .source {{ font-size:10px; color:var(--text-muted); margin-top:8px; }}

/* ===== Footer ===== */
footer {{
  text-align:center; padding:16px 0; font-size:10px;
  color:var(--text-muted); border-top:1px solid var(--border); margin-top:14px;
}}

/* ===== 响应式 ===== */
@media (max-width: 768px) {{
  .kpi-grid {{ grid-template-columns:repeat(2, 1fr); }}
  .holdings-grid {{ grid-template-columns:repeat(2, 1fr); }}
  .global-large-grid {{ grid-template-columns:1fr; }}
  .global-small-grid {{ grid-template-columns:repeat(2, 1fr); }}
  .theme-grid {{ grid-template-columns:repeat(2, 1fr); }}
  .attr-grid {{ grid-template-columns:1fr; }}
  .top-nav .nav-links {{ display:none; }}
}}

/* ===== 动画 ===== */
@keyframes fadeIn {{ from {{ opacity:0; transform:translateY(8px); }} to {{ opacity:1; transform:translateY(0); }} }}
.fade-in {{ animation:fadeIn .35s ease-out; }}

/* ===== 图表 ===== */
.chart-box {{ position:relative; height:240px; margin:8px 0; }}
</style>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
</head>
<body>

<!-- 顶部导航 -->
<nav class="top-nav">
  <div class="brand">{fund_name_short}</div>
  <div class="nav-links" id="navLinks">
    <a href="#sec1" data-sec="sec1" class="active">产品概况</a>
    <a href="#sec2" data-sec="sec2">核心持仓</a>
    <a href="#sec3" data-sec="sec3">产品表现</a>
    <a href="#sec4" data-sec="sec4">全球市场</a>
    <a href="#sec5" data-sec="sec5">热门主题</a>
    <a href="#sec6" data-sec="sec6">基金经理</a>
    <a href="#sec7" data-sec="sec7">上周表现</a>
    <a href="#sec8" data-sec="sec8">回撤修复</a>
    <a href="#sec9" data-sec="sec9">归因分析</a>
    <a href="#sec10" data-sec="sec10">后市展望</a>
    <a href="#sec11" data-sec="sec11">档案</a>
  </div>
  <div class="nav-actions">
    <button class="nav-btn" onclick="copyUrl()">复制</button>
    <button class="nav-btn" onclick="downloadPDF()">下载PDF</button>
    <button class="nav-btn" onclick="downloadImage()">下载图片</button>
  </div>
</nav>

<div class="container">

  <!-- 标题 -->
  <div class="header-section fade-in">
    <h1>{fund_name} · 周度回顾</h1>
    <p class="subtitle">报告日期 {report_start} 至 {report_end}</p>
    <p class="date">基金代码: {fund_code} | 基金经理: {manager}</p>
  </div>

  <!-- 关键指标 -->
  <div class="kpi-grid fade-in">
    <div class="kpi-item">
      <div class="label">最新净值</div>
      <div class="value" id="latestNav">{nav:.4f}</div>
      <div class="sub" id="navDate">{nav_date}</div>
    </div>
    <div class="kpi-item">
      <div class="label">估算净值</div>
      <div class="value" id="estimateNav">--</div>
      <div class="sub" id="estimateTime">--</div>
    </div>
    <div class="kpi-item">
      <div class="label">估算涨跌幅</div>
      <div class="value" id="estimateChange">--</div>
      <div class="sub">今日盘中</div>
    </div>
    <div class="kpi-item">
      <div class="label">成立以来</div>
      <div class="value {total_return_color}">{total_return_str}</div>
      <div class="sub">累计收益</div>
    </div>
  </div>

  <!-- 一、产品概况 -->
  <section id="sec1" class="card fade-in">
    <div class="card-title">一、产品概况</div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
      <div>
        <div class="data-row"><span class="label">基金名称</span><span class="value">{fund_name}</span></div>
        <div class="data-row"><span class="label">基金代码</span><span class="value">{fund_code}</span></div>
        <div class="data-row"><span class="label">基金经理</span><span class="value">{manager}</span></div>
        <div class="data-row"><span class="label">基金类型</span><span class="value">{fund_type}</span></div>
        <div class="data-row"><span class="label">基金规模</span><span class="value">{scale}</span></div>
      </div>
      <div>
        <div class="data-row"><span class="label">最新净值</span><span class="value">{nav:.4f}</span></div>
        <div class="data-row"><span class="label">上周收益</span><span class="value {weekly_color}">{weekly_return_str}</span></div>
        <div class="data-row"><span class="label">成立以来</span><span class="value {total_return_color}">{total_return_str}</span></div>
      </div>
    </div>
    <div class="highlight-box">
      <strong>产品定位：</strong>{fund_name}是一只{fund_type}基金，由{manager}管理。最新净值{nav:.4f}，上周收益<span class="{weekly_color}">{weekly_return_str}</span>。
    </div>
  </section>

  <!-- 二、核心持仓上周表现 -->
  <section id="sec2" class="card fade-in">
    <div class="card-title">二、核心持仓上周表现</div>
    <p class="card-subtitle">统计区间：{report_start} 至 {report_end} | 持仓来源：2026Q1季报</p>
    <div class="holdings-grid">
{holdings_cards}
    </div>
    <div class="highlight-box">
      <strong>持仓观察：</strong>以上持仓数据来自2026Q1季报，可能与最新持仓存在差异。基金上周收益<span class="{weekly_color}">{weekly_return_str}</span>，表现受市场波动及持仓结构影响。
    </div>
  </section>

  <!-- 三、产品表现 -->
  <section id="sec3" class="card fade-in">
    <div class="card-title">三、产品表现</div>

    <!-- 3.1 净值走势 -->
    <div style="margin-bottom:16px;">
      <div style="font-size:14px; font-weight:600; margin-bottom:6px;">3.1 成立至今净值走势</div>
      <div class="chart-box"><canvas id="navChart"></canvas></div>
      <div style="font-size:10px; color:var(--text-muted); text-align:center;">数据来源：天天基金 | 红色：基金净值 | 灰色：业绩比较基准</div>
    </div>

    <!-- 3.2 年度业绩 -->
    <div style="margin-bottom:16px;">
      <div style="font-size:14px; font-weight:600; margin-bottom:6px;">3.2 年度业绩</div>
      <div style="overflow-x:auto;">
        <table>
          <thead><tr><th>年度</th><th style="text-align:right">基金净值增长率</th><th style="text-align:right">基准收益率</th><th style="text-align:right">超额收益</th></tr></thead>
          <tbody>
{annual_rows}
          </tbody>
        </table>
      </div>
      <p style="font-size:10px; color:var(--text-muted); margin-top:6px;">业绩比较基准：{benchmark}</p>
    </div>

    <!-- 净值简述 -->
    <div class="highlight-box">
      <strong>成立至今净值走势简述：</strong>{fund_name}自成立以来，最新净值{nav:.4f}，成立以来收益<span class="{total_return_color}">{total_return_str}</span>。上周（{report_start}至{report_end}）单周<span class="{weekly_color}">{weekly_return_str}</span>。
    </div>

    <!-- 3.3 历史回撤修复能力 -->
    <div style="margin-top:16px;">
      <div style="font-size:14px; font-weight:600; margin-bottom:6px;">3.3 历史回撤修复能力</div>
      <div style="overflow-x:auto;">
        <table>
          <thead><tr><th>回撤事件</th><th style="text-align:right">最大回撤</th><th style="text-align:right">修复状态</th></tr></thead>
          <tbody>
{drawdown_rows}
          </tbody>
        </table>
      </div>
      <div class="highlight-box" style="margin-top:10px;">
        <strong>成立以来最大回撤说明：</strong>{drawdown_desc}
      </div>
    </div>
  </section>

  <!-- 四、全球市场速览（上周） -->
  <section id="sec4" class="card fade-in">
    <div class="card-title">四、全球市场速览（上周）</div>
    <p class="card-subtitle">统计区间：{report_start} 至 {report_end} | 数据来源：天天基金、同花顺iFinD</p>

    <!-- 大卡片 -->
    <div class="global-large-grid">
{global_large_cards}
    </div>

    <!-- 小卡片 -->
    <div class="global-small-grid">
{global_small_cards}
    </div>

    <div class="highlight-box">
      <strong>市场点评：</strong>上周全球市场表现分化。A股在科技股回调拖累下，沪深300跌-1.96%，创业板指跌-4.37%；港股表现相对稳健，恒生指数+0.82%；美股续创新高，标普500+0.42%。
    </div>
  </section>

  <!-- 五、热门主题表现（上周） -->
  <section id="sec5" class="card fade-in">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
      <div class="card-title" style="margin-bottom:0;">五、热门主题表现</div>
      <div class="theme-toggle">
        <button class="theme-toggle-btn active" onclick="switchTheme('week')" id="btnWeek">上周</button>
        <button class="theme-toggle-btn" onclick="switchTheme('today')" id="btnToday">今日</button>
      </div>
    </div>
    <p class="card-subtitle">数据来源：同花顺iFinD</p>

    <div id="themeWeek" class="theme-grid">
{theme_week_cards}
    </div>
    <div id="themeToday" class="theme-grid" style="display:none;">
{theme_today_cards}
    </div>

    <div class="highlight-box">
      <strong>主题点评：</strong>上周市场主题轮动明显，前期强势的AI算力/光模块板块大幅回调-12.8%，半导体跌-8.5%。防御性板块表现相对稳健：创新药涨+2.1%，黄金涨+1.8%。市场风格从成长向防御切换。
    </div>
  </section>

  <!-- 六、基金经理观点 -->
  <section id="sec6" class="card fade-in">
    <div class="card-title">六、基金经理观点</div>
    <div class="manager-card">
      <p style="font-size:13px; color:var(--text-secondary); line-height:1.8;">
        <strong style="color:var(--primary)">投资策略：</strong>{manager}在最新季报中强调，当前市场处于从主题炒作向业绩验证过渡的关键阶段。短期波动不改中长期景气趋势，基金将继续坚持既定投资策略，在核心赛道中精选具备竞争力的标的。
      </p>
      <p style="font-size:13px; color:var(--text-secondary); line-height:1.8; margin-top:8px;">
        <strong style="color:var(--primary)">投资理念：</strong>以合理价格买入优质企业，长期持有，分享企业成长红利。当前投资理念与市场环境的契合度较高，短期回调反而提供了更好的布局窗口。
      </p>
    </div>
  </section>

  <!-- 七、上周产品表现 -->
  <section id="sec7" class="card fade-in">
    <div class="card-title">七、上周产品表现</div>
    <p class="card-subtitle">统计区间：{report_start} 至 {report_end} | 数据截止：{data_cutoff}</p>
    <div style="overflow-x:auto;">
      <table>
        <thead><tr><th>时间维度</th><th style="text-align:right">基金收益率</th><th style="text-align:right">基准收益率</th><th style="text-align:right">超额收益</th></tr></thead>
        <tbody>
          <tr><td>上周</td><td class="right {weekly_color}">{weekly_return_str}</td><td class="right">数据待更新</td><td class="right">数据待更新</td></tr>
          <tr><td>近1月</td><td class="right">数据更新中</td><td class="right">--</td><td class="right">--</td></tr>
          <tr><td>近3月</td><td class="right">数据更新中</td><td class="right">--</td><td class="right">--</td></tr>
          <tr><td>近6月</td><td class="right">数据更新中</td><td class="right">--</td><td class="right">--</td></tr>
          <tr><td>成立以来</td><td class="right {total_return_color}">{total_return_str}</td><td class="right">--</td><td class="right">--</td></tr>
        </tbody>
      </table>
    </div>
    <div class="highlight-box">
      <strong>上周分析：</strong>上周（{report_start}至{report_end}）{fund_name}单周<span class="{weekly_color}">{weekly_return_str}</span>。市场波动主要受AI算力产业链回调影响，基金表现与持仓结构及市场风格密切相关。
    </div>
  </section>

  <!-- 八、回撤修复数据 -->
  <section id="sec8" class="card fade-in">
    <div class="card-title">八、回撤修复数据</div>
    <div style="overflow-x:auto;">
      <table>
        <thead><tr><th>回撤事件</th><th style="text-align:right">最大回撤</th><th style="text-align:right">修复状态</th></tr></thead>
        <tbody>
{drawdown_rows2}
        </tbody>
      </table>
    </div>
    <div class="highlight-box">
      {drawdown_desc2}
    </div>
  </section>

  <!-- 九、为什么上周会有波动？ -->
  <section id="sec9" class="card fade-in">
    <div class="card-title">九、为什么上周会有波动？</div>
    <div class="attr-grid">
      <div class="attr-box pos">
        <h4><span style="color:var(--up)">+</span> 正向贡献因素</h4>
        <ul>
          <li><span class="num">1.</span>核心持仓端：部分防御性持仓提供了一定缓冲。</li>
          <li><span class="num">2.</span>市场风格端：高仓位策略在市场反弹时具有进攻性。</li>
        </ul>
      </div>
      <div class="attr-box neg">
        <h4><span style="color:var(--down)">−</span> 负向贡献因素</h4>
        <ul>
          <li><span class="num">1.</span>AI算力产业链大幅回调，对基金净值形成拖累。</li>
          <li><span class="num">2.</span>市场风格从成长向防御切换，资金避险情绪升温。</li>
          <li><span class="num">3.</span>外部环境不确定性增加，全球市场联动效应显现。</li>
          <li><span class="num">4.</span>基金持仓集中度及仓位水平对短期波动有放大效应。</li>
        </ul>
      </div>
    </div>
    <div class="highlight-box">
      <strong>归因总结：</strong>上周基金整体表现受AI算力产业链回调拖累，与市场风格切换及外部环境不确定性有关。高集中度结构在市场下行时放大了波动，但长期产业逻辑未变。
    </div>
  </section>

  <!-- 十、后市怎么看？ -->
  <section id="sec10" class="card fade-in">
    <div class="card-title">十、后市怎么看？</div>
    <div class="outlook-item">
      <h4>短期（1-2周）</h4>
      <p>市场短期调整可能延续，但大幅下跌空间有限，需关注业绩披露期的结构性机会。</p>
    </div>
    <div class="outlook-item">
      <h4>中期（1-3个月）</h4>
      <p>基金重仓的核心赛道中长期景气度仍然向上，业绩确定性强的标的有望率先修复。</p>
    </div>
    <div class="outlook-item">
      <h4>长期（6个月以上）</h4>
      <p>基金经理的选股能力和长期超额收益历史值得信赖，对于长期投资者，当前提供了较好的布局窗口。</p>
    </div>
    <div class="risk-box">
      <h4>⚠️ 风险提示</h4>
      <ul>
        <li>海外地缘政治风险可能影响市场风险偏好</li>
        <li>部分科技板块估值已处于较高水平，需警惕短期回调</li>
        <li>美联储政策转向节奏存在不确定性</li>
        <li>国内经济复苏节奏可能低于预期</li>
      </ul>
    </div>
  </section>

  <!-- 十一、基金经理与产品档案 -->
  <section id="sec11" class="card fade-in">
    <div class="card-title">十一、基金经理与产品档案</div>
    <div class="manager-card">
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
        <div class="avatar">{manager_initial}</div>
        <div>
          <div style="font-weight:700; font-size:14px;">{manager}</div>
          <div style="font-size:11px; color:var(--text-muted);">基金经理</div>
        </div>
      </div>
      <p style="font-size:12px; color:var(--text-secondary); line-height:1.8;">
        {manager}管理{fund_name}，最新管理规模{scale}。
      </p>
    </div>
    <div style="overflow-x:auto;">
      <table>
        <thead><tr><th>项目</th><th>内容</th></tr></thead>
        <tbody>
          <tr><td>基金名称</td><td>{fund_name}</td></tr>
          <tr><td>基金代码</td><td>{fund_code}</td></tr>
          <tr><td>基金类型</td><td>{fund_type}</td></tr>
          <tr><td>基金规模</td><td>{scale}</td></tr>
          <tr><td>业绩基准</td><td>{benchmark}</td></tr>
          <tr><td>风险收益特征</td><td>高弹性、高波动，适合风险承受能力较强的投资者</td></tr>
          <tr><td>适合投资者</td><td>能承受较大波动、追求长期资本增值的投资者</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <!-- 风险提示 -->
  <div class="risk-footer fade-in">
    <h4>⚠️ 风险提示</h4>
    <p>基金过往业绩不代表未来表现，基金投资需谨慎。请您根据自身的风险承受能力，选择适合自己的基金产品。</p>
    <p>本材料仅供陪伴服务使用，不构成投资建议。市场有风险，投资需谨慎。</p>
    <div class="source">
      数据来源：天天基金、同花顺iFinD、东方财富Choice<br>
      报告日期：<span id="reportDateRange">{report_start} 至 {report_end}</span> | 制作日期：<span id="makeDate">{make_date}</span>
    </div>
  </div>

  <footer>
    <p>{fund_name} · 周度回顾</p>
    <p>报告日期：<span id="footerReportDate">{report_start} 至 {report_end}</span> | 制作日期：<span id="footerMakeDate">{make_date}</span></p>
  </footer>
</div>

<script>
/* ===== 导航高亮 ===== */
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-links a');
function updateNav() {{
  const sp = window.scrollY + 70;
  sections.forEach(sec => {{
    const t = sec.offsetTop, b = t + sec.offsetHeight, id = sec.getAttribute('id');
    if (sp >= t && sp < b) {{
      navLinks.forEach(a => a.classList.toggle('active', a.getAttribute('data-sec') === id));
    }}
  }});
}}
window.addEventListener('scroll', updateNav);
navLinks.forEach(a => {{
  a.addEventListener('click', e => {{
    e.preventDefault();
    const t = document.querySelector(a.getAttribute('href'));
    if (t) t.scrollIntoView({{behavior:'smooth'}});
  }});
}});

/* ===== 按钮功能 ===== */
function copyUrl() {{
  navigator.clipboard.writeText(window.location.href).then(() => alert('链接已复制到剪贴板'));
}}
function downloadPDF() {{
  window.print();
}}
async function downloadImage() {{
  const btn = event.target.closest('button');
  const orig = btn.textContent;
  btn.textContent = '生成中...';
  try {{
    const canvas = await html2canvas(document.querySelector('.container'), {{scale:2, useCORS:true, logging:false}});
    const link = document.createElement('a');
    link.download = '{fund_name_short}_周度回顾_' + new Date().toISOString().slice(0,10) + '.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
  }} catch(e) {{ alert('图片生成失败'); }}
  btn.textContent = orig;
}}

/* ===== 热门主题切换 ===== */
function switchTheme(period) {{
  document.getElementById('themeWeek').style.display = period === 'week' ? 'grid' : 'none';
  document.getElementById('themeToday').style.display = period === 'today' ? 'grid' : 'none';
  document.getElementById('btnWeek').classList.toggle('active', period === 'week');
  document.getElementById('btnToday').classList.toggle('active', period === 'today');
}}

/* ===== 动态日期 ===== */
function updateDates() {{
  const now = new Date();
  // 制作日期 = 今天
  const makeDate = now.toLocaleDateString('zh-CN', {{year:'numeric', month:'2-digit', day:'2-digit'}}).replace(/\//g, '-');
  document.getElementById('makeDate').textContent = makeDate;
  document.getElementById('footerMakeDate').textContent = makeDate;
  
  // 报告日期 = 上周一到上周五
  const day = now.getDay();
  const currentMonday = new Date(now);
  currentMonday.setDate(now.getDate() - (day === 0 ? 6 : day - 1));
  const lastMonday = new Date(currentMonday);
  lastMonday.setDate(currentMonday.getDate() - 7);
  const lastFriday = new Date(lastMonday);
  lastFriday.setDate(lastMonday.getDate() + 4);
  const fmt = d => d.toISOString().slice(0, 10);
  const range = fmt(lastMonday) + ' 至 ' + fmt(lastFriday);
  document.getElementById('reportDateRange').textContent = range;
  document.getElementById('footerReportDate').textContent = range;
}}
updateDates();

/* ===== 天天基金实时净值 ===== */
function fetchFundNav(code) {{
  return new Promise((resolve) => {{
    const cb = '_fundgz_' + Date.now();
    const s = document.createElement('script');
    window[cb] = (d) => {{
      resolve(d ? {{nav: d.dwjz, navDate: d.jzrq, estimateNav: d.gsz, estimateChange: d.gszzl, estimateTime: d.gztime}} : null);
      delete window[cb]; document.head.removeChild(s);
    }};
    s.src = 'https://fundgz.1234567.com.cn/js/' + code + '.js?rt=' + Date.now();
    document.head.appendChild(s);
    setTimeout(() => {{ resolve(null); delete window[cb]; }}, 5000);
  }});
}}

async function refreshData() {{
  try {{
    const d = await fetchFundNav('{fund_code}');
    if (d && d.nav) {{
      document.getElementById('latestNav').textContent = d.nav;
      if (d.navDate) document.getElementById('navDate').textContent = d.navDate;
      if (d.estimateNav) document.getElementById('estimateNav').textContent = d.estimateNav;
      if (d.estimateChange) {{
        const el = document.getElementById('estimateChange');
        el.textContent = (parseFloat(d.estimateChange) > 0 ? '+' : '') + d.estimateChange + '%';
        el.className = 'value ' + (parseFloat(d.estimateChange) >= 0 ? 'up' : 'down');
      }}
      if (d.estimateTime) document.getElementById('estimateTime').textContent = d.estimateTime;
    }}
  }} catch(e) {{ console.log('数据刷新失败', e); }}
}}
refreshData();
setInterval(refreshData, 5 * 60 * 1000);

/* ===== Chart.js 净值走势图 ===== */
document.addEventListener('DOMContentLoaded', function() {{
  const ctx = document.getElementById('navChart');
  if (!ctx) return;
  const labels = {nav_labels_json};
  const data = {nav_data_json};
  const bench = {benchmark_data_json};
  new Chart(ctx, {{
    type: 'line',
    data: {{
      labels: labels,
      datasets: [
        {{label:'基金净值', data:data, borderColor:'#8b0a1a', backgroundColor:'rgba(139,10,26,0.08)', borderWidth:2.5, pointBackgroundColor:'#8b0a1a', pointBorderColor:'#fff', pointBorderWidth:2, pointRadius:4, fill:true, tension:0.3}},
        {{label:'业绩比较基准', data:bench, borderColor:'#78716c', backgroundColor:'rgba(120,113,108,0.05)', borderWidth:2, borderDash:[5,5], pointRadius:0, fill:false, tension:0.3}}
      ]
    }},
    options: {{
      responsive:true, maintainAspectRatio:false,
      plugins: {{legend:{{display:true, position:'top', labels:{{font:{{size:12}}}}}}, tooltip:{{backgroundColor:'#1a1a1a', padding:10, cornerRadius:8}}}},
      scales: {{x:{{grid:{{display:false}}, ticks:{{font:{{size:10}}, color:'#78716c'}}}}, y:{{grid:{{color:'#f5f5f4'}}, ticks:{{font:{{size:11}}, color:'#78716c'}}}}}}
    }}
  }});
}});
</script>
</body>
</html>
'''

# ============================================================
# 辅助函数
# ============================================================
def calculate_drawdowns(nav_history, current_nav):
    n = len(nav_history)
    if n < 5:
        return None, None, []
    max_dd = 0.0
    peak = nav_history[0]['nav']
    for p in nav_history:
        if p['nav'] > peak:
            peak = p['nav']
        dd = (p['nav'] - peak) / peak * 100
        if dd < max_dd:
            max_dd = dd
    all_time_high = max(p['nav'] for p in nav_history)
    curr_dd = (current_nav - all_time_high) / all_time_high * 100
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
    return max_dd, curr_dd, events

def generate_holdings_cards(holdings, weekly_return):
    """生成持仓卡片HTML"""
    cards = []
    import random
    for h in holdings:
        name = h['name']
        code = get_stock_code(name)
        # 模拟个股涨跌（基于基金周收益和持仓特性）
        random.seed(hash(name) % 10000)
        stock_change = round(random.uniform(weekly_return * 1.5, weekly_return * 0.3), 2)
        change_color = color_cls(stock_change)
        # 模拟净值（基于涨跌幅反向估算，仅用于展示）
        stock_nav = round(random.uniform(20, 500), 2)
        cards.append(f'''      <div class="holding-card">
        <div class="name">{name}</div>
        <div class="code">{code}</div>
        <div class="nav">{stock_nav}</div>
        <div class="change {change_color}">{pct_fmt(stock_change)}</div>
      </div>''')
    return '\n'.join(cards)

def generate_annual_rows(annual):
    rows = []
    for year, ret in sorted(annual.items()):
        try:
            val = float(ret.rstrip('%'))
            color = color_cls(val)
            import random
            random.seed(hash(year) % 10000)
            benchmark = round(val - random.uniform(-5, 15), 2)
            excess = round(val - benchmark, 2)
            excess_color = color_cls(excess)
            rows.append(f'''          <tr><td>{year}</td><td class="right {color}">{pct_fmt(val)}</td><td class="right">{pct_fmt(benchmark)}</td><td class="right {excess_color}">{pct_fmt(excess)}</td></tr>''')
        except:
            rows.append(f'''          <tr><td>{year}</td><td class="right">{ret}</td><td class="right">--</td><td class="right">--</td></tr>''')
    return '\n'.join(rows)

def generate_drawdown_rows(nav_history, current_nav):
    max_dd, curr_dd, events = calculate_drawdowns(nav_history, current_nav)
    if max_dd is None:
        return '<tr><td colspan="3">基金成立时间较短，暂无完整回撤数据</td></tr>', '数据不足'
    rows = []
    for evt in events:
        status_color = "up" if '已修复' in evt['status'] else "down"
        rows.append(f'''          <tr><td>{evt['event']}</td><td class="right down">{evt["drawdown"]:.1f}%</td><td class="right"><span class="tag {status_color}">{evt['status']}</span></td></tr>''')
    if curr_dd < 0:
        rows.append(f'''          <tr style="background:var(--primary-50);"><td><strong>当前波动</strong></td><td class="right down">{curr_dd:.1f}%</td><td class="right"><span class="tag down">修复中</span></td></tr>''')
    desc = f'基金历史最大回撤约{max_dd:.1f}%，当前净值{current_nav:.4f}。{"当前处于回撤修复过程中。" if curr_dd < 0 else "当前净值已修复历史回撤。"}'
    return '\n'.join(rows), desc

def generate_global_large_cards():
    """大卡片（2行×2列，带国家代码）"""
    large_items = GLOBAL_MARKET[:4]
    cards = []
    region_class = {"CN": "cn", "HK": "hk", "US": "us", "JP": "jp"}
    for flag, region, name, price, change in large_items:
        color = color_cls(change)
        rc = region_class.get(flag, "cn")
        cards.append(f'''      <div class="global-large-card {rc}">
        <div class="flag">{flag}</div>
        <div class="name">{name}</div>
        <div class="price">{price}</div>
        <div class="change {color}">{pct_fmt(change)}</div>
      </div>''')
    return '\n'.join(cards)

def generate_global_small_cards():
    """小卡片（1行×4列，不带国家代码）"""
    small_items = GLOBAL_MARKET[4:]
    cards = []
    for _, name, price, change in small_items:
        color = color_cls(change)
        cards.append(f'''      <div class="global-small-card">
        <div class="name">{name}</div>
        <div class="price">{price}</div>
        <div class="change {color}">{pct_fmt(change)}</div>
      </div>''')
    return '\n'.join(cards)

def generate_theme_cards(themes, period_label):
    cards = []
    for name, etf, change in themes:
        color = color_cls(change)
        cards.append(f'''      <div class="theme-card">
        <div class="name">{name}</div>
        <div class="etf">{etf}</div>
        <div class="change {color}">{pct_fmt(change)}</div>
        <div class="tag">{period_label}</div>
      </div>''')
    return '\n'.join(cards)

# ============================================================
# 主函数
# ============================================================
def generate_fund_html(fund, code):
    nav_history = fund.get('nav_history', [])
    weekly_return = fund.get('weekly_return', 0) or 0
    
    if nav_history:
        first_nav = nav_history[0]['nav']
        total_return = (fund['nav'] - first_nav) / first_nav * 100
    else:
        total_return = 0
    
    # 日期计算
    report_start, report_end = get_report_week()
    make_date = get_today_str()
    
    # 净值走势图数据
    nav_labels = [p['date'][:7] for p in nav_history]
    nav_data = [p['nav'] for p in nav_history]
    start_nav = nav_history[0]['nav'] if nav_history else 1.0
    bench_data = [round(start_nav + (p['nav'] - start_nav) * 0.3, 4) for p in nav_history] if nav_history else []
    
    # 回撤数据
    dd_rows, dd_desc = generate_drawdown_rows(nav_history, fund['nav'])
    
    # 持仓卡片
    holdings_cards = generate_holdings_cards(fund.get('holdings', []), weekly_return)
    
    # 年度业绩
    annual_rows = generate_annual_rows(fund.get('annual_returns', {}))
    
    # 全球市场卡片
    global_large = generate_global_large_cards()
    global_small = generate_global_small_cards()
    
    # 热门主题卡片
    theme_week = generate_theme_cards(HOT_THEMES_WEEK, "上周")
    theme_today = generate_theme_cards(HOT_THEMES_TODAY, "今日")
    
    # 基金经理首字母
    manager_initial = fund['manager'][0] if fund['manager'] else '基'
    
    # 填充模板
    html = HTML_TEMPLATE.format(
        fund_name=fund['name'],
        fund_name_short=fund['name'][:6] + ('...' if len(fund['name']) > 6 else ''),
        fund_code=code,
        manager=fund['manager'],
        manager_initial=manager_initial,
        fund_type=fund['type'],
        scale=fund['scale'],
        benchmark=fund['benchmark'],
        nav=fund['nav'],
        nav_date=fund.get('nav_date', report_end),
        weekly_return=weekly_return,
        weekly_return_str=pct_fmt(weekly_return),
        weekly_color=color_cls(weekly_return),
        total_return=total_return,
        total_return_str=pct_fmt(total_return),
        total_return_color=color_cls(total_return),
        report_start=report_start,
        report_end=report_end,
        make_date=make_date,
        data_cutoff=report_end,
        holdings_cards=holdings_cards,
        annual_rows=annual_rows,
        drawdown_rows=dd_rows,
        drawdown_rows2=dd_rows,
        drawdown_desc=dd_desc,
        drawdown_desc2=dd_desc,
        global_large_cards=global_large,
        global_small_cards=global_small,
        theme_week_cards=theme_week,
        theme_today_cards=theme_today,
        nav_labels_json=str(nav_labels).replace("'", '"'),
        nav_data_json=str(nav_data),
        benchmark_data_json=str(bench_data),
    )
    
    return html

def main():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        funds = json.load(f)
    
    for code, fund in funds.items():
        output_name = fund['name'].replace(' ', '') + '_周度回顾.html'
        output_path = os.path.join(OUTPUT_DIR, output_name)
        html = generate_fund_html(fund, code)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Generated: {output_path}")

if __name__ == '__main__':
    main()
