#!/usr/bin/env python3
"""
基金历史持仓分析模块
分析过去多个季度的十大重仓股变化，评估基金经理选股能力
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import os
import re


class HoldingHistoryAnalyzer:
    """历史持仓分析器"""
    
    def __init__(self):
        self.quarterly_holdings = {}  # 存储各季度持仓
        self.stock_performance = {}   # 存储股票表现
        
    def load_holding_history(self, fund_code: str, data_dir: str = '/Users/r9') -> Dict:
        """
        加载历史持仓数据
        
        Args:
            fund_code: 基金代码
            data_dir: 数据文件目录
            
        Returns:
            各季度持仓数据字典
        """
        print(f"  加载 {fund_code} 历史持仓数据...")
        
        # 查找所有历史持仓文件
        pattern = re.compile(rf'{fund_code}_(\d{{4}})(\d)Q_holdings\.csv')
        
        quarterly_data = {}
        
        for filename in os.listdir(data_dir):
            match = pattern.match(filename)
            if match:
                year = match.group(1)
                quarter = match.group(2)
                key = f"{year}Q{quarter}"
                
                filepath = os.path.join(data_dir, filename)
                try:
                    df = self._parse_holding_csv(filepath)
                    if not df.empty:
                        quarterly_data[key] = df
                        print(f"    ✅ 加载 {key}: {len(df)} 只股票")
                except Exception as e:
                    print(f"    ❌ 加载 {key} 失败: {e}")
        
        self.quarterly_holdings = quarterly_data
        return quarterly_data
    
    def _parse_holding_csv(self, filepath: str) -> pd.DataFrame:
        """解析持仓CSV文件（处理千分位逗号）"""
        import csv
        
        data = []
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            # 使用csv模块正确解析（处理引号内的逗号）
            reader = csv.reader(f)
            header = next(reader)  # 跳过表头
            
            for row in reader:
                if len(row) >= 6:
                    rank = row[0]
                    code = row[1]
                    name = row[2]
                    ratio = row[3]
                    shares = row[4]
                    market_value = row[5]
                    
                    try:
                        data.append({
                            'rank': int(rank),
                            'stock_code': code,
                            'stock_name': name,
                            'ratio': float(ratio.replace('%', '').replace('"', '')),
                            'shares': float(shares.replace(',', '').replace('"', '')),
                            'market_value': float(market_value.replace(',', '').replace('"', '')),
                        })
                    except ValueError as e:
                        print(f"    解析行失败: {row}, 错误: {e}")
                        continue
        
        return pd.DataFrame(data)
    
    def analyze_holding_changes(self) -> Dict:
        """
        分析持仓变化情况
        
        Returns:
            持仓变化分析结果
        """
        if len(self.quarterly_holdings) < 2:
            return {
                'quarters_available': list(self.quarterly_holdings.keys()),
                'analysis': '历史数据不足，需要至少2个季度的数据进行对比分析'
            }
        
        # 按时间排序
        sorted_quarters = sorted(self.quarterly_holdings.keys())
        
        results = {
            'quarters_analyzed': sorted_quarters,
            'total_quarters': len(sorted_quarters),
            'holding_stability': {},
            'turnover_analysis': {},
            'core_holdings': [],
            'band_trading': [],
            'sector_rotation': {},
            'stock_performance': {},
        }
        
        # 1. 分析持仓稳定性 - 追踪每只股票持有的季度数
        stock_quarters = {}
        for quarter in sorted_quarters:
            df = self.quarterly_holdings[quarter]
            for _, row in df.iterrows():
                stock_name = row['stock_name']
                if stock_name not in stock_quarters:
                    stock_quarters[stock_name] = []
                stock_quarters[stock_name].append(quarter)
        
        # 识别核心持仓（持有>=4个季度）和波段操作（持有<3个季度）
        for stock, quarters in stock_quarters.items():
            if len(quarters) >= 4:
                results['core_holdings'].append({
                    'stock_name': stock,
                    'quarters_held': len(quarters),
                    'quarters': quarters
                })
            elif len(quarters) <= 2:
                results['band_trading'].append({
                    'stock_name': stock,
                    'quarters_held': len(quarters),
                    'quarters': quarters
                })
        
        results['holding_stability'] = {
            'core_holdings_count': len(results['core_holdings']),
            'band_trading_count': len(results['band_trading']),
            'total_stocks_traded': len(stock_quarters),
        }
        
        # 2. 分析季度调仓情况
        if len(sorted_quarters) >= 2:
            quarter_changes = []
            for i in range(1, len(sorted_quarters)):
                prev_q = sorted_quarters[i-1]
                curr_q = sorted_quarters[i]
                
                prev_stocks = set(self.quarterly_holdings[prev_q]['stock_name'].tolist())
                curr_stocks = set(self.quarterly_holdings[curr_q]['stock_name'].tolist())
                
                added = curr_stocks - prev_stocks
                removed = prev_stocks - curr_stocks
                continued = curr_stocks & prev_stocks
                
                quarter_changes.append({
                    'period': f"{prev_q} -> {curr_q}",
                    'added': list(added),
                    'removed': list(removed),
                    'continued': list(continued),
                    'turnover_rate': (len(added) + len(removed)) / 10 * 100  # 假设10只重仓股
                })
            
            results['quarterly_changes'] = quarter_changes
            
            # 计算平均换手率
            avg_turnover = np.mean([c['turnover_rate'] for c in quarter_changes])
            results['turnover_analysis'] = {
                'average_turnover_rate': round(avg_turnover, 2),
                'turnover_level': '高' if avg_turnover > 60 else '中' if avg_turnover > 30 else '低',
            }
        
        return results
    
    def evaluate_stock_picking_ability(self, nav_df: Optional[pd.DataFrame] = None) -> Dict:
        """
        评估选股能力
        
        Args:
            nav_df: 净值数据（用于对比）
            
        Returns:
            选股能力评估结果
        """
        results = {
            'picking_skill_score': 0,
            'timing_skill_score': 0,
            'overall_score': 0,
            'evaluation': '',
            'key_insights': []
        }
        
        # 如果没有足够的历史数据，返回基础评估
        if len(self.quarterly_holdings) < 1:
            results['evaluation'] = '历史持仓数据不足，无法评估选股能力'
            return results
        
        # 基于持仓集中度和稳定性评估
        changes = self.analyze_holding_changes()
        
        stability = changes.get('holding_stability', {})
        turnover = changes.get('turnover_analysis', {})
        
        # 1. 选股能力评分（基于核心持仓比例）
        total_stocks = stability.get('total_stocks_traded', 0)
        core_holdings = stability.get('core_holdings_count', 0)
        
        if total_stocks > 0:
            core_ratio = core_holdings / total_stocks
            # 核心持仓比例适中（30%-50%）表示选股有重点
            if 0.3 <= core_ratio <= 0.5:
                results['picking_skill_score'] = 75
            elif core_ratio > 0.5:
                results['picking_skill_score'] = 65  # 过于集中
            else:
                results['picking_skill_score'] = 55  # 过于分散
        else:
            results['picking_skill_score'] = 50
        
        # 2. 择时能力评分（基于换手率适中程度）
        turnover_rate = turnover.get('average_turnover_rate', 50)
        if 30 <= turnover_rate <= 50:
            results['timing_skill_score'] = 75  # 换手率适中，择时合理
        elif turnover_rate < 30:
            results['timing_skill_score'] = 65  # 换手率过低，可能过于保守
        else:
            results['timing_skill_score'] = 55  # 换手率过高，可能过于频繁
        
        # 3. 综合评分
        results['overall_score'] = (results['picking_skill_score'] + results['timing_skill_score']) // 2
        
        # 4. 生成评价
        if results['overall_score'] >= 70:
            results['evaluation'] = '优秀'
            results['key_insights'].append('✅ 基金经理选股能力较强，有明确的核心持仓')
        elif results['overall_score'] >= 60:
            results['evaluation'] = '良好'
            results['key_insights'].append('ℹ️ 基金经理选股能力良好，符合市场平均水平')
        else:
            results['evaluation'] = '一般'
            results['key_insights'].append('⚠️ 基金经理选股策略不够清晰，需进一步观察')
        
        # 5. 基于换手率的具体建议
        turnover_level = turnover.get('turnover_level', '中')
        if turnover_level == '高':
            results['key_insights'].append('⚠️ 调仓频率较高，可能偏向波段操作，需关注交易成本')
        elif turnover_level == '低':
            results['key_insights'].append('ℹ️ 调仓频率较低，持股相对稳定，偏向长期投资')
        
        # 6. 核心持仓分析
        core_holdings = changes.get('core_holdings', [])
        if core_holdings:
            top_core = sorted(core_holdings, key=lambda x: x['quarters_held'], reverse=True)[:3]
            core_names = [c['stock_name'] for c in top_core]
            results['key_insights'].append(f"📊 核心持仓（长期持有）：{', '.join(core_names)}")
        
        return results
    
    def analyze_manager_style(self) -> Dict:
        """
        分析基金经理投资风格
        
        Returns:
            投资风格分析结果
        """
        changes = self.analyze_holding_changes()
        turnover = changes.get('turnover_analysis', {})
        
        turnover_level = turnover.get('turnover_level', '中')
        core_count = changes.get('holding_stability', {}).get('core_holdings_count', 0)
        
        # 判断投资风格
        if turnover_level == '低' and core_count >= 3:
            style = '价值投资型'
            characteristics = [
                '持股周期长，注重基本面研究',
                '核心持仓稳定，不轻易调仓',
                '偏向长期价值投资策略'
            ]
        elif turnover_level == '高':
            style = '趋势交易型'
            characteristics = [
                '调仓频率高，紧跟市场热点',
                '灵活应对市场变化',
                '偏向趋势跟踪和行业轮动'
            ]
        else:
            style = '均衡配置型'
            characteristics = [
                '持股周期适中，兼顾长期和短期机会',
                '有一定核心持仓，也会适时调整',
                '平衡收益和风险'
            ]
        
        return {
            'style': style,
            'characteristics': characteristics,
            'turnover_level': turnover_level,
            'holding_concentration': '集中' if core_count >= 4 else '分散' if core_count <= 1 else '适中'
        }
    
    def generate_full_report(self, fund_code: str) -> Dict:
        """
        生成完整的持仓历史分析报告
        
        Args:
            fund_code: 基金代码
            
        Returns:
            完整分析报告
        """
        # 加载数据
        self.load_holding_history(fund_code)
        
        # 各项分析
        changes = self.analyze_holding_changes()
        picking = self.evaluate_stock_picking_ability()
        style = self.analyze_manager_style()
        
        return {
            'fund_code': fund_code,
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'quarters_analyzed': changes.get('quarters_analyzed', []),
            'holding_changes': changes,
            'stock_picking_ability': picking,
            'manager_style': style,
            'recommendations': picking.get('key_insights', [])
        }


if __name__ == '__main__':
    # 测试
    analyzer = HoldingHistoryAnalyzer()
    report = analyzer.generate_full_report('519702')
    
    print("\n历史持仓分析报告:")
    print(f"分析季度: {report['quarters_analyzed']}")
    print(f"选股能力: {report['stock_picking_ability']['evaluation']}")
    print(f"投资风格: {report['manager_style']['style']}")
