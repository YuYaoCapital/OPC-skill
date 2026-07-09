---
name: portfolio-week-companion
description: >
  基金投顾产品组合周度陪伴报告生成工具。面向理财经理与基金投顾团队，
  基于当周市场数据、组合净值、持仓信息、投研观点，自动生成面向客户的
  单页 HTML 周度陪伴报告。报告覆盖组合概况、资产表现、波动归因、后市观点、
  客户服务话术等 15 个模块，支持网页浏览、PDF 导出、嵌入公众号/企微分发。
  当用户需要"生成周度陪伴报告"、"产品组合周报"、"FOF 周报"、"客户陪伴网页"、
  "周度报告 HTML"时触发。
triggers:
  - 生成周度陪伴报告
  - 产品组合周报
  - FOF 周报
  - 客户陪伴网页
  - 周度报告 HTML
  - 组合周度回顾
  - 基金投顾周报
  - 陪伴报告
  - weekly companion report
  - portfolio weekly report
inputs:
  - product_code: 产品代码（必填）
  - product_name: 产品全称（必填）
  - report_period: 报告期（当周起始日—结束日，可选，默认上周五至本周五）
  - fund_manager: 基金经理（可选）
  - risk_level: 风险等级（可选）
  - target_client_profile: 适合客户画像（可选）
  - portfolio_nav_data: 组合每日净值序列（可由 Vega/Orion 提供）
  - portfolio_holdings: 组合持仓数据（可由 Vega 提供）
  - market_data: 当周市场行情数据（可由 china-market-data 提供）
  - research_views: 投研观点（可由 Helios/Terra/Mercury 提供）
  - attribution_data: 绩效归因数据（可由 Orion 提供）
outputs:
  - 单页 HTML 文件（默认）
  - PDF 文件（可选，打印导出）
  - H5 长图（可选，公众号/小程序嵌入）
  - Word 文件（可选，客户要求时）
---

# 产品组合周度陪伴报告

## 一、能力定位

`portfolio-week-companion` 负责将当周市场变化、组合表现、波动原因、后市观点转化为客户可读、可感、可操作的陪伴内容，输出为**单页 HTML 网页报告**。

报告由 Xueqi（产品中心）主笔，投研策略部（Atlas/Helios/Terra/Mercury/Orion）提供研究输入，投顾服务部（Mira/Belle/Dylan）负责客户化润色与分发，Sage（合规风控部）审核合规与话术。

> **参考样例**：`https://fof-weekly-report.pages.dev/`

> **能力矩阵（互补关系）**：
> | Skill | 输出格式 | 面向对象 | 使用场景 |
> |-------|----------|----------|----------|
> | `portfolio-week-companion` | **单页 HTML 网页** | 客户 | 投后陪伴，实时数据，沟通话术 |
> | `fund-weekly-review` | **Markdown / PDF** | 理财经理 | 专业周度回顾，持仓归因，主动权益/量化双框架 |
> | `fund-weekly-hybrid` | **Markdown / PDF** | 理财经理 | 融合版：周度回顾 + 基金经理横纵分析法深度档案 |
> 
> 当用户明确要求「面向客户的网页」「客户陪伴」「HTML」时触发本 Skill；当用户要求「PDF报告」「专业回顾」「深度分析」时，引导至 `fund-weekly-review` 或 `fund-weekly-hybrid`。

---

## 二、触发条件

| 触发词 | 示例 |
|--------|------|
| 周度陪伴报告 | "生成长盈计划的周度陪伴报告" |
| 组合周报 | "帮我做一份组合周报" |
| FOF 周报 | "这只 FOF 的周报怎么写" |
| 客户陪伴网页 | "输出客户陪伴的 HTML 报告" |
| 周度报告 | "本周的周度报告" |
| weekly report | "generate weekly companion report for product X" |

---

## 三、前置条件与输入准备

在生成报告前，须确认或获取以下输入（按优先级排序）：

### 3.1 必填输入

| 字段 | 说明 | 来源 |
|------|------|------|
| `product_code` | 产品代码（如 025313） | 用户输入 / 产品信息库 |
| `product_name` | 产品全称 | 用户输入 / 产品信息库 |
| `report_period_start` | 报告期起始日 | 默认上周五 |
| `report_period_end` | 报告期结束日 | 默认本周五 |

### 3.2 推荐输入（影响报告质量）

| 字段 | 说明 | 来源 |
|------|------|------|
| `portfolio_nav_data` | 组合每日净值序列 | Vega / Orion |
| `portfolio_holdings` | 组合持仓基金列表（名称、代码、占比） | Vega |
| `weekly_return` | 本周组合涨跌幅 | Orion |
| `since_inception_return` | 成立以来收益 | Orion |
| `max_drawdown_history` | 历史最大回撤及修复天数 | Orion |
| `market_indices` | A股/港股/美股/黄金当周行情 | `china-market-data` |
| `research_views` | 投研周度观点（固收/权益/宏观） | Helios / Terra / Mercury |
| `attribution_data` | Brinson 绩效归因 | Orion |
| `fund_quarterly_views` | 底层基金经理季报观点 | Castor |

### 3.3 可选输入

| 字段 | 说明 |
|------|------|
| `fund_manager` | 基金经理姓名 |
| `risk_level` | 产品风险等级 |
| `target_client_profile` | 适合客户画像 |
| `custom_themes` | 自定义热门主题列表 |
| `special_events` | 当周重大市场事件 |

### 3.4 自动日期计算（报告期动态确定）

报告期**不以固定上周五为锚**，而是根据**查询当天（today）**自动确定本周交易区间：

```javascript
// 自动日期计算逻辑（JavaScript）
function getWeekRange(today = new Date()) {
  const day = today.getDay(); // 0=周日, 1=周一...6=周六
  const monday = new Date(today);
  monday.setDate(today.getDate() - ((day + 6) % 7)); // 回溯到本周一
  const friday = new Date(monday);
  friday.setDate(monday.getDate() + 4); // 本周五
  
  // 如果今天是周五之前，报告期显示为「本周一至今天」；若周五及之后，显示完整周
  const endDate = (day >= 5) ? friday : today;
  return {
    start: format(monday),   // 如 2026-07-06
    end: format(endDate),    // 如 2026-07-08（今天）或 2026-07-10（周五）
    isPartial: day < 5       // 是否为周中部分报告
  };
}
```

**规则**：
- 周一至周四查询：报告期为「本周一 — 今天」，标注「数据截至X月X日，本周尚未结束」
- 周五至周日查询：报告期为完整周「本周一 — 本周五」
- 节假日自动顺延（通过交易日历库判断）
- 净值日期取产品最新公布的净值日（通常T-1或T-2）

---

## 四、报告模块结构（15 模块标准模板）

报告采用**单页长滚动**结构，按以下 15 个模块依次排列。每个模块包含「内容规范」「数据字段」「展示形式」「协作输入」四个维度。

---

### 模块 1：报告头（Header）

| 维度 | 说明 |
|------|------|
| **内容** | 报告名称、报告期（当周起始日—结束日）、产品全称、产品代码、风险等级、适合客户画像 |
| **数据字段** | `report_name`, `report_period_start`, `report_period_end`, `product_name`, `product_code`, `risk_level`, `target_client_profile` |
| **展示形式** | 页面顶部通栏，左侧产品名称大标题，右侧报告期；下方一行小字标注风险等级与适合客户画像 |
| **协作输入** | 从产品信息库获取 |

---

### 模块 2：产品概况（Product Overview）

| 维度 | 说明 |
|------|------|
| **内容** | 最新净值（含日期）、日涨跌、本周收益、成立以来收益；基金经理姓名；核心持仓基金实时净值列表（基金名称、代码、最新净值、日涨跌） |
| **数据字段** | `nav`, `nav_date`, `daily_return`, `weekly_return`, `since_inception_return`, `fund_manager`; 持仓数组 `{fund_name, fund_code, fund_nav, fund_daily_return}` |
| **展示形式** | 上方一行大数字卡片（净值/本周收益/成立以来收益），绿色涨/红色跌；下方持仓基金以网格卡片或表格展示，每只基金一行 |
| **协作输入** | Vega 提供组合净值、持仓数据；天天基金/东方财富提供底层基金实时净值 |
| **客户化要点** | 持仓数据须注明「截至 XXXX 年 XX 季报」，净值数据注明「实时获取」；若基金数量过多，仅展示 TOP10 持仓 |

---

### 模块 3：全球市场速览（Global Market Snapshot）

| 维度 | 说明 |
|------|------|
| **内容** | A股（沪深300）、港股（恒生指数）、美股（标普500）当周收盘价与涨跌幅；黄金（COMEX）价格与涨跌幅；沪深300 PE及分位、10年期国债收益率、股债性价比 |
| **数据字段** | `hs300_close`, `hs300_weekly_return`, `hsi_close`, `hsi_weekly_return`, `sp500_close`, `sp500_weekly_return`, `gold_price`, `gold_weekly_return`, `hs300_pe`, `hs300_pe_percentile`, `cn_10y_yield`, `equity_bond_spread` |
| **展示形式** | 图标+国旗/市场标识的卡片式布局，每个市场一个卡片；下方一行估值指标，用标签形式展示（如「PE 12.0 \| 合理」「估值分位 35% \| 中等」） |
| **协作输入** | `china-market-data` 提供 A 股/港股数据；Yahoo Finance 提供美股数据；东方财富/AKShare 提供黄金、国债、估值数据 |

---

### 模块 4：本周关键词（Weekly Keywords）

| 维度 | 说明 |
|------|------|
| **内容** | 用 1 个短句（≤15 字）+ 3 个关键词标签，概括当周市场核心特征 |
| **数据字段** | `weekly_keyword_sentence`, `weekly_tags[]` |
| **展示形式** | 醒目横幅/标签云，居中大字展示 |
| **协作输入** | 综合市场数据与 Orion 观点提炼；示例：「小幅回调 · 权益拖累 · 韧性仍在」 |

---

### 模块 5：热门主题表现（Hot Themes）

| 维度 | 说明 |
|------|------|
| **内容** | 当周热门行业/主题 ETF 的涨跌幅排名，覆盖：中概互联、人工智能、游戏传媒、军工、证券、光伏、芯片半导体、医药医疗、白酒、黄金、科创50、煤炭等 |
| **数据字段** | 主题数组 `{theme_name, etf_name, etf_code, weekly_return}` |
| **展示形式** | 网格卡片或横向滚动条，每个主题一个卡片，显示主题名、ETF名、涨跌幅（绿涨红跌或红涨绿跌，须统一） |
| **协作输入** | `china-market-data` 或东方财富 ETF 行情数据 |

---

### 模块 6：基金经理观点（Fund Manager View — 季报摘录）

| 维度 | 说明 |
|------|------|
| **内容** | 摘录产品底层 FOF 基金经理在最新季报中的三部分：① 上季度/近期市场回顾；② 组合运作思路；③ 下季度展望。须注明基金经理姓名、数据来源（季报日期） |
| **数据字段** | `fm_name`, `fm_review`, `fm_strategy`, `fm_outlook`, `quarterly_report_date` |
| **展示形式** | 三段式卡片，每段配小标题（📊 市场回顾 / 🎯 运作思路 / 🔭 后市展望），底部注明「数据来源：XX基金XXXX年X季报 \| 基金经理：XXX」 |
| **协作输入** | Castor 提供基金季报文本；提取关键段落 |

---

### 模块 7：AI 智能解读（AI Insight）

| 维度 | 说明 |
|------|------|
| **内容** | 基于当周市场数据，生成三段客户化解读：① 市场概况（当周各大类资产表现综述）；② 对产品的影响（为什么组合会涨/跌，与产品设计逻辑的关系）；③ 给投资者的建议（持有/加仓/定投/观望） |
| **数据字段** | `ai_market_summary`, `ai_impact_on_fund`, `ai_investor_advice` |
| **展示形式** | 三栏卡片或折叠面板，标题分别为「市场概况」「对 FOF 的影响」「给投资者的建议」 |
| **协作输入** | 基于模块 3/5/10 的数据自动生成；语言须通俗，避免过度专业术语 |

---

### 模块 8：本周产品表现（Weekly Performance）

| 维度 | 说明 |
|------|------|
| **内容** | ① 五日逐日涨跌幅柱状图/卡片（周一至周五，含日期、涨跌幅、颜色区分涨跌）；② 成立以来净值走势折线图；③ 一段客户化解读文字 |
| **数据字段** | 五日数组 `{date, daily_return}`; 成立以来净值序列 `{date, nav}`; `weekly_commentary` |
| **展示形式** | 上方五日卡片（横向排列，每个卡片一个日期+涨跌幅）；中间净值走势折线图；下方解读文字 |
| **协作输入** | Vega 提供组合每日净值；`china-market-data` 提供交易日对齐 |
| **客户化要点** | 解读须以「亲爱的投资者朋友」开头，用第二人称；涨跌幅颜色统一（建议：国内习惯红涨绿跌，若面向海外客户则绿涨红跌，须在产品 SOP 中明确） |

---

### 模块 9：回撤修复数据（Drawdown Anchor）

| 维度 | 说明 |
|------|------|
| **内容** | 展示产品历史最大回撤修复时间、当前回撤状态、历史平均修复天数等心理锚定数据，帮助客户建立「波动是暂时的」认知 |
| **数据字段** | `max_drawdown_pct`, `max_drawdown_recovery_days`, `current_drawdown_pct`, `current_drawdown_days`, `avg_recovery_days`, `historical_incidents[]` |
| **展示形式** | 大数字卡片布局，例如：「43天 \| 历史最大回撤修复天数」「~10天 \| 其他几次小波动平均恢复」「0.75% \| 当前回撤 已持续X天」 |
| **协作输入** | Orion 提供历史绩效数据；提炼关键数字 |
| **客户化要点** | 配一句安抚性标语，如「投资最怕的不是跌，而是跌了不知道要跌多久」「耐心持有，产品也能较快修复」 |

---

### 模块 10：组合波动原因分析（Performance Attribution）

| 维度 | 说明 |
|------|------|
| **内容** | 按资产类别拆解当周组合波动来源：① 债券端（利率债/信用债/可转债表现，票息贡献）；② 权益端（A股/港股/美股，大盘/中小盘，成长/价值）；③ 商品与另类（黄金、REITs、CTA）；④ 小结（FOF 多资产配置理念的通俗解释） |
| **数据字段** | 各类资产周涨跌幅、对组合收益贡献度、主要驱动因素 |
| **展示形式** | 分节标题（如「1. 债券端：债市表现」「2. 权益端：A股表现」），每节 2-4 句话；最后「💡 小结」段落 |
| **协作输入** | Orion 提供 Brinson 归因；Helios/Terra 提供大类资产观点；Castor 提供底层基金异常提示 |
| **客户化要点** | 须用通俗语言，例如「这正体现了FOF『多资产、多策略』的设计理念——不押注单一资产，通过配置获取稳健回报」 |

---

### 模块 11：后市观点（Market Outlook）

| 维度 | 说明 |
|------|------|
| **内容** | 分三个子模块：① 债券市场观点（票息价值、收益率走势、流动性）；② 权益市场观点（估值、风格、行业）；③ 黄金/另类资产观点；④ 组合应对（是否触发再平衡阈值） |
| **数据字段** | `bond_outlook`, `equity_outlook`, `commodity_outlook`, `portfolio_action` |
| **展示形式** | 三级标题分节，每节 3-5 句话；组合应对单独一个小节 |
| **协作输入** | Helios（固收）/ Terra（权益）/ Mercury（宏观）提供周度观点；Orion 提供再平衡信号 |
| **合规要求** | 不得承诺收益；须用「值得关注」「可能」「建议」等谨慎措辞 |

---

### 模块 12：客户行动指南（Action Guide）

| 维度 | 说明 |
|------|------|
| **内容** | 根据客户不同持仓状态，给出差异化建议，以表格形式呈现 |
| **数据字段** | 状态-动作-理由 三列表格 |
| **展示形式** | 表格，四行（持仓未满建议期、持仓已满且盈利、持仓已满且浮亏、尚未持仓观望），列：您的状态 / 建议动作 / 理由 |
| **协作输入** | 根据产品特性与客户生命周期设计 |
| **客户化要点** | 动作须具体可操作，如「安心持有」「继续配置」「分批补仓」「启动小额定投」 |

---

### 模块 13：财经新闻与沟通策略（News & Communication Playbook）

| 维度 | 说明 |
|------|------|
| **内容** | 按市场/资产类别（A股、港股、美股、黄金等），每条新闻包含五个维度：① 市场动态（1-2 句话）；② 产生的影响（对组合的影响）；③ 历史上此类事件对市场的影响（概率/规律）；④ 影响哪些客户；⑤ 如何沟通（顾问话术，可直接复制） |
| **数据字段** | 每条新闻 `{market, headline, impact_on_portfolio, historical_pattern, affected_clients, advisor_script}` |
| **展示形式** | 每个市场一个折叠面板/卡片，面板标题带国旗/图标，展开后五个维度依次排列 |
| **协作输入** | `daily-market-hotspot` / `r9-opc-research-macro` 提供当周重要新闻；撰写沟通策略 |
| **特殊要求** | 每个市场的话术旁须配「📋 复制」按钮（HTML `navigator.clipboard` 实现），方便顾问一键复制 |

---

### 模块 14：理财经理沟通贴士（Advisor Toolkit）

| 维度 | 说明 |
|------|------|
| **内容** | 三个子模块：① 本周沟通重点（3 句话，每句话术旁配复制按钮）；② 不同客群话术模板（新客户<1个月、盈利老客户、浮亏客户-持仓短、浮亏客户-持仓长）；③ 常见客户异议回应（预设 3-5 个 Q&A） |
| **数据字段** | `key_messages[3]`, `client_segments[]`, `common_objections[]` |
| **展示形式** | ① 三行文本，每行前有数字标号，右侧「📋 复制」按钮；② 客群话术以引用块/卡片展示，标题为客群标签；③ Q&A 以折叠列表或问答对形式展示 |
| **协作输入** | `post-investment-companion` / `fund-market-volatility-script` 提供话术基座；Belle/Dylan 客户化润色 |
| **合规要求** | 所有话术须经 Sage 审核；不得出现「保本」「稳赚」等绝对化表述 |

---

### 模块 15：附录（Appendix）

| 维度 | 说明 |
|------|------|
| **内容** | ① 数据来源说明（天天基金网、东方财富、Wind、AKShare 等）；② 标准风险揭示语句；③ 往期报告链接/索引（如有）；④ 制作日期 |
| **数据字段** | `data_sources[]`, `risk_disclosure`, `report_date`, `production_date` |
| **展示形式** | 页面底部灰色小字区域，分条列出 |
| **协作输入** | Sage 提供合规话术模板 |

---

## 五、HTML 报告模板规范

当用户要求「输出网页报告」或「生成 HTML 报告」时，按以下技术规范执行。

### 5.1 页面结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OPC · {{产品名称}} 周度陪伴报告</title>
  <style> /* 内联样式，详见 templates/companion-report-template.html */ </style>
</head>
<body>
  <header>  <!-- 模块1：报告头 --> </header>
  <main>
    <section id="overview">       <!-- 模块2：产品概况 --></section>
    <section id="market">         <!-- 模块3：全球市场速览 --></section>
    <section id="keywords">       <!-- 模块4：本周关键词 --></section>
    <section id="themes">         <!-- 模块5：热门主题 --></section>
    <section id="fm-view">        <!-- 模块6：基金经理观点 --></section>
    <section id="ai-insight">     <!-- 模块7：AI智能解读 --></section>
    <section id="performance">    <!-- 模块8：本周产品表现 --></section>
    <section id="drawdown">       <!-- 模块9：回撤修复数据 --></section>
    <section id="attribution">    <!-- 模块10：波动原因分析 --></section>
    <section id="outlook">        <!-- 模块11：后市观点 --></section>
    <section id="action">         <!-- 模块12：客户行动指南 --></section>
    <section id="news">           <!-- 模块13：财经新闻与沟通策略 --></section>
    <section id="advisor">        <!-- 模块14：理财经理沟通贴士 --></section>
  </main>
  <footer>                        <!-- 模块15：附录 --></footer>
  <script> /* 复制按钮交互，详见模板 */ </script>
</body>
</html>
```

### 5.2 视觉风格

| 元素 | 规范 |
|------|------|
| **配色** | 主色：深蓝/品牌色（#1e3a5f 或 OPC 品牌色）；辅助色：浅灰背景（#f5f7fa）；涨：#e74c3c（红），跌：#27ae60（绿）—— 国内 A 股习惯；或按产品 SOP 统一 |
| **字体** | 中文：系统字体栈 `"PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif`；数字等宽：`"DIN Alternate", "Helvetica Neue", Arial` |
| **卡片** | 圆角 12px，白色背景，微弱阴影 `box-shadow: 0 2px 8px rgba(0,0,0,0.06)`，padding 16-24px |
| **间距** | 模块间 margin 32-48px；移动端缩小至 20-24px |
| **响应式** | 移动端：卡片全宽堆叠；表格横向滚动；五日卡片改为纵向排列 |

### 5.3 交互元素

| 元素 | 实现方式 |
|------|----------|
| **复制按钮** | 每个话术旁放「📋 复制」按钮，点击后调用 `navigator.clipboard.writeText()`，按钮文字临时变为「✅ 已复制」，2 秒后恢复 |
| **折叠面板** | 模块 13 的市场新闻卡片可使用 `<details>` 原生折叠或简单的 CSS/JS 手风琴；默认展开前 2 个市场，其余折叠 |
| **锚点导航** | 页面顶部或侧边可设置浮动导航栏，点击平滑滚动到对应模块（可选，长报告建议加） |
| **图表** | 净值走势折线图可用轻量级方案：① SVG 内联绘制；② ECharts/Chart.js CDN 引入（推荐，控制包大小）；③ 若环境受限，用 CSS 柱状图替代 |

### 5.4 输出格式

- **默认**：单个 `.html` 文件，CSS 和 JS 全部内联，确保离线可打开、可转发
- **扩展**：如需 PDF 导出，可在 HTML 中增加「🖨️ 打印/PDF」按钮，调用 `window.print()`，配合 `@media print` 样式优化分页
- **嵌入**：如需嵌入公众号/小程序，须确保所有资源内联，无外引 CDN（或仅引微信白名单 CDN）

> **模板文件**：`templates/companion-report-template.html` —— 可直接复制并填充数据使用。

---

## 五、实时数据获取与多源降级机制

### 5.1 数据源优先级与分工

采用**多源优先级 + 自动降级**机制，任一数据源失效时自动切换至备用源。浏览器端通过 JavaScript 异步请求实现，服务端通过 Python 脚本轮询实现。

| 优先级 | 数据源 | 用途 | 接入方式 | 浏览器端可用性 | 服务端可用性 |
|--------|--------|------|----------|--------------|--------------|
| **P1** | **Wind (万得)** | 主力数据源：ETF净值、板块资金流向、北向资金、融资余额 | Wind API (`WindPy`) | ❌ 跨域 | ✅ Python SDK |
| **P2** | **iFinD (同花顺)** | 行情、板块资金流向、龙虎榜 | iFinD API (`iFinDPy`) | ❌ 跨域 | ✅ Python SDK |
| **P3** | **Tushare Pro** | ETF日线/实时行情、资金流向、龙虎榜 | Tushare Pro API (`tushare`) | ❌ 跨域 | ✅ Python SDK |
| **P4** | **东方财富 Choice** | ETF实时净值、资金流向、融资融券、北向资金 | Choice API / 网页 | ⚠️ 需代理 | ✅ Python SDK |
| **P5** | **AKShare** | ETF实时行情、板块资金、北向资金、融资融券 | `akshare` | ⚠️ 部分可用 | ✅ Python SDK |
| **P6** | **Baostock** | 个股行情、指数成分股 | `baostock` | ❌ 跨域 | ✅ Python SDK |
| **P7** | **天天基金网 (Eastmoney Fund)** | **基金实时净值、估算净值、涨跌幅、规模** | **JSONP API (`fundgz.1234567.com.cn/js/{code}.js`)** | ✅ **JSONP 无跨域** | ✅ Python + `requests` |
| **P8** | **巨潮资讯网 (cninfo)** | 政策公告、监管文件、上市公司公告 | 网页抓取/官方API | ✅ 可直抓 | ✅ Python SDK |
| **P9** | **盈米 (Yingmi)** | 基金净值、组合诊断、资产配置 | MCP SSE `https://stargate.yingmi.com/mcp/sse?apiKey=...` | ❌ 需代理 | ✅ SSE 流式 |

### 5.2 浏览器端实时数据获取（前端 JS）

对于部署到互联网（pages.dev）的静态 HTML，**浏览器端**通过以下方式获取实时数据：

#### 基金净值（天天基金 JSONP — P7）

```javascript
// 天天基金实时净值 JSONP（无跨域限制，最可靠）
function fetchFundNav(fundCode) {
  return new Promise((resolve) => {
    const script = document.createElement('script');
    const callbackName = '_fundgz_' + Date.now();
    window[callbackName] = (data) => {
      resolve({
        fundCode: data.fundcode,
        name: data.name,
        nav: data.dwjz,           // 单位净值（最新公布）
        navDate: data.jzrq,       // 净值日期
        estimateNav: data.gsz,    // 估算净值（实时）
        estimateChange: data.gszzl, // 估算涨跌幅%
        estimateTime: data.gztime // 估算时间
      });
      delete window[callbackName];
      document.head.removeChild(script);
    };
    script.src = `https://fundgz.1234567.com.cn/js/${fundCode}.js?rt=${Date.now()}`;
    document.head.appendChild(script);
    setTimeout(() => { resolve(null); delete window[callbackName]; }, 5000);
  });
}
```

#### 指数行情（东方财富 API — P4/P7）

```javascript
// 东方财富开放 API（支持 CORS，可直接 fetch）
async function fetchIndexQuote(secid) {
  // secid 格式：1.000300(沪深300), 0.399006(创业板), 116.HSI(恒生)等
  const url = `https://push2.eastmoney.com/api/qt/stock/get?secid=${secid}&fields=f43,f44,f45,f46,f57,f58,f60,f170,f171`;
  const res = await fetch(url);
  const json = await res.json();
  const d = json.data;
  return {
    code: d.f57, name: d.f58,
    price: (d.f43 / 100).toFixed(2),      // 当前价（分→元）
    open: (d.f46 / 100).toFixed(2),
    high: (d.f44 / 100).toFixed(2),
    low: (d.f45 / 100).toFixed(2),
    prevClose: (d.f60 / 100).toFixed(2),
    changePct: (d.f171 / 100).toFixed(2) + '%'  // 涨跌%
  };
}
```

**常用 secid 映射**：
| 指数 | secid |
|------|-------|
| 沪深300 | `1.000300` 或 `0.399300` |
| 上证指数 | `1.000001` |
| 创业板指 | `0.399006` |
| 恒生指数 | `116.HSI`（可能不可用）→ 降级至 `hkHSI`（新浪）或手动输入 |
| 标普500 | 需通过 Yahoo Finance 或后端代理获取 |
| 黄金(COMEX) | 需通过 Yahoo Finance 或后端代理获取 |

#### 美股/黄金（Yahoo Finance — 降级方案）

```javascript
// 通过 CORS 代理或后端服务获取 Yahoo Finance 数据
// 推荐部署 Cloudflare Worker 做数据转发
async function fetchYahooQuote(symbol) {
  // symbol: ^GSPC(标普500), GC=F(COMEX黄金), ^HSI(恒生)
  const proxyUrl = 'https://your-worker.your-subdomain.workers.dev/quote?symbol=' + symbol;
  const res = await fetch(proxyUrl);
  return res.json();
}
```

### 5.3 自动刷新机制（每 5 分钟）

```javascript
// 页面加载后启动定时刷新
const REFRESH_INTERVAL = 5 * 60 * 1000; // 5分钟

async function refreshData() {
  const fundData = await fetchFundNav('025313');
  if (fundData) updateFundDOM(fundData);
  
  const indices = ['1.000300', '0.399006', '1.000001'];
  for (const secid of indices) {
    const quote = await fetchIndexQuote(secid);
    if (quote) updateIndexDOM(secid, quote);
  }
  
  document.getElementById('last-update').textContent = 
    '数据更新：' + new Date().toLocaleString('zh-CN');
}

// 首次加载 + 定时刷新
refreshData();
setInterval(refreshData, REFRESH_INTERVAL);
```

### 5.4 异常降级策略

```javascript
// 封装带降级的数据获取函数
async function fetchWithFallback(fetchers) {
  for (const fetcher of fetchers) {
    try {
      const data = await fetcher();
      if (data && data.price !== undefined) return data;
    } catch (e) { console.warn('Source failed:', e.message); }
  }
  return null; // 全部降级失败
}

// 使用示例：获取恒生指数
const hsi = await fetchWithFallback([
  () => fetchIndexQuote('116.HSI'),      // P4 东财
  () => fetchYahooQuote('^HSI'),         // P4 Yahoo（需代理）
  () => fetchFromCache('hsi')            // P9 本地缓存兜底
]);
```

---

## 六、数据输入与协作流程

```
Vega 提供：组合净值、持仓数据、申赎数据、底层基金净值
    ↓
Orion 提供：组合绩效归因、风险指标、再平衡信号、历史回撤数据
    ↓
Helios/Terra/Mercury 提供：大类资产/宏观/行业周度观点
    ↓
Castor 提供：底层基金评价、异常基金提示、基金经理季报摘录
    ↓
china-market-data / AKShare / 东方财富：A股/港股/美股/黄金/债券/ETF 行情
    ↓
Xueqi 整合 → 撰写周度陪伴报告（初稿，按 15 个模块填充）
    ↓
Sage 审核：合规性、风险提示、话术边界
    ↓
Belle/Dylan 客户化润色 → 输出终稿 HTML
    ↓
Mira 团队分发至客户（公众号/社群/1对1）
    ↓
r9-opc-memory 自动归档
```

### 6.1 各模块数据映射速查表

| 模块 | 主要数据来源 | 责任人 |
|------|-------------|--------|
| 模块 2 产品概况 | Vega（净值/持仓）+ 天天基金（底层基金净值） | Xueqi |
| 模块 3 全球市场 | `china-market-data` + Yahoo Finance + AKShare | Xueqi |
| 模块 4 关键词 | Xueqi 综合提炼 | Xueqi |
| 模块 5 热门主题 | `china-market-data` / 东方财富 ETF 数据 | Xueqi |
| 模块 6 基金经理观点 | Castor（季报文本） | Xueqi 摘录 |
| 模块 7 AI 解读 | Xueqi 基于模块 3/5/10 生成 | Xueqi |
| 模块 8 产品表现 | Vega（每日净值） | Xueqi |
| 模块 9 回撤数据 | Orion（历史绩效） | Xueqi 提炼 |
| 模块 10 波动归因 | Orion（Brinson）+ Castor（基金评价） | Xueqi |
| 模块 11 后市观点 | Helios/Terra/Mercury（投研观点） | Xueqi 转写 |
| 模块 12 行动指南 | Xueqi 根据产品特性设计 | Xueqi |
| 模块 13 新闻策略 | `daily-market-hotspot` / 宏观研究 | Xueqi |
| 模块 14 沟通贴士 | `post-investment-companion` + Belle/Dylan | Xueqi 整合 |
| 模块 15 附录 | Sage（合规话术） | Xueqi 组装 |

---

## 七、可调用的 Skill

| 用途 | Skill |
|------|-------|
| 市场数据获取 | `china-market-data` |
| 组合绩效归因 | `r9-opc-research-portfolio`（Orion） |
| 基金评价与诊断 | `fund-r9alpha-evaluation`、`fund-diagnosis-3.10` |
| 大类资产/行业观点 | `r9-opc-research-asset`、`r9-opc-research-sector` |
| 宏观解读 | `r9-opc-research-macro` |
| 客户陪伴话术 | `post-investment-companion`、`fund-market-volatility-script` |
| FOF 陪伴体系参考 | `cmb-fyf-companion-service` |
| 报告生成 | `client-report`、`xlsx-author`、`pptx-author` |
| 内容创作 | `khazix-writer`、`daily-market-hotspot` |

---

## 八、输出规范

| 维度 | 规范 |
|------|------|
| **文件命名** | `YYYYMMDD_周度陪伴报告_产品名称_v1.html`（网页版）; `YYYYMMDD_周度陪伴报告_产品名称_v1.pdf`（PDF 版，可选） |
| **归档路径** | `OPC/02_投顾服务/陪伴内容/` |
| **更新频率** | 每周五收盘后生成，周六上午完成合规审核，周六下午/周日上午触达客户 |
| **版本管理** | 如有重大市场事件，可发布 v2 补充版；同名文件自动加版本号 |
| **输出格式优先级** | ① 单页 HTML（默认） → ② PDF（打印导出） → ③ 长图（H5/公众号，按需） → ④ Word（客户要求时） |
| **多产品支持** | 支持同时输入多个产品代码，批量生成对应报告；每个产品独立一个 HTML 文件 |

---

---

## 九、部署规范（互联网可访问）

### 9.1 部署要求

报告必须部署到**互联网可访问的 CDN**，以满足客户通过微信、浏览器直接打开的需求。推荐以下平台：

| 平台 | 域名后缀 | 特点 | 适用场景 |
|------|----------|------|----------|
| **Cloudflare Pages** | `*.pages.dev` | 免费、全球 CDN、支持自定义域名、支持 Pages Functions | **首选**，与参考模板一致 |
| **Vercel** | `*.vercel.app` | 免费、全球 CDN、Serverless Functions | 备选，支持动态 API |
| **GitHub Pages** | `*.github.io` | 免费、静态托管、自定义域名 | 纯静态报告 |
| **Netlify** | `*.netlify.app` | 免费、Form/Edge Functions | 需要表单交互时 |
| **阿里云 OSS + CDN** | 自定义域名 | 国内访问速度快、需备案 | 面向国内客户 |
| **腾讯云 COS + CDN** | 自定义域名 | 国内访问速度快、需备案 | 面向国内客户 |

### 9.2 Cloudflare Pages 部署步骤（推荐）

1. **创建 GitHub 仓库**（如 `opc-companion-reports`）
2. **推送 HTML 文件**到仓库
3. **连接 Cloudflare Pages**：Dashboard → Pages → Create a project → 连接 GitHub 仓库
4. **构建设置**：Framework preset = `None`，Build command = `exit 0`，Build output directory = `/`
5. **自定义域名**（可选）：绑定 `report.opc-wealth.com` 等企业域名
6. **部署完成**：获得 `https://opc-companion-reports.pages.dev/YYYYMMDD_周度陪伴报告_产品名称.html`

### 9.3 实时数据代理（跨域处理）

对于浏览器端无法直接访问的数据源（Yahoo Finance、盈米 SSE），通过 **Cloudflare Pages Functions**（`_worker.js`）做服务端代理：

```javascript
// _worker.js — Cloudflare Pages Function
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/api/yahoo') {
      const symbol = url.searchParams.get('symbol');
      const yahoo = await fetch(`https://query1.finance.yahoo.com/v8/finance/chart/${symbol}`);
      return new Response(yahoo.body, { headers: { 'Access-Control-Allow-Origin': '*' } });
    }
    return env.ASSETS.fetch(request); // 静态文件回退
  }
};
```

### 9.4 自动化部署（GitHub Actions）

```yaml
# .github/workflows/deploy.yml
name: Deploy Companion Report
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 18 * * 5'  # 每周五 18:00 UTC 自动部署
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate Report
        run: python scripts/generate_report.py --product 025313
      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: opc-companion-reports
          directory: ./dist
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
```

### 9.5 访问安全与合规

- **HTTPS 强制**：所有部署平台默认开启 HTTPS
- **SEO 控制**：在 `<head>` 中加入 `<meta name="robots" content="noindex, nofollow">`
- **数据缓存**：静态 HTML 缓存 5 分钟，实时数据通过 JS 单独刷新

## 十、合规要求

- 必须包含标准风险揭示：「过往业绩不代表未来表现，投资有风险，入市需谨慎」
- 不得承诺保本保收益
- 不得使用「肯定」「必然」「稳赚」等绝对化表述
- 涉及具体产品的，须注明产品风险等级与客户适当性匹配要求
- 所有话术须经 Sage 审核后方可对外发布
- 网页报告中须在页脚显著位置展示风险提示与免责声明
- 基金经理观点须注明来源（季报日期），不得断章取义或过度解读
- 数据须注明来源（天天基金、东方财富、Wind 等），不得使用未经验证的第三方数据

---

## 十一、模板与参考文件

| 文件 | 路径 | 说明 |
|------|------|------|
| HTML 报告模板 | `templates/companion-report-template.html` | 可直接复制填充的完整单页 HTML 模板 |
| 沟通话术参考 | `references/advisor-scripts.md` | 各客群标准话术与异议回应模板 |
| 数据映射表 | `references/data-mapping.md` | 15 模块与数据来源的详细映射 |
| 合规话术库 | `references/compliance-disclaimer.md` | Sage 审核通过的标准风险揭示与免责声明 |

---

*产品组合周度陪伴报告 | 维护者：Xueqi（产品中心）*
*"每周一份陪伴，让客户在市场波动中始终感到有人在身边。"*
