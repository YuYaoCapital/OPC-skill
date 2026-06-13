#!/usr/bin/env python3
"""
且慢API与本地分析工具结合使用示例
展示如何获取真实基金数据并进行投顾分析
"""

import os
import sys
from datetime import datetime, timedelta

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qieman_api import QiemanAPIClient, batch_fetch_funds, create_client_from_env
from fund_analysis import (
    portfolio_analysis, 
    calculate_rebalance_signal,
    risk_assessment,
    generate_asset_allocation,
    format_report
)


def example_1_basic_fund_query():
    """示例1: 基础基金数据查询"""
    print("=" * 60)
    print("示例1: 基础基金数据查询")
    print("=" * 60)
    
    try:
        client = create_client_from_env()
    except ValueError as e:
        print(f"错误: {e}")
        print("提示: 请先设置 QIEMAN_API_KEY 和 QIEMAN_API_SECRET 环境变量")
        return
    
    # 搜索基金
    print("\n搜索'沪深300'相关基金...")
    funds = client.search_funds("沪深300", fund_type="index", limit=5)
    for fund in funds:
        print(f"  {fund.get('code')}: {fund.get('name')} ({fund.get('type')})")
    
    # 获取单只基金信息
    fund_code = "000001"  # 华夏成长混合
    print(f"\n获取基金 {fund_code} 信息...")
    info = client.get_fund_info(fund_code)
    print(f"  基金名称: {info.get('data', {}).get('name', 'N/A')}")
    print(f"  基金类型: {info.get('data', {}).get('type', 'N/A')}")
    print(f"  成立日期: {info.get('data', {}).get('establish_date', 'N/A')}")
    
    # 获取净值数据
    print(f"\n获取基金 {fund_code} 近90天净值...")
    nav_df = client.get_fund_nav(fund_code, limit=90)
    if not nav_df.empty:
        print(f"  最新净值: {nav_df['nav'].iloc[-1]}")
        print(f"  90天前净值: {nav_df['nav'].iloc[0]}")
        print(f"  期间涨跌幅: {(nav_df['nav'].iloc[-1]/nav_df['nav'].iloc[0]-1)*100:.2f}%")


def example_2_portfolio_analysis():
    """示例2: 组合分析"""
    print("\n" + "=" * 60)
    print("示例2: 投资组合分析")
    print("=" * 60)
    
    try:
        client = create_client_from_env()
    except ValueError as e:
        print(f"错误: {e}")
        return
    
    # 定义组合持仓
    holdings = [
        {"code": "000001", "weight": 0.20},  # 华夏成长
        {"code": "110020", "weight": 0.30},  # 易方达沪深300
        {"code": "260108", "weight": 0.25},  # 景顺长城新兴成长
        {"code": "000171", "weight": 0.25},  # 易方达裕丰回报(债基)
    ]
    
    print("\n组合配置:")
    for h in holdings:
        print(f"  {h['code']}: {h['weight']*100:.0f}%")
    
    # 批量获取净值数据
    print("\n获取净值数据...")
    fund_codes = [h["code"] for h in holdings]
    fund_navs = batch_fetch_funds(client, fund_codes)
    
    if len(fund_navs) < len(holdings):
        print("警告: 部分基金数据获取失败")
        return
    
    # 构建权重字典
    weights = {h["code"]: h["weight"] for h in holdings}
    
    # 进行组合分析
    print("\n进行组合分析...")
    result = portfolio_analysis(fund_navs, weights)
    
    # 输出结果
    print(format_report(result))
    
    # 风险评估
    portfolio_value = 100000  # 假设组合市值10万元
    portfolio = result['portfolio']
    risk = risk_assessment(
        portfolio_value, 
        portfolio['volatility'], 
        portfolio['max_drawdown']
    )
    
    print("\n【风险评估】")
    print(f"  风险等级: {risk['risk_level']}")
    print(f"  月度VaR(95%): -{risk['monthly_var_95']:.0f}元")
    print(f"  历史最大回撤金额: -{risk['max_drawdown_amount']:.0f}元")


def example_3_strategy_recommendation():
    """示例3: 策略推荐与定投计划"""
    print("\n" + "=" * 60)
    print("示例3: 策略推荐与定投计划")
    print("=" * 60)
    
    try:
        client = create_client_from_env()
    except ValueError as e:
        print(f"错误: {e}")
        return
    
    # 获取策略推荐
    risk_profile = "balanced"  # 平衡型
    amount = 100000  # 10万元
    
    print(f"\n风险偏好: {risk_profile}")
    print(f"投资金额: {amount}元")
    
    # 本地生成资产配置
    allocation = generate_asset_allocation(risk_profile)
    print("\n建议资产配置:")
    for asset, weight in allocation.items():
        print(f"  {asset}: {weight*100:.0f}%")
    
    # 从且慢获取策略推荐(如API支持)
    try:
        strategy = client.get_strategy_recommendation(risk_profile, amount, horizon="long")
        if "error" not in strategy:
            print("\n且慢策略推荐:")
            print(f"  策略名称: {strategy.get('data', {}).get('name', 'N/A')}")
            print(f"  预期收益: {strategy.get('data', {}).get('expected_return', 'N/A')}")
            print(f"  风险等级: {strategy.get('data', {}).get('risk_level', 'N/A')}")
    except Exception as e:
        print(f"\n获取策略推荐失败: {e}")
    
    # 生成定投计划
    print("\n定投计划示例:")
    fund_codes = ["110020", "000001"]  # 沪深300 + 华夏成长
    monthly_amount = 2000  # 每月2000元
    
    print(f"  定投基金: {', '.join(fund_codes)}")
    print(f"  每月金额: {monthly_amount}元")
    print(f"  分配方案:")
    for code in fund_codes:
        print(f"    {code}: {monthly_amount/len(fund_codes):.0f}元/月")


def example_4_rebalance_analysis():
    """示例4: 再平衡分析"""
    print("\n" + "=" * 60)
    print("示例4: 组合再平衡分析")
    print("=" * 60)
    
    # 目标配置
    target = {
        "000001": 0.20,
        "110020": 0.30,
        "260108": 0.25,
        "000171": 0.25
    }
    
    # 模拟当前配置（因市场波动偏离目标）
    current = {
        "000001": 0.18,  # 下跌偏离
        "110020": 0.35,  # 上涨偏离
        "260108": 0.27,  # 上涨偏离
        "000171": 0.20   # 下跌偏离
    }
    
    print("\n目标配置 vs 当前配置:")
    for code in target:
        t = target[code]
        c = current.get(code, 0)
        deviation = c - t
        print(f"  {code}: 目标{t*100:.0f}% | 当前{c*100:.0f}% | 偏离{deviation*100:+.0f}%")
    
    # 计算再平衡信号
    signals = calculate_rebalance_signal(current, target, threshold=0.03)
    
    print("\n再平衡建议 (偏离>3%触发):")
    if signals:
        for s in signals:
            action = "买入" if s['action'] == 'buy' else "卖出"
            print(f"  {s['fund']}: {action} {s['adjust_amount']*100:.1f}%")
    else:
        print("  暂无再平衡需求")


def example_5_market_data():
    """示例5: 市场数据查询"""
    print("\n" + "=" * 60)
    print("示例5: 市场数据查询")
    print("=" * 60)
    
    try:
        client = create_client_from_env()
    except ValueError as e:
        print(f"错误: {e}")
        return
    
    # 获取市场概览
    print("\n获取市场概览...")
    overview = client.get_market_overview()
    if "error" not in overview:
        data = overview.get('data', {})
        print(f"  上证指数: {data.get('sh_index', 'N/A')}")
        print(f"  深证成指: {data.get('sz_index', 'N/A')}")
        print(f"  沪深300: {data.get('hs300', 'N/A')}")
    
    # 获取行业表现
    print("\n获取行业表现...")
    sectors = client.get_sector_performance()
    if sectors:
        print("  涨幅前3行业:")
        sorted_sectors = sorted(sectors, key=lambda x: x.get('change', 0), reverse=True)[:3]
        for s in sorted_sectors:
            print(f"    {s.get('name')}: {s.get('change', 0):+.2f}%")


def run_all_examples():
    """运行所有示例"""
    examples = [
        example_1_basic_fund_query,
        example_2_portfolio_analysis,
        example_3_strategy_recommendation,
        example_4_rebalance_analysis,
        example_5_market_data,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n示例执行出错: {e}")
        print("\n" + "-" * 60)


if __name__ == "__main__":
    print("且慢API与本地分析工具结合使用示例")
    print("=" * 60)
    print("\n使用前请设置环境变量:")
    print("  export QIEMAN_API_KEY='your_api_key'")
    print("  export QIEMAN_API_SECRET='your_api_secret'")
    print("\n" + "=" * 60)
    
    import sys
    if len(sys.argv) > 1:
        # 运行指定示例
        example_num = sys.argv[1]
        func_name = f"example_{example_num}_"
        for example in [example_1_basic_fund_query, example_2_portfolio_analysis,
                       example_3_strategy_recommendation, example_4_rebalance_analysis,
                       example_5_market_data]:
            if example.__name__.startswith(func_name):
                example()
                break
    else:
        # 运行所有示例
        print("\n运行所有示例...\n")
        run_all_examples()