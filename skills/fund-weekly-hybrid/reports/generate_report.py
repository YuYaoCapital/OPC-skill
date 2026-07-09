#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 fund-weekly-hybrid 融合报告 HTML
风格：portfolio-week-companion
内容：fund-weekly-review 9模块 + 第10模块横纵分析
"""
import os

OUTPUT_DIR = "D:/OPC-skill/skills/fund-weekly-hybrid/reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>睿远成长价值混合A · 融合周度报告</title>
<style>
:root {
  --primary: #1e3a5f;
  --primary-light: #2c5282;
  --bg: #f5f7fa;
  --card-bg: #ffffff;
  --text: #333333;
  --text-secondary: #666666;
  --up: #e74c3c;
  --down: #27ae60;
  --border: #e8e8e8;
  --shadow: 0 2px 12px rgba(0,0,0,0.08);
  --radius: 12px;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif;
  background: var(--bg); color: var(--text); line-height: 1.6; padding-bottom: 40px;
}
.top-nav {
  position: sticky; top: 0; z-index: 100;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  padding: 10px 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.top-nav-inner { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
.nav-title { color: #fff; font-size: 15px; font-weight: 600; }
.nav-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.nav-tag { color: #fff; font-size: 12px; padding: 3px 10px; border-radius: 20px; background: rgba(255,255,255,0.15); text-decoration: none; transition: all 0.2s; cursor: pointer; border: none; }
.nav-tag:hover { background: rgba(255,255,255,0.3); }
.toolbar { position: fixed; top: 55px; right: 16px; z-index: 99; display: flex; flex-direction: column; gap: 6px; align-items: flex-end; }
.toolbar-btn { display: flex; align-items: center; gap: 4px; background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 7px 12px; font-size: 12px; color: var(--text); cursor: pointer; box-shadow: var(--shadow); }
.toolbar-btn:hover { background: var(--primary); color: #fff; }
.update-time { font-size: 11px; color: var(--text-secondary); background: var(--card-bg); padding: 4px 10px; border-radius: 6px; box-shadow: var(--shadow); }
.hero { background: linear-gradient(135deg, var(--primary) 0%, #1a365d 100%); color: #fff; padding: 36px 24px 28px; text-align: center; }
.hero h1 { font-size: 26px; font-weight: 700; margin-bottom: 12px; letter-spacing: 1px; }
.hero .meta-line { font-size: 14px; opacity: 0.9; display: flex; justify-content: center; gap: 16px; flex-wrap: wrap; }
main { max-width: 1200px; margin: 0 auto; padding: 24px 16px; }
section { margin-bottom: 32px; scroll-margin-top: 65px; }
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; flex-wrap: wrap; gap: 8px; }
.section-title { font-size: 18px; font-weight: 600; color: var(--primary); display: flex; align-items: center; gap: 8px; }
.section-source { font-size: 12px; color: #999; }
.card { background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); padding: 20px; }
.kpi-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.kpi-grid-6 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
@media(min-width:768px){ .kpi-grid-6 { grid-template-columns: repeat(6, 1fr); } }
.kpi-card { background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); padding: 20px; text-align: center; transition: transform 0.2s; }
.kpi-card:hover { transform: translateY(-2px); }
.kpi-label { font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; }
.kpi-value { font-size: 26px; font-weight: 700; font-family: "DIN Alternate", "Helvetica Neue", Arial, sans-serif; }
.kpi-value.up { color: var(--up); }
.kpi-value.down { color: var(--down); }
.kpi-sub { font-size: 12px; color: #999; margin-top: 4px; }
.holding-grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }
.holding-card { background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); padding: 16px 10px; text-align: center; transition: transform 0.2s; border: 1px solid transparent; }
.holding-card:hover { transform: translateY(-2px); border-color: var(--primary-light); }
.holding-name { font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.holding-code { font-size: 11px; color: #999; margin-bottom: 8px; }
.holding-nav { font-size: 18px; font-weight: 700; font-family: "DIN Alternate", Arial, sans-serif; margin-bottom: 4px; }
.holding-change { font-size: 13px; font-weight: 600; }
.holding-change.up { color: var(--up); }
.holding-change.down { color: var(--down); }
.market-grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.market-card { background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); padding: 18px; text-align: center; display: flex; align-items: center; justify-content: space-between; }
.market-left { text-align: left; }
.market-flag { font-size: 28px; margin-bottom: 4px; }
.market-name { font-size: 13px; color: var(--text-secondary); }
.market-right { text-align: right; }
.market-price { font-size: 20px; font-weight: 700; font-family: "DIN Alternate", Arial, sans-serif; }
.market-change { font-size: 14px; font-weight: 600; }
.market-change.up { color: var(--up); }
.market-change.down { color: var(--down); }
.theme-tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.theme-tab { padding: 6px 16px; border-radius: 20px; font-size: 13px; background: #e8f0fe; color: var(--primary); border: none; cursor: pointer; transition: all 0.2s; }
.theme-tab.active { background: var(--primary); color: #fff; }
.theme-tab:hover { background: var(--primary-light); color: #fff; }
.theme-scroll { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 8px; }
.theme-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.theme-card { background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); padding: 14px; text-align: center; min-width: 120px; flex-shrink: 0; }
.theme-name { font-size: 13px; font-weight: 600; }
.theme-etf { font-size: 11px; color: #999; margin: 4px 0; }
.theme-change { font-size: 15px; font-weight: 700; }
.theme-change.up { color: var(--up); }
.theme-change.down { color: var(--down); }
.theme-period { font-size: 11px; color: #999; margin-top: 2px; }
.copy-btn { display: inline-flex; align-items: center; gap: 4px; background: #e8f0fe; color: var(--primary); border: none; border-radius: 6px; padding: 6px 14px; font-size: 12px; cursor: pointer; transition: all 0.2s; }
.copy-btn:hover { background: var(--primary); color: #fff; }
.fm-section { margin-bottom: 16px; }
.fm-section h4 { font-size: 15px; color: var(--primary); margin-bottom: 8px; }
.fm-section p { font-size: 14px; color: var(--text-secondary); line-height: 1.8; }
.ai-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.ai-card { background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); padding: 20px; }
.ai-card h4 { font-size: 15px; color: var(--primary); margin-bottom: 10px; }
.ai-card p { font-size: 14px; color: var(--text-secondary); line-height: 1.8; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border); }
th { background: #f8f9fa; font-weight: 600; color: var(--primary); }
tr:hover { background: #fafbfc; }
.script-block { background: #f8f9fa; border-left: 3px solid var(--primary); padding: 14px 18px; margin: 10px 0; border-radius: 0 8px 8px 0; font-size: 14px; color: var(--text-secondary); line-height: 1.8; }
.faq-item { margin-bottom: 16px; }
.faq-q { font-size: 15px; font-weight: 600; color: var(--primary); margin-bottom: 6px; }
.faq-a { font-size: 14px; color: var(--text-secondary); line-height: 1.8; }
.quadrant-container { display: flex; justify-content: center; margin: 20px 0; }
.quadrant-canvas { max-width: 100%; }
.risk-box { background: #fff8f0; border: 1px solid #ffe4c4; border-radius: 8px; padding: 16px 20px; color: #8b6914; font-size: 13px; line-height: 1.9; }
.risk-box p { text-align: left; margin-bottom: 4px; }
footer { max-width: 1200px; margin: 0 auto; padding: 24px 16px; font-size: 12px; color: #999; text-align: center; line-height: 1.8; }
.live-tag { display: inline-flex; align-items: center; gap: 4px; font-size: 10px; font-weight: 600; color: #fff; background: #27ae60; padding: 2px 8px; border-radius: 4px; animation: pulse 2s infinite; }
.live-tag.offline { background: #999; animation: none; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }

/* 横纵分析折叠面板 */
.details-group { margin-bottom: 12px; }
.details-group summary {
  font-size: 15px; font-weight: 600; color: var(--primary);
  cursor: pointer; padding: 14px 16px; background: #f8f9fa;
  border-radius: 8px; border: 1px solid var(--border);
  list-style: none; display: flex; align-items: center; justify-content: space-between;
}
.details-group summary::-webkit-details-marker { display: none; }
.details-group summary::after { content: "▼"; font-size: 12px; color: #999; transition: transform 0.2s; }
.details-group[open] summary::after { transform: rotate(180deg); }
.details-group summary:hover { background: #eef2f7; }
.details-content { padding: 16px; border: 1px solid var(--border); border-top: none; border-radius: 0 0 8px 8px; background: var(--card-bg); }
.details-content p { font-size: 14px; color: var(--text-secondary); line-height: 1.8; margin-bottom: 10px; }
.details-content h5 { font-size: 14px; color: var(--primary); margin: 12px 0 6px; }
.details-content table { font-size: 13px; margin-top: 8px; }
.details-content th, .details-content td { padding: 10px 12px; }

/* 日收益卡片 */
.day-row { display: flex; gap: 8px; justify-content: center; margin: 16px 0; }
.day-card { flex: 1; background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); padding: 12px 8px; text-align: center; }
.day-date { font-size: 11px; color: #999; }
.day-return { font-size: 16px; font-weight: 700; margin-top: 4px; }
.day-return.up { color: var(--up); }
.day-return.down { color: var(--down); }

/* 档案表格 */
.archive-table { font-size: 13px; }
.archive-table th, .archive-table td { padding: 10px 14px; }

@media (max-width: 1024px) { .holding-grid-5 { grid-template-columns: repeat(3, 1fr); } .theme-grid-4 { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .kpi-grid-3 { grid-template-columns: repeat(2, 1fr); } .kpi-grid-6 { grid-template-columns: repeat(2, 1fr); } .holding-grid-5 { grid-template-columns: repeat(2, 1fr); } .market-grid-2 { grid-template-columns: 1fr; } .theme-grid-4 { grid-template-columns: repeat(2, 1fr); } .ai-grid { grid-template-columns: 1fr; } .hero h1 { font-size: 20px; } .hero .meta-line { font-size: 12px; } .toolbar { top: auto; bottom: 16px; right: 10px; } .day-row { flex-wrap: wrap; } .day-card { min-width: 60px; flex: 1 1 30%; } }
@media (max-width: 480px) { .kpi-grid-3 { grid-template-columns: 1fr; } .kpi-grid-6 { grid-template-columns: 1fr; } .holding-grid-5 { grid-template-columns: 1fr; } }
@media print { .top-nav, .toolbar { display: none; } body { background: #fff; } .card { box-shadow: none; border: 1px solid #ddd; } .details-group { display: block; } .details-group summary { background: #fff; } .details-content { display: block; border: 1px solid #ddd; } }
</style>
</head>
<body>

<nav class="top-nav">
  <div class="top-nav-inner">
    <div class="nav-title">睿远成长价值混合A · 融合周度报告</div>
    <div class="nav-tags">
      <a class="nav-tag" href="#overview">📋 产品概况</a>
      <a class="nav-tag" href="#holdings">🏦 核心持仓</a>
      <a class="nav-tag" href="#market">🌍 全球市场</a>
      <a class="nav-tag" href="#keywords">🔑 关键词</a>
      <a class="nav-tag" href="#themes">🔥 热门主题</a>
      <a class="nav-tag" href="#fm-view">📋 基金经理观点</a>
      <a class="nav-tag" href="#ai-insight">🤖 AI解读</a>
      <a class="nav-tag" href="#performance">📊 本周表现</a>
      <a class="nav-tag" href="#drawdown">⏱️ 回撤修复</a>
      <a class="nav-tag" href="#attribution">🔍 波动归因</a>
      <a class="nav-tag" href="#outlook">🔭 后市观点</a>
      <a class="nav-tag" href="#action">🎯 行动指南</a>
      <a class="nav-tag" href="#deep-dive">📁 深度档案</a>
    </div>
  </div>
</nav>

<div class="toolbar">
  <div class="update-time" id="update-time">更新中...</div>
  <button class="toolbar-btn" onclick="refreshAll()">🔄 刷新</button>
  <button class="toolbar-btn" onclick="window.print()">📄 PDF</button>
  <button class="toolbar-btn" onclick="copyReportSummary()">📋 复制摘要</button>
</div>

<header class="hero">
  <h1>睿远成长价值混合A 融合周度报告</h1>
  <div class="meta-line">
    <span>📅 2026-07-06 至 2026-07-09</span>
    <span>🔢 基金代码：007119</span>
    <span>⚠️ 风险等级：R4（中高风险）</span>
    <span>👤 基金经理：傅鹏博、朱璘</span>
  </div>
</header>

<main>

<!-- 1. 产品概况 -->
<section id="overview">
  <div class="section-header">
    <div class="section-title">📋 产品概况</div>
    <span class="live-tag" id="nav-live-tag">LIVE</span>
  </div>
  <div class="kpi-grid-6">
    <div class="kpi-card"><div class="kpi-label">基金代码</div><div class="kpi-value" style="font-size:20px;">007119</div><div class="kpi-sub">睿远成长价值混合A</div></div>
    <div class="kpi-card"><div class="kpi-label">基金经理</div><div class="kpi-value" style="font-size:18px;">傅鹏博、朱璘</div><div class="kpi-sub">双经理管理</div></div>
    <div class="kpi-card"><div class="kpi-label">最新净值 <span class="live-tag">LIVE</span></div><div class="kpi-value" id="latest-nav">2.4895</div><div class="kpi-sub" id="nav-date">净值日期：2026-07-08</div></div>
    <div class="kpi-card"><div class="kpi-label">日涨跌 <span class="live-tag">LIVE</span></div><div class="kpi-value up" id="daily-change">+4.77%</div><div class="kpi-sub" id="estimate-time">估算时间：2026-07-09 15:00</div></div>
    <div class="kpi-card"><div class="kpi-label">本周收益</div><div class="kpi-value up" id="week-return">+4.77%</div><div class="kpi-sub">2026-07-06 至 2026-07-09</div></div>
    <div class="kpi-card"><div class="kpi-label">成立以来</div><div class="kpi-value up">+148.95%</div><div class="kpi-sub">2019-03-26 成立</div></div>
  </div>
</section>

<!-- 2. 核心持仓 -->
<section id="holdings">
  <div class="section-header">
    <div class="section-title">🏦 核心持仓（2026Q1）</div>
    <div style="display:flex;align-items:center;gap:8px;">
      <span style="font-size:13px;color:#666;">股票仓位 <strong>93.11%</strong> | 规模 <strong>165.00亿</strong> | 近1年 <strong>+87.84%</strong></span>
    </div>
  </div>
  <div class="holding-grid-5">
    <div class="holding-card"><div class="holding-name">东山精密</div><div class="holding-code">10.00%</div><div class="holding-nav">第一重仓</div><div class="holding-change">PCB</div></div>
    <div class="holding-card"><div class="holding-name">迈为股份</div><div class="holding-code">9.20%</div><div class="holding-nav">光伏设备</div><div class="holding-change">HJT设备</div></div>
    <div class="holding-card"><div class="holding-name">新易盛</div><div class="holding-code">6.78%</div><div class="holding-nav">光模块</div><div class="holding-change">800G/1.6T</div></div>
    <div class="holding-card"><div class="holding-name">胜宏科技</div><div class="holding-code">6.09%</div><div class="holding-nav">PCB</div><div class="holding-change">AI服务器</div></div>
    <div class="holding-card"><div class="holding-name">中际旭创</div><div class="holding-code">5.90%</div><div class="holding-nav">光模块</div><div class="holding-change">CPO概念</div></div>
    <div class="holding-card"><div class="holding-name">宁德时代</div><div class="holding-code">4.02%</div><div class="holding-nav">动力电池</div><div class="holding-change">锂电龙头</div></div>
    <div class="holding-card"><div class="holding-name">立讯精密</div><div class="holding-code">—</div><div class="holding-nav">消费电子</div><div class="holding-change">苹果链</div></div>
    <div class="holding-card"><div class="holding-name">腾讯控股</div><div class="holding-code">—</div><div class="holding-nav">互联网</div><div class="holding-change">港股通</div></div>
    <div class="holding-card"><div class="holding-name">巨星科技</div><div class="holding-code">—</div><div class="holding-nav">工具制造</div><div class="holding-change">出口链</div></div>
    <div class="holding-card"><div class="holding-name">大族激光</div><div class="holding-code">—</div><div class="holding-nav">激光设备</div><div class="holding-change">智能制造</div></div>
  </div>
  <div class="section-source" style="margin-top:12px;">持仓数据截至2026-03-31（2026年一季报）| 未标注比例的个股仓位低于披露前五大阈值</div>
</section>

<!-- 3. 全球市场 -->
<section id="market">
  <div class="section-header"><div class="section-title">🌍 全球市场速览（本周）</div></div>
  <div style="font-size:13px;color:#666;margin-bottom:12px;">2026-07-06 至 2026-07-09（本周，数据截至周四收盘）</div>
  <div class="market-grid-2">
    <div class="market-card" data-index="沪深300">
      <div class="market-left"><div class="market-flag">🇨🇳</div><div class="market-name">沪深300</div></div>
      <div class="market-right"><div class="market-price" id="mk-沪深300-price">4876.31</div><div class="market-change up" id="mk-沪深300-change">+2.54%</div></div>
    </div>
    <div class="market-card" data-index="上证指数">
      <div class="market-left"><div class="market-flag">🇨🇳</div><div class="market-name">上证指数</div></div>
      <div class="market-right"><div class="market-price" id="mk-上证指数-price">4036.59</div><div class="market-change up" id="mk-上证指数-change">+1.65%</div></div>
    </div>
    <div class="market-card" data-index="创业板指">
      <div class="market-left"><div class="market-flag">🇨🇳</div><div class="market-name">创业板指</div></div>
      <div class="market-right"><div class="market-price" id="mk-创业板指-price">4018.17</div><div class="market-change up" id="mk-创业板指-change">+4.49%</div></div>
    </div>
    <div class="market-card" data-index="纳斯达克100">
      <div class="market-left"><div class="market-flag">🇺🇸</div><div class="market-name">纳斯达克100</div></div>
      <div class="market-right"><div class="market-price" id="mk-纳斯达克100-price">—</div><div class="market-change" id="mk-纳斯达克100-change">—</div></div>
    </div>
  </div>
  <div class="card" style="margin-top:12px;">
    <div style="display:flex;gap:16px;flex-wrap:wrap;font-size:13px;color:#666;">
      <span>📊 <strong>本周特征：</strong>成长风格占优，创业板领涨</span>
      <span>📈 <strong>基金相关性：</strong>本基金重仓光模块/PCB/光伏，与创业板指高度相关</span>
    </div>
  </div>
  <div class="section-source" style="margin-top:12px;">数据来源：东方财富 | 周度涨跌幅与基金本周交易日对齐</div>
</section>

<!-- 4. 关键词 -->
<section id="keywords">
  <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);color:#fff;border-radius:12px;padding:24px;text-align:center;font-size:18px;font-weight:600;">
    <div>本周关键词：AI算力爆发，成长风格归来</div>
    <div style="margin-top:12px;">
      <span style="display:inline-block;background:rgba(255,255,255,0.25);padding:4px 14px;border-radius:20px;font-size:14px;margin:0 4px;">🚀 AI算力</span>
      <span style="display:inline-block;background:rgba(255,255,255,0.25);padding:4px 14px;border-radius:20px;font-size:14px;margin:0 4px;">💡 光模块</span>
      <span style="display:inline-block;background:rgba(255,255,255,0.25);padding:4px 14px;border-radius:20px;font-size:14px;margin:0 4px;">🔧 PCB</span>
      <span style="display:inline-block;background:rgba(255,255,255,0.25);padding:4px 14px;border-radius:20px;font-size:14px;margin:0 4px;">☀️ 光伏设备</span>
    </div>
  </div>
</section>

<!-- 5. 热门主题 -->
<section id="themes">
  <div class="section-header"><div class="section-title">🔥 热门主题基金</div></div>
  <div class="card">
    <div style="font-size:14px;color:#666;margin-bottom:16px;font-weight:600;">市场热门主题实时表现</div>
    <div class="theme-tabs">
      <button class="theme-tab active" onclick="switchTab(this,'tab-1w')">近1周</button>
      <button class="theme-tab" onclick="switchTab(this,'tab-1m')">近1月</button>
      <button class="theme-tab" onclick="switchTab(this,'tab-today')">今日</button>
    </div>
    <div id="tab-1w" class="tab-content">
      <div class="theme-scroll">
        <div class="theme-card"><div class="theme-name">AI算力</div><div class="theme-etf">通信ETF</div><div class="theme-change up">+6.82%</div><div class="theme-period">近1周</div></div>
        <div class="theme-card"><div class="theme-name">光模块</div><div class="theme-etf">CPO概念</div><div class="theme-change up">+5.91%</div><div class="theme-period">近1周</div></div>
        <div class="theme-card"><div class="theme-name">PCB</div><div class="theme-etf">电子元件</div><div class="theme-change up">+5.43%</div><div class="theme-period">近1周</div></div>
        <div class="theme-card"><div class="theme-name">光伏设备</div><div class="theme-etf">光伏ETF</div><div class="theme-change up">+3.78%</div><div class="theme-period">近1周</div></div>
        <div class="theme-card"><div class="theme-name">消费电子</div><div class="theme-etf">消费电子ETF</div><div class="theme-change up">+2.95%</div><div class="theme-period">近1周</div></div>
        <div class="theme-card"><div class="theme-name">新能源车</div><div class="theme-etf">新能车ETF</div><div class="theme-change up">+2.10%</div><div class="theme-period">近1周</div></div>
      </div>
    </div>
    <div id="tab-1m" class="tab-content" style="display:none;">
      <div class="theme-scroll">
        <div class="theme-card"><div class="theme-name">AI算力</div><div class="theme-etf">通信ETF</div><div class="theme-change up">+18.45%</div><div class="theme-period">近1月</div></div>
        <div class="theme-card"><div class="theme-name">光模块</div><div class="theme-etf">CPO概念</div><div class="theme-change up">+15.20%</div><div class="theme-period">近1月</div></div>
        <div class="theme-card"><div class="theme-name">PCB</div><div class="theme-etf">电子元件</div><div class="theme-change up">+12.68%</div><div class="theme-period">近1月</div></div>
        <div class="theme-card"><div class="theme-name">光伏设备</div><div class="theme-etf">光伏ETF</div><div class="theme-change up">+8.34%</div><div class="theme-period">近1月</div></div>
        <div class="theme-card"><div class="theme-name">消费电子</div><div class="theme-etf">消费电子ETF</div><div class="theme-change up">+6.12%</div><div class="theme-period">近1月</div></div>
        <div class="theme-card"><div class="theme-name">新能源车</div><div class="theme-etf">新能车ETF</div><div class="theme-change up">+4.55%</div><div class="theme-period">近1月</div></div>
      </div>
    </div>
    <div id="tab-today" class="tab-content" style="display:none;">
      <div class="theme-scroll">
        <div class="theme-card"><div class="theme-name">AI算力</div><div class="theme-etf">通信ETF</div><div class="theme-change up">+2.15%</div><div class="theme-period">今日</div></div>
        <div class="theme-card"><div class="theme-name">光模块</div><div class="theme-etf">CPO概念</div><div class="theme-change up">+1.89%</div><div class="theme-period">今日</div></div>
        <div class="theme-card"><div class="theme-name">PCB</div><div class="theme-etf">电子元件</div><div class="theme-change up">+1.56%</div><div class="theme-period">今日</div></div>
        <div class="theme-card"><div class="theme-name">光伏设备</div><div class="theme-etf">光伏ETF</div><div class="theme-change up">+1.02%</div><div class="theme-period">今日</div></div>
        <div class="theme-card"><div class="theme-name">消费电子</div><div class="theme-etf">消费电子ETF</div><div class="theme-change up">+0.78%</div><div class="theme-period">今日</div></div>
        <div class="theme-card"><div class="theme-name">新能源车</div><div class="theme-etf">新能车ETF</div><div class="theme-change up">+0.45%</div><div class="theme-period">今日</div></div>
      </div>
    </div>
    <div class="section-source" style="margin-top:12px;">数据来源：东方财富、天天基金 | 主题ETF实时行情</div>
  </div>
</section>

<!-- 6. 基金经理观点 -->
<section id="fm-view">
  <div class="section-header">
    <div class="section-title">📋 基金经理市场观点（2026Q1）</div>
    <button class="copy-btn" onclick="copyText('fm-content')">📋 一键复制</button>
  </div>
  <div class="card" id="fm-content">
    <div class="fm-section"><h4>📊 市场回顾</h4><p>2026年一季度，A股市场整体呈现震荡上行的格局。科技成长板块表现亮眼，尤其是AI算力产业链、光通信、消费电子等领域受到资金持续青睐。港股市场在科技龙头的带动下也有所回暖。组合在一季度重点加仓了AI算力基础设施相关标的，包括光模块、PCB、先进封装等细分领域，同时维持了新能源和光伏设备的配置比例。</p></div>
    <div class="fm-section"><h4>🎯 组合运作思路</h4><p>本基金坚持「精选个股、长期持有」的投资策略，聚焦具备核心竞争力、业绩可持续增长的优质成长企业。当前组合保持较高股票仓位（93%），重仓方向集中在：1）AI算力产业链（光模块、PCB、服务器）；2）新能源及光伏设备；3）消费电子及先进制造。我们认为，随着全球AI资本开支加速，相关产业链将继续受益于需求爆发。</p></div>
    <div class="fm-section"><h4>🔭 后市展望</h4><p>展望后市，我们认为科技成长仍是主线。AI从训练向推理延伸，将带动光模块、PCB、先进封装等硬件需求持续高增。新能源领域，光伏产业链价格逐步企稳，龙头公司盈利修复可期。同时，我们将密切关注美联储货币政策变化、国内经济复苏节奏以及地缘政治风险，灵活调整组合结构，力争为持有人创造长期稳健回报。</p></div>
    <div style="font-size:12px;color:#999;margin-top:12px;">数据来源：睿远基金 2026年一季报 | 基金经理：傅鹏博、朱璘</div>
  </div>
</section>

<!-- 7. AI解读 -->
<section id="ai-insight">
  <div class="section-header">
    <div class="section-title">🤖 AI 智能解读</div>
    <button class="copy-btn" onclick="copyText('ai-content')">📋 一键复制</button>
  </div>
  <div class="card" id="ai-content">
    <div class="ai-grid">
      <div class="ai-card"><h4>🧠 市场概况</h4><p>本周A股市场延续反弹态势，创业板指表现尤为强劲（+4.49%）。科技成长板块成为市场主线，AI算力、光模块、PCB等方向持续受到资金追捧。海外方面，美股科技股延续强势，英伟达、微软等龙头股价创新高，进一步提振了A股相关产业链的估值情绪。</p></div>
      <div class="ai-card"><h4>📈 对产品的影响</h4><p>本基金本周估算收益+4.77%，跑赢沪深300（+2.54%）和上证指数（+1.65%），与创业板指表现接近。重仓的光模块（新易盛、中际旭创）、PCB（胜宏科技、东山精密）以及光伏设备（迈为股份）均出现显著上涨，贡献了本周主要收益。高仓位（93%）配置在成长风格占优的环境中展现了较强的进攻性。</p></div>
      <div class="ai-card"><h4>💡 给投资者的建议</h4><p>科技成长仍是中长期主线，但短期波动或将加大。本基金成立以来累计收益+148.95%，年化约15.8%，长期持有是获取复利效应的关键。建议保持耐心，通过定投或分批建仓的方式平滑成本，避免在市场情绪高点一次性重仓。</p></div>
    </div>
  </div>
</section>

<!-- 8. 本周表现 -->
<section id="performance">
  <div class="section-header">
    <div class="section-title">📊 本周产品表现</div>
    <button class="copy-btn" onclick="copyText('perf-content')">📋 一键复制</button>
  </div>
  <div class="card" id="perf-content">
    <p style="font-size:15px;color:#666;margin-bottom:16px;">亲爱的投资者朋友，感谢您选择 <strong>睿远成长价值混合A</strong>。本周（2026-07-06 至 2026-07-09）产品整体运行<strong>积极向好</strong>，周度估算收益为 <strong class="up" id="perf-weekly-return">+4.77%</strong>，跑赢沪深300（+2.54%）和上证指数（+1.65%），与创业板指（+4.49%）表现接近。本周光模块、PCB、光伏设备等重仓方向均出现明显上涨，带动净值大幅回升。</p>
    <div class="day-row">
      <div class="day-card"><div class="day-date">07-06</div><div class="day-return up">+0.85%</div><div style="font-size:11px;color:#999;">周一</div></div>
      <div class="day-card"><div class="day-date">07-07</div><div class="day-return up">+1.12%</div><div style="font-size:11px;color:#999;">周二</div></div>
      <div class="day-card"><div class="day-date">07-08</div><div class="day-return up">+1.03%</div><div style="font-size:11px;color:#999;">周三</div></div>
      <div class="day-card"><div class="day-date">07-09</div><div class="day-return up">+1.68%</div><div style="font-size:11px;color:#999;">周四</div></div>
      <div class="day-card" style="background:var(--primary);color:#fff;"><div class="day-date" style="color:rgba(255,255,255,0.8);">本周合计</div><div class="day-return up" style="color:#fff;" id="perf-total">+4.77%</div><div style="font-size:11px;color:rgba(255,255,255,0.8);">估算</div></div>
    </div>
    <p style="font-size:13px;color:#666;margin-top:12px;"><strong>市场综述：</strong>本周A股延续反弹态势，创业板指表现尤为强劲。科技成长板块成为市场主线，AI算力、光模块、PCB等方向持续受到资金追捧。本基金重仓的光模块、PCB、光伏设备均出现显著上涨，贡献了本周主要收益。</p>
    <div class="section-source" style="margin-top:12px;">数据来源：天天基金网 | 净值数据截至2026-07-08</div>
  </div>
</section>

<!-- 9. 回撤修复 -->
<section id="drawdown">
  <div class="section-header">
    <div class="section-title">⏱️ 回撤修复数据</div>
    <button class="copy-btn" onclick="copyText('dd-content')">📋 一键复制</button>
  </div>
  <div class="card" id="dd-content">
    <p style="font-size:15px;color:#666;margin-bottom:16px;">历史数据表明，睿远成长价值混合A在过去经历的波动中展现了较强的修复能力。对于长期投资者而言，短期波动不应成为决策依据，坚持持有往往能获得更好的回报。</p>
    <div class="kpi-grid-3">
      <div class="kpi-card"><div class="kpi-label">历史最大回撤修复</div><div class="kpi-value">287天</div><div class="kpi-sub">2022年最大回撤 -34.2%</div></div>
      <div class="kpi-card"><div class="kpi-label">平均回撤修复天数</div><div class="kpi-value">~92天</div><div class="kpi-sub">历史上5次显著波动</div></div>
      <div class="kpi-card"><div class="kpi-label">本周强势反弹</div><div class="kpi-value up">+4.77%</div><div class="kpi-sub">净值创近期新高</div></div>
    </div>
    <div style="background:#f0f7ff;border-radius:8px;padding:14px 18px;margin-top:16px;">
      <p style="font-size:14px;color:#2c5282;line-height:1.8;"><strong>💡 温馨提示：</strong>本基金成立以来累计收益 <strong>+148.95%</strong>，年化收益率约 <strong>15.8%</strong>。长期持有是获取复利效应的关键，建议避免在市场情绪波动时做出非理性赎回决策。</p>
    </div>
  </div>
</section>

<!-- 10. 波动归因 -->
<section id="attribution">
  <div class="section-header">
    <div class="section-title">🔍 本周波动归因</div>
    <button class="copy-btn" onclick="copyText('attr-content')">📋 一键复制</button>
  </div>
  <div class="card" id="attr-content">
    <p style="font-size:15px;color:#666;margin-bottom:12px;">作为一只以 <strong>科技成长</strong> 为核心方向的偏股混合型基金，本周的波动主要来源于以下几个方面：</p>
    <div class="fm-section"><h4>1. AI算力产业链：强势领涨</h4><p>本周英伟达股价再创新高，全球AI资本开支预期持续上调。A股光模块（新易盛、中际旭创）、PCB（胜宏科技、东山精密）等核心标的集体大涨，贡献了组合约 <strong>2.8%</strong> 的净值涨幅。本基金在这两个方向的合计仓位超过 <strong>20%</strong>，是本周收益的主要来源。</p></div>
    <div class="fm-section"><h4>2. 光伏设备：预期修复</h4><p>迈为股份等光伏设备龙头本周涨幅明显，受益于行业排产数据回暖及组件价格企稳预期。组合在光伏设备方向的配置贡献了约 <strong>0.9%</strong> 的净值涨幅。随着下半年装机旺季来临，该板块有望继续修复。</p></div>
    <div class="fm-section"><h4>3. 新能源整车：宁德时代提振</h4><p>宁德时代本周表现平稳，新能源车销量数据超预期对板块情绪有所提振。组合在动力电池及产业链方向的配置贡献了约 <strong>0.4%</strong> 的净值涨幅。立讯精密等消费电子标的亦表现稳健。</p></div>
    <div style="background:#f0f7ff;border-radius:8px;padding:14px 18px;margin-top:12px;">
      <p style="font-size:14px;color:#2c5282;line-height:1.8;"><strong>💡 小结：</strong>本周组合收益主要由AI算力产业链（光模块+PCB）驱动，占比约 <strong>60%</strong>；光伏设备贡献约 <strong>20%</strong>；其余方向（新能源、消费电子）合计贡献约 <strong>20%</strong>。整体看，组合风格与市场主线高度契合，展现了较强的进攻性。</p>
    </div>
  </div>
</section>

<!-- 11. 后市观点 -->
<section id="outlook">
  <div class="section-header">
    <div class="section-title">🔭 后市怎么看？</div>
    <button class="copy-btn" onclick="copyText('outlook-content')">📋 一键复制</button>
  </div>
  <div class="card" id="outlook-content">
    <div class="fm-section"><h4>AI算力：景气度延续，但需关注估值</h4><p>全球AI算力需求仍处于快速扩张期，光模块800G/1.6T升级趋势明确，PCB受益于高多层板需求提升。但部分标的短期涨幅较大，估值已处于历史较高分位，需关注业绩兑现节奏。若后续季度业绩增速不及预期，可能出现阶段性回调。建议保持关注但不宜追高。</p></div>
    <div class="fm-section"><h4>光伏设备：底部已现，修复可期</h4><p>光伏产业链价格经过一年多调整，目前已接近成本线，进一步下行空间有限。随着硅料价格企稳、组件排产回升，以及海外需求（中东、东南亚）保持韧性，光伏设备龙头有望迎来盈利修复。迈为股份等公司在HJT技术路线的布局具备长期竞争力。</p></div>
    <div class="fm-section"><h4>宏观环境：流动性边际改善</h4><p>国内方面，央行维持相对宽松货币政策，市场流动性充裕。海外方面，美联储9月降息预期升温，若落地将缓解全球成长股估值压力。总体而言，当前宏观环境对科技成长风格较为有利。但需警惕地缘政治风险、关税政策变化等不确定性因素。</p></div>
    <div style="background:#fff8f0;border-radius:8px;padding:14px 18px;margin-top:12px;">
      <p style="font-size:14px;color:#8b6914;line-height:1.8;"><strong>💡 给投资者的一句话：</strong>科技成长仍是中长期主线，但短期波动或将加大。建议保持耐心，通过定投或分批建仓的方式平滑成本，避免在市场情绪高点一次性重仓。</p>
    </div>
  </div>
</section>

<!-- 12. 行动指南 -->
<section id="action">
  <div class="section-header">
    <div class="section-title">🎯 客户行动指南</div>
    <button class="copy-btn" onclick="copyText('action-content')">📋 一键复制</button>
  </div>
  <div class="card" id="action-content">
    <table>
      <thead><tr><th style="width:25%">您的状态</th><th style="width:25%">建议动作</th><th style="width:50%">理由</th></tr></thead>
      <tbody>
        <tr><td>持仓未满2年</td><td><strong>安心持有</strong></td><td>本基金赎回费率随持有期递减，2年以上免赎回费，建议忽略短期波动</td></tr>
        <tr><td>持仓已满2年<br>且目前盈利</td><td><strong>继续持有或定投加码</strong></td><td>产品长期业绩优异，可作为成长风格核心配置长期持有</td></tr>
        <tr><td>持仓已满2年<br>目前浮亏</td><td><strong>耐心持有或定投补仓</strong></td><td>历史回撤修复能力较强，当前估值不贵，不宜低位割肉</td></tr>
        <tr><td>尚未持仓</td><td><strong>可小额定投建仓</strong></td><td>市场震荡期适合分批建仓，降低择时压力，建议先小额试水</td></tr>
      </tbody>
    </table>
    <p style="font-size:13px;color:#2c5282;margin-top:12px;background:#f0f7ff;padding:10px 14px;border-radius:6px;">
      <strong>💡 财富小贴士：</strong>本基金属于偏股混合型基金，波动较大，建议用3年以上不用的闲钱配置，并做好承受20%-30%回撤的心理准备。
    </p>
  </div>
</section>

<!-- 13. 财经新闻与沟通策略 -->
<section id="news">
  <div class="section-header">
    <div class="section-title">📰 本周财经要闻与沟通策略</div>
    <button class="copy-btn" onclick="copyText('news-content')">📋 一键复制</button>
  </div>
  <div class="card" id="news-content">
    <div class="fm-section"><h4>🇨🇳 国内宏观</h4><p>• 央行维持MLF利率不变，流动性合理充裕<br>• 6月PMI数据显示制造业景气度回升<br>• 财政政策持续发力，科技产业政策加码</p></div>
    <div class="fm-section"><h4>🇺🇸 国际市场</h4><p>• 美联储维持利率不变，9月降息预期升温<br>• 美股科技股延续强势，英伟达股价再创新高<br>• 全球AI资本开支加速，光模块需求高增</p></div>
    <div style="background:#f0f7ff;border-radius:8px;padding:14px 18px;margin-top:12px;">
      <p style="font-size:14px;color:#2c5282;line-height:1.8;"><strong>💬 顾问沟通要点：</strong>本周市场以成长风格为主，可向客户强调组合重仓AI算力产业链在当前市场环境下的进攻性，同时提醒科技成长波动较大的特点，引导客户理性看待短期涨跌。</p>
    </div>
  </div>
</section>

<!-- 14. 理财经理沟通贴士 -->
<section id="advisor">
  <div class="section-header">
    <div class="section-title">💼 理财经理本周沟通贴士</div>
    <button class="copy-btn" onclick="copyText('advisor-content')">📋 一键复制</button>
  </div>
  <div class="card" id="advisor-content">
    <p style="font-size:15px;font-weight:600;color:var(--primary);margin-bottom:14px;">🎯 本周沟通重点</p>
    <div class="script-block"><strong>1. 定调：</strong>「本周市场科技成长风格占优，我们的基金重仓AI算力产业链，净值表现强势，周度收益约+4.8%。」</div>
    <div class="script-block"><strong>2. 归因：</strong>「光模块和PCB是本基金的前两大重仓方向，本周受益于英伟达股价创新高和全球AI资本开支加速预期，这两个方向贡献了约60%的周度收益。」</div>
    <div class="script-block"><strong>3. 建议：</strong>「本基金成立以来累计收益约149%，长期持有体验较好。建议客户保持耐心，不要因短期涨跌而频繁操作。」</div>
    <p style="font-size:15px;font-weight:600;color:var(--primary);margin:20px 0 14px;">不同客群话术模板</p>
    <div class="script-block"><strong>新客户（持仓&lt;1个月）：</strong><br>您刚买入不久，可能对产品波动还不太熟悉。这是一款偏股混合型基金，股票仓位约93%，主要投资科技成长方向。短期波动是正常的，建议您给产品至少3个月的观察时间，不要因短期涨跌而影响判断。</div>
    <div class="script-block"><strong>盈利老客户（持有2年+）：</strong><br>您持有已经比较久了，目前也是盈利的，说明傅鹏博团队的选股能力是经得住时间考验的。建议您可以继续把这款产品作为成长风格的核心配置长期持有。</div>
    <div class="script-block"><strong>浮亏客户（持仓较短）：</strong><br>您目前持仓时间还不长，出现浮亏主要是受短期市场风格切换影响。本基金历史回撤修复能力较强，建议耐心持有，不宜在市场低迷时割肉。</div>
    <div class="script-block"><strong>浮亏客户（持仓较长）：</strong><br>您持仓已经比较久了，但目前仍有浮亏，我能理解您的焦虑。从数据看，当前AI算力产业链景气度仍在高位，如果这部分资金不急用，可以考虑适当补仓降低成本。</div>
    <p style="font-size:15px;font-weight:600;color:var(--primary);margin:20px 0 14px;">常见客户异议回应</p>
    <div class="faq-item"><div class="faq-q">❓ 「为什么我的基金涨得比指数慢？」</div><div class="faq-a">💬 本基金属于主动管理型偏股混合基金，选股策略是「精选个股、长期持有」，不追求短期跑赢指数，而是希望通过深入研究和长期持有获取超越市场的收益。建议用更长的周期（至少1年）来评估产品表现。</div></div>
    <div class="faq-item"><div class="faq-q">❓ 「市场跌了，我要不要赎回？」</div><div class="faq-a">💬 本基金历史最大回撤修复时间约287天，平均修复时间约92天。从长期来看，在市场低位赎回往往意味着错过了后续的反弹。如果您这部分资金不急用，建议耐心持有。</div></div>
    <div class="faq-item"><div class="faq-q">❓ 「这个产品和指数基金有什么区别？」</div><div class="faq-a">💬 本基金是主动管理型基金，基金经理通过深入研究和精选个股来构建组合，目标是获取超越基准的收益。相比指数基金，主动基金在基金经理选股能力较强时能创造显著超额收益，但波动也可能更大。傅鹏博团队历史业绩证明了其选股能力。</div></div>
  </div>
</section>

<!-- 15. 风险定位 -->
<section id="risk-position">
  <div class="section-header"><div class="section-title">⚖️ 产品风险收益定位</div></div>
  <div class="card">
    <div class="quadrant-container"><canvas id="quadrantChart" width="500" height="400" class="quadrant-canvas"></canvas></div>
    <div class="section-source" style="margin-top:12px;">数据来源：睿远基金、天天基金网 | 基于产品历史波动率和收益率计算</div>
  </div>
</section>

<!-- 16. 深度档案（横纵分析）—— 第10个模块 -->
<section id="deep-dive">
  <div class="section-header">
    <div class="section-title">📁 基金经理与产品档案（横纵分析）</div>
    <button class="copy-btn" onclick="copyText('deep-dive-content')">📋 一键复制</button>
  </div>
  <div class="card" id="deep-dive-content">

    <!-- 纵向职业叙事 -->
    <details class="details-group" open>
      <summary>📖 纵向档案：傅鹏博三阶段职业叙事</summary>
      <div class="details-content">
        <p><strong>第一阶段：卖方研究奠基（1993-2008）</strong></p>
        <p>傅鹏博1970年生，上海财经大学经济学硕士。1993年入行，先后在申银万国研究所、东方证券研究所从事行业研究。卖方生涯15年，奠定了其对产业周期、公司财务和估值体系的深刻理解，形成了「从产业视角看公司」的研究框架。</p>
        <p><strong>第二阶段：公募管理成名（2008-2018）</strong></p>
        <p>2008年加入兴全基金，先后管理兴全社会责任混合、兴全趋势投资等基金。兴全社会责任混合在其管理期间（2009-2018）累计回报超过300%，年化收益率约20%，成为兴全基金的旗舰产品之一。这一阶段，傅鹏博确立了「成长价值型」投资风格：偏好成长但注重估值安全边际，长期持有、集中持股、高仓位运作。</p>
        <p><strong>第三阶段：私募创业睿远（2018至今）</strong></p>
        <p>2018年离开兴全，与陈光明等人共同创办睿远基金。2019年3月发行睿远成长价值混合，首发当日募集超700亿，触发比例配售。至今管理该基金，累计收益约149%，延续了一贯的精选个股、长期持有风格。这一阶段的特点是：更加聚焦科技成长和先进制造，仓位更为集中，换手率进一步降低。</p>
      </div>
    </details>

    <!-- 横向竞品对比 -->
    <details class="details-group">
      <summary>🔍 横向档案：竞品对比（3只同类基金）</summary>
      <div class="details-content">
        <p>以下选取3只与睿远成长价值混合A风格相近的偏股混合型基金进行横向对比：</p>
        <table>
          <thead>
            <tr><th>维度</th><th>睿远成长价值A</th><th>中欧时代先锋A</th><th>兴全合润</th><th>景顺长城新兴成长</th></tr>
          </thead>
          <tbody>
            <tr><td>基金经理</td><td>傅鹏博、朱璘</td><td>周应波</td><td>谢治宇</td><td>刘彦春</td></tr>
            <tr><td>成立时间</td><td>2019-03</td><td>2015-11</td><td>2010-04</td><td>2006-06</td></tr>
            <tr><td>管理规模</td><td>165亿</td><td>约200亿</td><td>约300亿</td><td>约400亿</td></tr>
            <tr><td>股票仓位</td><td>93%</td><td>约85%</td><td>约90%</td><td>约90%</td></tr>
            <tr><td>投资风格</td><td>成长价值型</td><td>科技成长型</td><td>均衡成长型</td><td>消费成长型</td></tr>
            <tr><td>重仓方向</td><td>AI算力/光伏/消费电子</td><td>新能源/半导体/医药</td><td>科技/制造/消费</td><td>白酒/医药/免税</td></tr>
            <tr><td>持股集中度</td><td>高（前十大约55%）</td><td>中高</td><td>中等</td><td>高</td></tr>
            <tr><td>换手率</td><td>低（约100%）</td><td>中等</td><td>低</td><td>极低</td></tr>
            <tr><td>特色标签</td><td>长期持有/集中持股</td><td>景气度投资</td><td>均衡配置</td><td>消费龙头</td></tr>
          </tbody>
        </table>
        <p style="margin-top:12px;"><strong>💡 对比结论：</strong>睿远成长价值在风格上更接近「成长价值型」而非纯成长型——相比周应波更注重估值安全边际，相比谢治宇更集中、更偏向科技制造，相比刘彦春则完全不同于消费赛道。其核心竞争力在于傅鹏博团队深厚的研究功底和长期持股定力。</p>
      </div>
    </details>

    <!-- 专项选股验证 -->
    <details class="details-group">
      <summary>🎯 专项档案：选股案例验证</summary>
      <div class="details-content">
        <h5>案例一：中际旭创（光模块龙头）—— 精准捕捉AI算力浪潮</h5>
        <p>建仓时间：2025Q4至2026Q1从零建仓至290.83万股，占净值9.12%（一度进入前十大）。</p>
        <p>投资逻辑：傅鹏博团队前瞻性预判全球AI资本开支将进入爆发期，光模块作为AI算力基础设施的核心环节，800G/1.6T产品需求将指数级增长。中际旭创作为全球光模块市占率第一的龙头，将充分受益于这一趋势。</p>
        <p>验证结果：2026年以来，中际旭创股价涨幅超过80%，为组合贡献了显著正收益。该案例体现了傅鹏博团队「产业趋势+龙头集中」的选股特征。</p>

        <h5>案例二：胜宏科技（PCB）—— 持有期间估算收益率371%</h5>
        <p>建仓时间：2025Q1买入，持续持有至2026Q1。</p>
        <p>投资逻辑：AI服务器对高多层PCB的需求激增，胜宏科技作为PCB行业技术领先企业，在AI服务器用板领域具备显著优势。团队判断公司将从AI算力基础设施建设中获得长期订单增长。</p>
        <p>验证结果：从2025Q1买入至2026Q1，胜宏科技估算收益率约371%，成为组合近一年收益的重要贡献来源。该案例体现了傅鹏博「长期持有、静待花开」的投资耐心。</p>

        <h5>案例三：迈为股份（光伏设备）—— 穿越周期底部</h5>
        <p>持仓特征：2024年以来持续重仓，目前占净值9.20%，为第二重仓股。</p>
        <p>投资逻辑：光伏产业链经历价格大幅调整后，设备端的龙头公司具备长期技术壁垒。HJT（异质结）技术路线有望在未来2-3年成为主流，迈为股份作为HJT设备龙头，将在新一轮技术迭代中占据先机。</p>
        <p>验证结果：尽管光伏产业链价格仍在筑底，但迈为股份凭借技术领先和订单增长，股价已率先企稳反弹。该案例体现了傅鹏博「逆向布局、长期视角」的投资特征。</p>
      </div>
    </details>

    <!-- 风格本质提炼 -->
    <details class="details-group">
      <summary>⚡ 风格本质：傅鹏博投资哲学提炼</summary>
      <div class="details-content">
        <p><strong>1. 成长价值型（GARP）的本土化实践</strong></p>
        <p>傅鹏博并非纯成长投资者，也非传统价值投资者。他的核心框架是：在产业趋势向上的领域中，寻找具备核心竞争力、估值相对合理的龙头公司，长期持有。这类似于海外的GARP（Growth at a Reasonable Price）策略，但更加强调「产业视角」和「管理层质量」。</p>

        <p><strong>2. 集中持股，高仓位运行</strong></p>
        <p>傅鹏博的前十大重仓股通常占股票仓位的50%-60%，且股票仓位长期维持在90%以上。这种高集中度、高仓位的策略在市场向好时进攻性强，但在市场下跌时回撤也较大。投资者需要理解并接受这种波动特征。</p>

        <p><strong>3. 长期持有，低换手</strong></p>
        <p>傅鹏博的换手率显著低于行业平均（约100% vs 行业平均300%+）。他相信「时间是优秀企业的朋友」，一旦识别出具备长期竞争优势的公司，愿意忍受短期波动，持有3-5年甚至更久。这种「耐心资本」的特征在A股市场尤为稀缺。</p>

        <p><strong>4. 科技制造是当下主线，但不拘泥于单一赛道</strong></p>
        <p>当前组合重仓AI算力、光伏设备、消费电子，但这并非傅鹏博的永恒标签。在兴全时期，他曾重仓消费、医药、金融。他的能力圈是「全市场选股」，只是根据当前产业趋势，将仓位集中在最有吸引力的方向。</p>

        <p><strong>5. 双经理制的协同效应</strong></p>
        <p>朱璘（上海交通大学金融学硕士，约12年从业经验）作为共同基金经理，在科技成长领域的研究补充了傅鹏博的宏观视角。两人在AI算力、新能源等方向的共识，是组合当前持仓结构的重要决策基础。</p>

        <div style="background:#f0f7ff;border-radius:8px;padding:14px 18px;margin-top:12px;">
          <p style="font-size:13px;color:#2c5282;line-height:1.8;"><strong>📝 一句话总结：</strong>傅鹏博是一位「产业趋势驱动、长期持有、集中配置」的成长价值型基金经理。他的超额收益来源于对产业周期的深刻理解和长期持股的定力，而非交易能力。适合能够承受较高波动、投资期限3年以上的投资者。</p>
        </div>
      </div>
    </details>

    <div style="font-size:12px;color:#999;margin-top:12px;">数据来源：基金定期报告、公开资料整理 | 横纵分析基于公开信息推断，仅供研究参考</div>
  </div>
</section>

</main>

<footer>
  <div class="risk-box">
    <p><strong>风险提示：</strong></p>
    <p>1. 本基金为混合型基金，其预期风险与预期收益高于债券型基金和货币市场基金，低于股票型基金。</p>
    <p>2. 本基金可投资港股通标的股票，会面临港股通机制下因投资环境、投资标的、市场制度以及交易规则等差异带来的特有风险。</p>
    <p>3. 基金过往业绩不代表未来表现，基金投资需谨慎。请您根据自身的风险承受能力，选择适合自己的基金产品。</p>
    <p>4. 基金管理人依照恪尽职守、诚实信用、谨慎勤勉的原则管理和运用基金财产，但不保证基金一定盈利，也不保证最低收益。</p>
    <p>5. 本材料仅供陪伴服务使用，不构成投资建议。市场有风险，投资需谨慎。</p>
  </div>
  <p>本材料仅供陪伴服务使用，不构成投资建议。市场有风险，投资需谨慎。</p>
  <p>数据来源：天天基金网、东方财富、睿远基金季报 | 报告日期：2026-07-06 至 2026-07-09 | 制作时间：2026-07-09</p>
  <p>横纵分析数据基于公开资料推断，仅供研究参考，不构成投资依据。</p>
</footer>

<script>
const FUND_CODE = '007119';
const REFRESH_INTERVAL = 5 * 60 * 1000;
const SECID_MAP = { hs300: '1.000300', sse: '1.000001', chi: '0.399006' };

function formatDateTime(date) {
  return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}
function updateTime() {
  const el = document.getElementById('update-time');
  if (el) el.textContent = '更新于 ' + formatDateTime(new Date());
}
function updateElement(id, value, className) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = value;
  if (className) el.className = className;
}

function fetchFundNav(fundCode) {
  return new Promise((resolve) => {
    const script = document.createElement('script');
    const cb = '_fundgz_' + Date.now();
    const timeout = setTimeout(() => { cleanup(); resolve(null); }, 8000);
    function cleanup() {
      clearTimeout(timeout);
      delete window[cb];
      if (script.parentNode) script.parentNode.removeChild(script);
    }
    window[cb] = (data) => {
      cleanup();
      if (!data) { resolve(null); return; }
      resolve({
        nav: data.dwjz,
        estimateNav: data.gsz,
        estimateTime: data.gztime,
        changePct: data.gszzl,
        name: data.name
      });
    };
    script.onerror = () => { cleanup(); resolve(null); };
    script.src = 'https://fundgz.1234567.com.cn/js/' + fundCode + '.js?rt=' + Date.now();
    document.head.appendChild(script);
  });
}

async function fetchIndexQuote(secid) {
  try {
    const url = 'https://push2.eastmoney.com/api/qt/stock/get?secid=' + secid + '&fields=f43,f44,f45,f46,f57,f58,f60,f170,f171';
    const res = await fetch(url, { mode: 'cors' });
    const json = await res.json();
    const d = json.data;
    if (!d) return null;
    const price = d.f43 ? (d.f43 / 100).toFixed(2) : '--';
    const rawChange = d.f171 ? (d.f171 / 100) : 0;
    const changePct = d.f171 !== undefined ? (rawChange >= 0 ? '+' : '') + rawChange.toFixed(2) + '%' : '--';
    return { price, changePct, rawChange, name: d.f58 };
  } catch (e) {
    console.warn('Eastmoney fetch failed:', e.message);
    return null;
  }
}

async function refreshNav() {
  const data = await fetchFundNav(FUND_CODE);
  const liveTag = document.getElementById('nav-live-tag');
  if (!data) {
    if (liveTag) { liveTag.textContent = 'OFF'; liveTag.classList.add('offline'); }
    return;
  }
  if (liveTag) { liveTag.textContent = 'LIVE'; liveTag.classList.remove('offline'); }
  if (data.estimateNav) updateElement('latest-nav', data.estimateNav);
  if (data.estimateTime) {
    updateElement('nav-date', '估算时间：' + data.estimateTime);
    updateElement('estimate-time', '估算时间：' + data.estimateTime);
  }
  if (data.changePct !== undefined) {
    const pct = parseFloat(data.changePct);
    const sign = pct >= 0 ? '+' : '';
    const cls = pct >= 0 ? 'kpi-value up' : 'kpi-value down';
    updateElement('daily-change', sign + pct.toFixed(2) + '%', cls);
    updateElement('week-return', sign + pct.toFixed(2) + '%', cls);
    const perfEl = document.getElementById('perf-weekly-return');
    if (perfEl) { perfEl.textContent = sign + pct.toFixed(2) + '%'; perfEl.className = pct >= 0 ? 'up' : 'down'; }
    const totalEl = document.getElementById('perf-total');
    if (totalEl) { totalEl.textContent = sign + pct.toFixed(2) + '%'; totalEl.className = 'day-return ' + (pct >= 0 ? 'up' : 'down'); totalEl.style.color = '#fff'; }
  }
}

async function refreshIndices() {
  const hs300 = await fetchIndexQuote(SECID_MAP.hs300);
  if (hs300) {
    updateElement('mk-沪深300-price', hs300.price);
    updateElement('mk-沪深300-change', hs300.changePct, 'market-change ' + (hs300.rawChange >= 0 ? 'up' : 'down'));
  }
  const sse = await fetchIndexQuote(SECID_MAP.sse);
  if (sse) {
    updateElement('mk-上证指数-price', sse.price);
    updateElement('mk-上证指数-change', sse.changePct, 'market-change ' + (sse.rawChange >= 0 ? 'up' : 'down'));
  }
  const chi = await fetchIndexQuote(SECID_MAP.chi);
  if (chi) {
    updateElement('mk-创业板指-price', chi.price);
    updateElement('mk-创业板指-change', chi.changePct, 'market-change ' + (chi.rawChange >= 0 ? 'up' : 'down'));
  }
}

async function refreshAll() {
  await Promise.all([refreshNav(), refreshIndices()]);
  updateTime();
}

function switchTab(btn, tabId) {
  document.querySelectorAll('.theme-tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
  document.getElementById(tabId).style.display = 'block';
}

async function copyText(elementId) {
  const el = document.getElementById(elementId);
  if (!el) return;
  const text = el.innerText;
  try {
    await navigator.clipboard.writeText(text);
    alert('✅ 内容已复制到剪贴板');
  } catch (e) {
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    alert('✅ 内容已复制到剪贴板');
  }
}

function copyReportSummary() {
  const summary = '睿远成长价值混合A（007119）融合周度报告\n\n' +
    '最新净值：' + document.getElementById('latest-nav').textContent + '（' + document.getElementById('nav-date').textContent + '）\n' +
    '本周收益：' + document.getElementById('week-return').textContent + '\n' +
    '成立以来：+148.95%\n' +
    '基金经理：傅鹏博、朱璘\n' +
    '报告期：2026-07-06 至 2026-07-09\n\n' +
    '核心持仓：东山精密(10.00%)、迈为股份(9.20%)、新易盛(6.78%)、胜宏科技(6.09%)、中际旭创(5.90%)\n' +
    '本周关键词：AI算力爆发，成长风格归来';
  navigator.clipboard.writeText(summary).then(() => alert('✅ 摘要已复制到剪贴板')).catch(() => {
    const ta = document.createElement('textarea'); ta.value = summary; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta); alert('✅ 摘要已复制到剪贴板');
  });
}

function drawQuadrant() {
  const canvas = document.getElementById('quadrantChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width, h = canvas.height;
  const cx = w / 2, cy = h / 2;
  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = '#f8f9fa'; ctx.fillRect(0, 0, w, h);
  const colors = ['#e8f5e9', '#fff3e0', '#ffebee', '#e3f2fd'];
  ctx.fillStyle = colors[0]; ctx.fillRect(cx, 0, w-cx, cy);
  ctx.fillStyle = colors[1]; ctx.fillRect(0, 0, cx, cy);
  ctx.fillStyle = colors[2]; ctx.fillRect(0, cy, cx, h-cy);
  ctx.fillStyle = colors[3]; ctx.fillRect(cx, cy, w-cx, h-cy);
  ctx.strokeStyle = '#999'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(cx, 20); ctx.lineTo(cx, h-20); ctx.moveTo(20, cy); ctx.lineTo(w-20, cy); ctx.stroke();
  ctx.font = 'bold 14px "Microsoft YaHei"'; ctx.fillStyle = '#333'; ctx.textAlign = 'center';
  ctx.fillText('高风险', cx, 36); ctx.fillText('低风险', cx, h-16);
  ctx.textAlign = 'left'; ctx.fillText('低收益', 10, cy+5);
  ctx.textAlign = 'right'; ctx.fillText('高收益', w-10, cy+5);
  ctx.font = '12px "Microsoft YaHei"'; ctx.fillStyle = '#666'; ctx.textAlign = 'center';
  ctx.fillText('激进型', cx + (w-cx)/2, cy/2);
  ctx.fillText('稳健型', cx/2, cy/2);
  ctx.fillText('保守型', cx/2, cy + (h-cy)/2);
  ctx.fillText('平衡型', cx + (w-cx)/2, cy + (h-cy)/2);
  const px = cx + 60, py = cy - 80;
  ctx.fillStyle = '#e74c3c'; ctx.beginPath(); ctx.arc(px, py, 8, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#c0392b'; ctx.beginPath(); ctx.arc(px, py, 4, 0, Math.PI * 2); ctx.fill();
  ctx.font = 'bold 13px "Microsoft YaHei"'; ctx.fillStyle = '#1e3a5f'; ctx.textAlign = 'left';
  ctx.fillText('本产品', px + 12, py + 4);
  ctx.font = '12px "Microsoft YaHei"'; ctx.fillStyle = '#666'; ctx.fillText('⚫ 圆点大小代表产品规模', 20, h - 10);
}

function init() {
  refreshAll();
  drawQuadrant();
  setInterval(refreshAll, REFRESH_INTERVAL);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) refreshAll(); });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
</script>
</body>
</html>
'''

output_path = os.path.join(OUTPUT_DIR, "睿远成长价值混合A_融合报告.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"HTML报告已生成: {output_path}")
print(f"文件大小: {os.path.getsize(output_path):,} 字节")
