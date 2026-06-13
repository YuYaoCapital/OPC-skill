# 固收+基金评价指标计算方法

## 收益指标

### 1. 区间收益率

$$R = \frac{NV_t - NV_0}{NV_0} \times 100\%$$

其中 $NV_t$ 为期末净值，$NV_0$ 为期初净值

### 2. 年化收益率（几何平均）

$$R_{annual} = (1 + R)^{\frac{252}{n}} - 1$$

其中 $n$ 为交易日数量，252为年化交易日

### 3. 超额收益

$$\alpha = R_{fund} - R_{benchmark}$$

### 4. 夏普比率

$$Sharpe = \frac{R_p - R_f}{\sigma_p}$$

其中 $R_p$ 为组合收益，$R_f$ 为无风险利率，$\sigma_p$ 为组合收益标准差

### 5. Calmar比率

$$Calmar = \frac{R_{annual}}{|MDD|}$$

其中 $MDD$ 为最大回撤

---

## 风险指标（重点）

### 1. 最大回撤（Maximum Drawdown）

$$MDD = \max_{t \in [0,T]} \left( \frac{P_{peak} - P_t}{P_{peak}} \right)$$

其中 $P_{peak}$ 为区间内的最高净值

### 2. ⭐最大回撤恢复天数（核心指标）

**定义**：从最大回撤最低点恢复到前高的交易日天数

**计算步骤**：

```python
def calculate_recovery_days(nav_series):
    """
    计算每次最大回撤的恢复天数
    """
    peaks = nav_series.cummax()
    drawdowns = (nav_series - peaks) / peaks
    
    recovery_periods = []
    in_drawdown = False
    drawdown_start = None
    lowest_point = None
    lowest_date = None
    
    for date, nav in nav_series.items():
        current_peak = peaks[date]
        dd = (nav - current_peak) / current_peak
        
        if dd < -0.005 and not in_drawdown:  # 回撤超过0.5%视为开始
            in_drawdown = True
            drawdown_start = date
            lowest_point = nav
            lowest_date = date
        
        elif in_drawdown:
            if nav < lowest_point:
                lowest_point = nav
                lowest_date = date
            
            if nav >= current_peak * 0.995:  # 恢复到前高的99.5%
                recovery_days = (date - lowest_date).days
                recovery_periods.append({
                    'start': drawdown_start,
                    'lowest': lowest_date,
                    'end': date,
                    'max_dd': (lowest_point - nav_series[:date].max()) / nav_series[:date].max(),
                    'recovery_days': recovery_days
                })
                in_drawdown = False
    
    return recovery_periods
```

**输出示例**：

| 回撤开始 | 最低日期 | 回撤幅度 | 恢复日期 | 恢复天数 |
|----------|----------|----------|----------|----------|
| 2022-01-04 | 2022-04-26 | -5.23% | 2022-07-15 | 54 |
| 2023-05-09 | 2023-06-01 | -2.15% | 2023-06-28 | 19 |

### 3. 波动率（年化标准差）

$$\sigma = \sqrt{252} \times \sqrt{\frac{1}{n-1} \sum_{i=1}^{n}(R_i - \bar{R})^2}$$

### 4. 下行标准差

只计算负收益的波动：

$$\sigma_{down} = \sqrt{252} \times \sqrt{\frac{1}{n-1} \sum_{R_i < 0}(R_i - \bar{R})^2}$$

### 5. 索提诺比率

$$Sortino = \frac{R_p - R_f}{\sigma_{down}}$$

### 6. VaR (Value at Risk)

历史模拟法：

$$VaR_{95\%} = \text{收益率序列的第5百分位数}$$

---

## 收益归因指标

### Brinson归因模型

**资产配置效应**：

$$AA = \sum_{i}(w_{p,i} - w_{b,i}) \times R_{b,i}$$

**个股选择效应**：

$$SS = \sum_{i}w_{b,i} \times (R_{p,i} - R_{b,i})$$

**交互效应**：

$$INT = \sum_{i}(w_{p,i} - w_{b,i}) \times (R_{p,i} - R_{b,i})$$

其中 $w$ 为权重，$R$ 为收益，$p$ 为组合，$b$ 为基准，$i$ 为资产类别

### 固收+专项归因

**债券部分**：
- 利息收入贡献 = 债券票息 / 组合平均资产
- 资本利得贡献 = (债券卖出价 - 买入价) / 组合平均资产
- 久期效应 = 久期 × 利率变动

**权益部分**：
- 股票收益贡献 = 股票仓位 × 股票组合收益
- 可转债收益贡献 = 可转债仓位 × 可转债组合收益
- 打新收益贡献 = 打新收益 / 组合平均资产

---

## 调仓有效性指标

### 1. 调仓胜率

$$WinRate = \frac{\text{调仓后表现优于未调仓的次数}}{\text{总调仓次数}} \times 100\%$$

### 2. 新增个股胜率

追踪新增重仓股后续30/60/90日收益，计算正收益比例

### 3. 剔除个股胜率

追踪剔除个股后续30/60/90日收益，计算避免损失的比例

### 4. 调仓贡献度

$$Contribution = \sum_{i} \Delta w_i \times (R_{i,actual} - R_{i,if\_not\_changed})$$
