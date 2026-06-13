---
name: fund-r9alpha-evaluation
description: R9Alpha研基标准基金评价报告生成工具。当用户需要"按照R9alpha标准分析基金"、"生成基金评价底稿"、"基金评价报告"、"分析某只基金值不值得买"、"写基金研究报告"、"填充基金评价Excel"时触发。支持读取本地持仓CSV、JSON、Excel数据，自动从天天基金网在线爬取补全缺失指标，并生成Markdown深度分析报告。如有Wind终端可进一步提取量化指标补全。
---

# R9Alpha 研基基金评价报告生成

## 工作流程

### Step 1: 确认输入信息
向用户确认（如未明确提供）：
- **基金代码**（如 519702）
- **R9alpha 评价底稿模板 Excel 路径**（用户本地的 `.xlsx` 文件）
- **工作目录**（存放基金持仓 CSV、JSON、风险收益 Excel 等数据的目录，默认当前目录）

### Step 2: 搜索本地数据源
在工作目录下自动搜索与基金代码相关的文件：
- 持仓 CSV：`{fundcode}_*Q_holdings.csv`
- 完整数据 JSON：`fund_{fundcode}_complete_data.json`
- 风险收益 Excel：`*最新风险收益指标*({fundcode}*).xlsx`
- 投资备忘录 Markdown：`*{fundcode}*_投资研究备忘录.md`
- 基金诊断报告 HTML：`*基金诊断报告*_{fundcode}*.html`

### Step 3: 从天天基金网在线爬取补全数据（V2 新增）
如果本地数据不全或用户要求在线补全，自动从 **天天基金网 (fund.eastmoney.com)** 爬取以下数据：

| 数据类型 | 接口/页面 | 补全指标 |
|---------|----------|---------|
| 基本信息 | `fundgz.1234567.com.cn/js/{code}.js` | 基金名称、最新净值、日涨跌 |
| F10 基础概况 | `fund.eastmoney.com/f10/jbgk_{code}.html` | 基金类型、成立日期、规模、经理、基准 |
| 基金经理 | `fundf10.eastmoney.com/jjjl_{code}.html` | 经理姓名、上任日期、任职回报 |
| 业绩表现 | `fund.eastmoney.com/f10/jdzf_{code}.html` | 各周期收益与排名（1周/1月/3月/6月/1年/3年/5年/成立来）|
| 历史净值 | `api.fund.eastmoney.com/f10/lsjz` | 3年日净值（用于计算风险指标）|
| 十大重仓 | `fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc` | 最新重仓股及占比 |
| 行业配置 | `fundf10.eastmoney.com/FundArchivesDatas.aspx?type=hytz` | 行业分布及变动 |
| 资产配置 | `fundf10.eastmoney.com/FundArchivesDatas.aspx?type=zcpz` | 股票/债券/现金占比 |
| 持有人结构 | `fundf10.eastmoney.com/cyrjg_{code}.html` | 机构/个人/内部占比 |

**在线计算的风险指标**：
- 年化收益率、年化波动率
- 最大回撤
- 夏普比率（Rf=2.5%）
- 卡玛比率
- **索提诺比率**（新增）
- **下行标准差**（新增）
- **回撤恢复天数**（新增）
- **月度胜率**（新增）
- **上涨月平均收益 / 下跌月平均亏损**（新增）

### Step 4: 提取并整理数据
按 [references/r9alpha-framework.md](references/r9alpha-framework.md) 的指标体系，将本地数据 + 在线数据分类整理到以下维度：
1. 基础信息（基金经理、规模、成立时间、风格指标、持有人结构）
2. 收益指标（今年以来、去年、2018年、年化、近三年）
3. 风险指标（最大回撤、标准差、下行风险）
4. 性价比指标（夏普、卡玛、索提诺）
5. 超额指标（超额收益、Brinson定性归因、跟踪误差、信息比率）
6. 持有人体验（回撤恢复天数、胜率、赔率）
7. 价值观/道德（发行时点、限额保护投资者情况）
8. 基金公司（研究团队、考核机制）
9. 市场分析（季报观点一句话）
10. 市场展望（季报展望一句话 + 与上期变化）
11. R9Alpha 综合评价（1-5星评分 + 投资建议）

### Step 5: 生成 Excel 评价底稿
在用户提供（或指定的）R9alpha 模板 Excel 的右侧新增一列 `"{基金代码} 数据/分析"`，逐行填充对应指标的数据分析。无法获取的字段标记为 "待补充（Wind/Choice）"。

### Step 6: 生成 Markdown 深度报告
基于整理的数据生成一份结构化的 Markdown 报告，包含：
- 执行摘要
- 十大模块分析（对应 R9alpha 框架）
- 持仓变化追踪表
- SWOT 分析
- R9Alpha 评分汇总表
- 投资建议与风险提示

### Step 7: 尝试补全缺失指标（可选）
如果用户有 Wind 终端且同意，执行脚本 `scripts/generate-fund-evaluation.py` 的 Wind 扩展逻辑（或参考项目中的 Wind 提取脚本）来补全以下量化指标：
- 下行标准差、索提诺比率
- 信息比率 IR、跟踪误差
- 全部持仓加权市盈率 PE_TTM
- 机构持仓占比
- 基金份额变化率
- 月频胜率/赔率（上涨月平均收益、下跌月平均亏损）

## 输出文件

执行完成后向用户报告生成的文件路径：
- **Excel 评价底稿**：`{输出目录}/基金评价底稿_{基金代码}_R9Alpha.xlsx`
- **Markdown 深度报告**：`{输出目录}/基金评价报告_{基金代码}_R9Alpha.md`

## 自动化脚本

当需要批量生成或重复执行时，可直接调用：

```bash
# 基础模式（仅本地数据）
python scripts/generate-fund-evaluation.py <基金代码> --template <模板路径> --output-dir <输出目录> --work-dir <数据目录>

# 在线补全模式（推荐）
python scripts/generate-fund-evaluation.py <基金代码> --template <模板路径> --fetch-online
```

参数说明：
- `fund_code`: 基金代码，如 519702
- `--template`: R9alpha 评价底稿模板 Excel 路径
- `--output-dir`: 输出目录（默认当前目录）
- `--work-dir`: 工作目录，搜索本地数据（默认当前目录）
- `--fetch-online`: **强制从天天基金网在线爬取数据补全缺失指标**

## 数据来源优先级

1. **本地持仓 CSV**：`{fundcode}_{YYYY}Q{Q}_holdings.csv`
2. **本地 JSON 数据**：`fund_{fundcode}_complete_data.json`
3. **本地风险收益 Excel**：`最新风险收益指标-({fundcode}.OF).xlsx`
4. **本地投资备忘录 Markdown**：`{基金名}_{fundcode}_投资研究备忘录.md`
5. **天天基金网在线爬取**：`fund.eastmoney.com` / `fundf10.eastmoney.com`（自动补全本地缺失数据）
6. **Wind API**：通过 `WindPy` 提取净值、风险指标、持有人结构、市盈率等
7. **网络公开资料**：季报访谈、基金经理观点、中国基金报、证券时报等

## 评价标准参考

读取 `references/r9alpha-framework.md` 了解完整的指标体系定义、数据来源优先级和评分标准。
