# 且慢(盈米)API接入指南

## 概述

且慢(盈米)提供两种接入方式：
1. **MCP SSE** (推荐): Server-Sent Events实时通信，适合AI Agent
2. **OpenAPI**: 标准REST API，适合传统应用

## MCP SSE接入

### 端点信息

- **SSE端点**: `https://stargate.yingmi.com/mcp/sse?apiKey=YOUR_API_KEY`
- **协议**: MCP (Model Context Protocol)
- **通信方式**: Server-Sent Events + HTTP POST

### 连接流程

```
1. 客户端 → GET /mcp/sse?apiKey=xxx
2. 服务端 ← 返回 SSE stream
3. 服务端 ← event: endpoint (发送message端点URL)
4. 服务端 ← event: message (发送可用tools列表)
5. 客户端 → POST message端点 (调用tools)
6. 服务端 ← 返回tool执行结果
```

### 工具列表

#### get_fund_info - 基金信息查询
```json
{
  "code": "000001"
}
```
返回：基金名称、类型、成立日期、管理公司、费率等

#### get_fund_nav - 净值数据
```json
{
  "code": "000001",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "limit": 252
}
```
返回：日期、单位净值、累计净值、日涨跌幅

#### search_funds - 基金搜索
```json
{
  "keyword": "沪深300",
  "fund_type": "index",
  "limit": 20
}
```
fund_type可选: stock/bond/mixed/qdii/index/money

#### analyze_portfolio - 组合分析
```json
{
  "holdings": [
    {"code": "000001", "weight": 0.3},
    {"code": "110020", "weight": 0.4},
    {"code": "260108", "weight": 0.3}
  ]
}
```
返回：组合收益率、波动率、夏普比率、最大回撤、相关性矩阵

#### get_strategy_recommendation - 策略推荐
```json
{
  "risk_profile": "balanced",
  "amount": 100000,
  "horizon": "long"
}
```
risk_profile: conservative/moderate/balanced/growth/aggressive
horizon: short/medium/long

#### get_investment_plan - 定投计划
```json
{
  "fund_codes": ["110020", "000001"],
  "amount": 2000,
  "frequency": "monthly"
}
```
frequency: weekly/monthly

#### get_market_overview - 市场概览
```json
{}
```
返回：主要指数行情、涨跌幅、成交额

#### get_fund_performance - 业绩指标
```json
{
  "code": "000001",
  "period": "1y"
}
```
period: 1m/3m/6m/1y/3y/5y/all

## OpenAPI接入

### 基础信息

- **Base URL**: `https://api.qieman.com` (示例，需确认实际地址)
- **认证**: API Key + Secret
- **格式**: JSON

### 认证方式

```python
headers = {
    "Authorization": "Bearer {API_KEY}",
    "X-API-Secret": "{API_SECRET}"
}
```

### 主要端点

| 端点 | 方法 | 说明 |
|------|------|------|
| /v1/fund/info | GET | 基金信息 |
| /v1/fund/nav | GET | 净值数据 |
| /v1/fund/search | GET | 基金搜索 |
| /v1/fund/performance | GET | 业绩指标 |
| /v1/fund/holding | GET | 持仓数据 |
| /v1/portfolio/analyze | POST | 组合分析 |
| /v1/portfolio/risk | POST | 风险计算 |
| /v1/portfolio/rebalance | POST | 再平衡建议 |
| /v1/strategy/recommend | POST | 策略推荐 |
| /v1/plan/investment | POST | 定投计划 |
| /v1/market/overview | GET | 市场概览 |
| /v1/market/sector | GET | 行业表现 |
| /v1/market/macro | GET | 宏观指标 |

## 使用建议

### 数据缓存

建议对以下数据做本地缓存：
- 基金基本信息 (缓存7天)
- 历史净值数据 (缓存1天)
- 市场概览 (缓存1小时)

### 调用限制

注意API调用频率限制：
- 实时行情: 60次/分钟
- 历史数据: 1000次/小时
- 组合分析: 100次/小时

### 错误处理

常见错误码：
- `400`: 参数错误
- `401`: 认证失败
- `429`: 请求过于频繁
- `500`: 服务器内部错误

## 示例代码

参见：
- `scripts/qieman_mcp_client.py` - MCP客户端
- `scripts/qieman_api.py` - OpenAPI客户端
- `scripts/example_qieman_integration.py` - 综合示例

## 支持

- 且慢官网: https://www.qieman.com
- 盈米官网: https://www.yingmi.cn
- 开发者文档: https://stargate.yingmi.com/docs