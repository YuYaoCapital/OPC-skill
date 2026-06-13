#!/usr/bin/env python3
"""
基金投顾分析工具
提供组合分析、风险评估、基金筛选等功能
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


def calculate_annual_return(nav_series: pd.Series) -> float:
    """计算年化收益率"""
    total_return = (nav_series.iloc[-1] / nav_series.iloc[0]) - 1
    days = (nav_series.index[-1] - nav_series.index[0]).days
    years = days / 365
    return (1 + total_return) ** (1/years) - 1 if years > 0 else 0


def calculate_volatility(nav_series: pd.Series) -> float:
    """计算年化波动率"""
    daily_returns = nav_series.pct_change().dropna()
    return daily_returns.std() * np.sqrt(252)


def calculate_max_drawdown(nav_series: pd.Series) -> float:
    """计算最大回撤"""
    cummax = nav_series.cummax()
    drawdown = (nav_series - cummax) / cummax
    return drawdown.min()


def calculate_sharpe_ratio(nav_series: pd.Series, risk_free_rate: float = 0.03) -> float:
    """计算夏普比率"""
    annual_return = calculate_annual_return(nav_series)
    volatility = calculate_volatility(nav_series)
    if volatility == 0:
        return 0
    return (annual_return - risk_free_rate) / volatility


def calculate_calmar_ratio(nav_series: pd.Series) -> float:
    """计算卡玛比率"""
    annual_return = calculate_annual_return(nav_series)
    max_dd = abs(calculate_max_drawdown(nav_series))
    if max_dd == 0:
        return 0
    return annual_return / max_dd


def calculate_var(nav_series: pd.Series, confidence: float = 0.95) -> float:
    """计算VaR(风险价值)"""
    daily_returns = nav_series.pct_change().dropna()
    return np.percentile(daily_returns, (1 - confidence) * 100)


def portfolio_analysis(
    fund_navs: Dict[str, pd.Series],
    weights: Dict[str, float],
    risk_free_rate: float = 0.03
) -> Dict:
    """
    组合综合分析
    
    Args:
        fund_navs: 基金净值序列字典 {基金名称: 净值序列}
        weights: 基金权重字典 {基金名称: 权重}
        risk_free_rate: 无风险利率
    
    Returns:
        组合分析结果字典
    """
    # 对齐日期
    common_dates = None
    for nav in fund_navs.values():
        if common_dates is None:
            common_dates = set(nav.index)
        else:
            common_dates = common_dates.intersection(set(nav.index))
    common_dates = sorted(list(common_dates))
    
    if len(common_dates) < 30:
        raise ValueError("数据不足，至少需要30个共同交易日")
    
    # 计算组合净值
    portfolio_nav = pd.Series(0.0, index=common_dates)
    fund_metrics = {}
    
    for fund_name, nav in fund_navs.items():
        aligned_nav = nav[common_dates]
        weight = weights.get(fund_name, 0)
        portfolio_nav += aligned_nav / aligned_nav.iloc[0] * weight
        
        # 单个基金指标
        fund_metrics[fund_name] = {
            'weight': weight,
            'annual_return': calculate_annual_return(aligned_nav),
            'volatility': calculate_volatility(aligned_nav),
            'max_drawdown': calculate_max_drawdown(aligned_nav),
            'sharpe_ratio': calculate_sharpe_ratio(aligned_nav, risk_free_rate),
            'calmar_ratio': calculate_calmar_ratio(aligned_nav),
        }
    
    # 组合整体指标
    portfolio_metrics = {
        'annual_return': calculate_annual_return(portfolio_nav),
        'volatility': calculate_volatility(portfolio_nav),
        'max_drawdown': calculate_max_drawdown(portfolio_nav),
        'sharpe_ratio': calculate_sharpe_ratio(portfolio_nav, risk_free_rate),
        'calmar_ratio': calculate_calmar_ratio(portfolio_nav),
        'var_95': calculate_var(portfolio_nav),
    }
    
    # 相关性矩阵
    returns_df = pd.DataFrame({
        name: nav[common_dates].pct_change().dropna()
        for name, nav in fund_navs.items()
    })
    correlation_matrix = returns_df.corr()
    
    return {
        'portfolio': portfolio_metrics,
        'funds': fund_metrics,
        'correlation': correlation_matrix.to_dict(),
        'portfolio_nav': portfolio_nav.to_dict()
    }


def calculate_rebalance_signal(
    current_weights: Dict[str, float],
    target_weights: Dict[str, float],
    threshold: float = 0.05
) -> List[Dict]:
    """
    计算再平衡信号
    
    Args:
        current_weights: 当前权重
        target_weights: 目标权重
        threshold: 触发再平衡的偏离阈值
    
    Returns:
        需要调整的基金列表
    """
    signals = []
    all_funds = set(current_weights.keys()) | set(target_weights.keys())
    
    for fund in all_funds:
        current = current_weights.get(fund, 0)
        target = target_weights.get(fund, 0)
        deviation = abs(current - target)
        
        if deviation > threshold:
            signals.append({
                'fund': fund,
                'current_weight': current,
                'target_weight': target,
                'deviation': current - target,
                'action': 'buy' if current < target else 'sell',
                'adjust_amount': abs(target - current)
            })
    
    # 按调整幅度排序
    signals.sort(key=lambda x: x['adjust_amount'], reverse=True)
    return signals


def risk_assessment(portfolio_value: float, volatility: float, max_drawdown: float) -> Dict:
    """
    风险评估
    
    Args:
        portfolio_value: 组合市值
        volatility: 年化波动率
        max_drawdown: 最大回撤
    
    Returns:
        风险评估结果
    """
    # 计算95%置信度下的月度最大损失
    monthly_vol = volatility / np.sqrt(12)
    monthly_var = portfolio_value * monthly_vol * 1.645  # 95%置信度
    
    # 最大回撤金额
    max_loss_amount = portfolio_value * abs(max_drawdown)
    
    # 风险等级
    if max_drawdown > -0.30:
        risk_level = "高风险"
    elif max_drawdown > -0.20:
        risk_level = "中高风险"
    elif max_drawdown > -0.10:
        risk_level = "中等风险"
    else:
        risk_level = "中低风险"
    
    return {
        'monthly_var_95': monthly_var,
        'max_drawdown_amount': max_loss_amount,
        'risk_level': risk_level,
        'stress_test_loss': portfolio_value * 0.20  # 假设极端情况20%下跌
    }


def generate_asset_allocation(risk_profile: str) -> Dict[str, float]:
    """
    根据风险等级生成资产配置建议
    
    Args:
        risk_profile: 风险等级 (conservative/moderate/balanced/growth/aggressive)
    
    Returns:
        资产配置比例
    """
    allocations = {
        'conservative': {  # 保守型
            'money_market': 0.30,
            'short_bond': 0.25,
            'long_bond': 0.30,
            'balanced': 0.10,
            'equity': 0.05
        },
        'moderate': {  # 稳健型
            'money_market': 0.15,
            'short_bond': 0.20,
            'long_bond': 0.25,
            'balanced': 0.20,
            'equity': 0.20
        },
        'balanced': {  # 平衡型
            'money_market': 0.05,
            'short_bond': 0.10,
            'long_bond': 0.20,
            'balanced': 0.25,
            'equity': 0.40
        },
        'growth': {  # 成长型
            'money_market': 0.00,
            'short_bond': 0.05,
            'long_bond': 0.10,
            'balanced': 0.25,
            'equity': 0.60
        },
        'aggressive': {  # 进取型
            'money_market': 0.00,
            'short_bond': 0.00,
            'long_bond': 0.05,
            'balanced': 0.20,
            'equity': 0.75
        }
    }
    
    return allocations.get(risk_profile, allocations['balanced'])


def format_report(analysis_result: Dict) -> str:
    """格式化分析报告"""
    lines = []
    lines.append("=" * 50)
    lines.append("组合分析报告")
    lines.append("=" * 50)
    
    # 组合整体
    portfolio = analysis_result['portfolio']
    lines.append("\n【组合整体指标】")
    lines.append(f"年化收益率: {portfolio['annual_return']*100:.2f}%")
    lines.append(f"年化波动率: {portfolio['volatility']*100:.2f}%")
    lines.append(f"最大回撤: {portfolio['max_drawdown']*100:.2f}%")
    lines.append(f"夏普比率: {portfolio['sharpe_ratio']:.2f}")
    lines.append(f"卡玛比率: {portfolio['calmar_ratio']:.2f}")
    
    # 单基金表现
    lines.append("\n【基金明细】")
    for fund, metrics in analysis_result['funds'].items():
        lines.append(f"\n{fund} (权重: {metrics['weight']*100:.1f}%)")
        lines.append(f"  年化收益: {metrics['annual_return']*100:.2f}%")
        lines.append(f"  波动率: {metrics['volatility']*100:.2f}%")
        lines.append(f"  最大回撤: {metrics['max_drawdown']*100:.2f}%")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # 示例用法
    print("基金投顾分析工具")
    print("导入方法: from fund_analysis import *")
    print("\n主要函数:")
    print("- portfolio_analysis(): 组合综合分析")
    print("- calculate_rebalance_signal(): 再平衡信号")
    print("- risk_assessment(): 风险评估")
    print("- generate_asset_allocation(): 生成资产配置")