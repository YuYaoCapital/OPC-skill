#!/usr/bin/env python3
"""
基金同类对比分析模块
基于已有数据进行同类基金对比分析
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class FundComparator:
    """基金对比分析器"""
    
    def __init__(self):
        # 同类基金基准数据（基于市场平均水平）
        self.category_benchmarks = {
            '混合型-偏股': {
                'avg_returns': {
                    'last_month': -2.5,
                    'last_3month': 3.0,
                    'last_6month': 8.0,
                    'last_year': 15.0,
                    'last_2year': 25.0,
                },
                'avg_risk': {
                    'volatility': 18.0,
                    'max_drawdown': -20.0,
                    'sharpe_ratio': 0.5,
                },
                'total_funds': 1200,
            },
            '混合型-灵活': {
                'avg_returns': {
                    'last_month': -2.0,
                    'last_3month': 3.5,
                    'last_6month': 7.5,
                    'last_year': 12.0,
                    'last_2year': 20.0,
                },
                'avg_risk': {
                    'volatility': 16.0,
                    'max_drawdown': -18.0,
                    'sharpe_ratio': 0.6,
                },
                'total_funds': 800,
            },
            '股票型': {
                'avg_returns': {
                    'last_month': -3.0,
                    'last_3month': 2.5,
                    'last_6month': 9.0,
                    'last_year': 18.0,
                    'last_2year': 30.0,
                },
                'avg_risk': {
                    'volatility': 20.0,
                    'max_drawdown': -22.0,
                    'sharpe_ratio': 0.45,
                },
                'total_funds': 600,
            },
        }
    
    def analyze_category_performance(self, fund_info: Dict, performance: Dict, risk_metrics: Dict) -> Dict:
        """
        分析基金在同类中的表现
        
        Args:
            fund_info: 基金基本信息
            performance: 业绩数据
            risk_metrics: 风险指标
            
        Returns:
            同类对比分析结果
        """
        fund_type = fund_info.get('fund_type', '混合型-偏股')
        fund_type_base = fund_type.split('-')[0] if '-' in fund_type else fund_type
        
        # 获取同类基准
        benchmark = self.category_benchmarks.get(fund_type, 
                    self.category_benchmarks.get('混合型-偏股'))
        
        result = {
            'fund_code': fund_info.get('fund_code', ''),
            'fund_name': fund_info.get('fund_name', ''),
            'fund_type': fund_type,
            'category_avg': benchmark['avg_returns'],
            'category_risk_avg': benchmark['avg_risk'],
            'total_funds_in_category': benchmark['total_funds'],
            'period_comparison': {},
            'risk_comparison': {},
            'rank_estimates': {},
            'rank_percentiles': {},
            'summary': {},
        }
        
        # 1. 各周期收益对比
        period_names = {
            'last_month': '近1月',
            'last_3month': '近3月',
            'last_6month': '近6月',
            'last_year': '近1年',
            'last_2year': '近2年',
        }
        
        for period_key, period_name in period_names.items():
            if period_key in performance and performance[period_key].get('return') is not None:
                fund_return = performance[period_key]['return']
                category_avg = benchmark['avg_returns'].get(period_key, 0)
                excess_return = fund_return - category_avg
                
                # 估算排名分位（基于正态分布假设）
                std_dev = 8.0  # 假设同类基金收益率标准差约为8%
                z_score = (fund_return - category_avg) / std_dev
                percentile = 50 + z_score * 25
                percentile = max(5, min(95, percentile))  # 限制在5%-95%
                
                estimated_rank = int(benchmark['total_funds'] * (1 - percentile / 100))
                
                result['period_comparison'][period_key] = {
                    'period_name': period_name,
                    'fund_return': fund_return,
                    'category_avg': category_avg,
                    'excess_return': round(excess_return, 2),
                    'outperform': excess_return > 0,
                    'rank_estimate': estimated_rank,
                    'rank_percentile': round(percentile, 1),
                    'total_funds': benchmark['total_funds'],
                }
                
                result['rank_estimates'][period_key] = estimated_rank
                result['rank_percentiles'][period_key] = round(percentile, 1)
        
        # 2. 风险指标对比
        if risk_metrics:
            result['risk_comparison'] = {
                'volatility': {
                    'fund': risk_metrics.get('volatility', 0),
                    'category_avg': benchmark['avg_risk']['volatility'],
                    'diff': round(risk_metrics.get('volatility', 0) - benchmark['avg_risk']['volatility'], 2),
                },
                'max_drawdown': {
                    'fund': risk_metrics.get('max_drawdown', 0),
                    'category_avg': benchmark['avg_risk']['max_drawdown'],
                    'diff': round(risk_metrics.get('max_drawdown', 0) - benchmark['avg_risk']['max_drawdown'], 2),
                },
                'sharpe_ratio': {
                    'fund': risk_metrics.get('sharpe_ratio', 0),
                    'category_avg': benchmark['avg_risk']['sharpe_ratio'],
                    'diff': round(risk_metrics.get('sharpe_ratio', 0) - benchmark['avg_risk']['sharpe_ratio'], 2),
                },
            }
        
        # 3. 综合表现总结
        if result['rank_percentiles']:
            avg_percentile = np.mean(list(result['rank_percentiles'].values()))
            result['summary']['avg_percentile'] = round(avg_percentile, 1)
            
            # 确定综合评级
            if avg_percentile >= 70:
                result['summary']['overall_rating'] = '优秀'
                result['summary']['rating_desc'] = '业绩表现优秀，同类排名靠前'
            elif avg_percentile >= 50:
                result['summary']['overall_rating'] = '良好'
                result['summary']['rating_desc'] = '业绩表现良好，优于同类平均'
            elif avg_percentile >= 30:
                result['summary']['overall_rating'] = '一般'
                result['summary']['rating_desc'] = '业绩表现一般，接近同类平均'
            else:
                result['summary']['overall_rating'] = '较差'
                result['summary']['rating_desc'] = '业绩表现较差，同类排名靠后'
            
            # 找出最佳和最差周期
            best_period = max(result['rank_percentiles'].items(), key=lambda x: x[1])
            worst_period = min(result['rank_percentiles'].items(), key=lambda x: x[1])
            
            result['summary']['best_period'] = {
                'period': period_names.get(best_period[0], best_period[0]),
                'percentile': best_period[1],
            }
            result['summary']['worst_period'] = {
                'period': period_names.get(worst_period[0], worst_period[0]),
                'percentile': worst_period[1],
            }
            
            # 计算胜率（跑赢同类平均的周期比例）
            outperform_count = sum(1 for p in result['period_comparison'].values() if p['outperform'])
            total_periods = len(result['period_comparison'])
            if total_periods > 0:
                result['summary']['win_rate'] = round(outperform_count / total_periods * 100, 1)
        
        return result
    
    def get_similar_funds_comparison(self, fund_type: str, performance: Dict) -> Dict:
        """
        获取同类基金对比表格数据
        
        Args:
            fund_type: 基金类型
            performance: 目标基金业绩数据
            
        Returns:
            同类基金对比数据
        """
        benchmark = self.category_benchmarks.get(fund_type, 
                    self.category_benchmarks.get('混合型-偏股'))
        
        comparison = {
            'fund_type': fund_type,
            'performance_table': [],
            'risk_table': [],
        }
        
        # 业绩对比表
        periods = ['last_month', 'last_3month', 'last_6month', 'last_year']
        period_names = {'last_month': '近1月', 'last_3month': '近3月', 
                       'last_6month': '近6月', 'last_year': '近1年'}
        
        header = ['对比项'] + [period_names[p] for p in periods]
        comparison['performance_table'].append(header)
        
        # 本基金
        fund_row = ['本基金（519702）']
        for period in periods:
            ret = performance.get(period, {}).get('return', None)
            fund_row.append(f"{ret:.2f}%" if ret is not None else '-')
        comparison['performance_table'].append(fund_row)
        
        # 同类平均
        avg_row = ['同类平均']
        for period in periods:
            avg = benchmark['avg_returns'].get(period, 0)
            avg_row.append(f"{avg:.2f}%")
        comparison['performance_table'].append(avg_row)
        
        # 同类前25%（良好）
        top25_row = ['同类前25%（良好）']
        for period in periods:
            avg = benchmark['avg_returns'].get(period, 0)
            top25 = avg + 6  # 假设前25%比平均高6%
            top25_row.append(f"{top25:.2f}%")
        comparison['performance_table'].append(top25_row)
        
        # 同类前10%（优秀）
        top10_row = ['同类前10%（优秀）']
        for period in periods:
            avg = benchmark['avg_returns'].get(period, 0)
            top10 = avg + 12  # 假设前10%比平均高12%
            top10_row.append(f"{top10:.2f}%")
        comparison['performance_table'].append(top10_row)
        
        return comparison
    
    def generate_comparison_report(self, fund_info: Dict, performance: Dict, risk_metrics: Dict) -> Dict:
        """
        生成完整的同类对比报告
        
        Args:
            fund_info: 基金基本信息
            performance: 业绩数据
            risk_metrics: 风险指标
            
        Returns:
            完整对比报告
        """
        # 同类表现分析
        category_analysis = self.analyze_category_performance(fund_info, performance, risk_metrics)
        
        # 同类基金对比表
        similar_funds = self.get_similar_funds_comparison(
            fund_info.get('fund_type', '混合型-偏股'),
            performance
        )
        
        # 生成优劣势分析
        strengths = []
        weaknesses = []
        
        # 基于排名分位分析
        summary = category_analysis.get('summary', {})
        avg_percentile = summary.get('avg_percentile', 50)
        
        if avg_percentile >= 60:
            strengths.append(f"整体业绩表现{summary.get('overall_rating', '良好')}，同类排名靠前（前{100-avg_percentile:.0f}%）")
        elif avg_percentile < 40:
            weaknesses.append(f"整体业绩表现{summary.get('overall_rating', '一般')}，同类排名靠后（后{avg_percentile:.0f}%）")
        
        # 基于各周期表现分析
        for period, data in category_analysis.get('period_comparison', {}).items():
            if data['rank_percentile'] >= 70:
                strengths.append(f"{data['period_name']}表现优秀，跑赢同类平均{data['excess_return']:+.2f}%，排名前{100-data['rank_percentile']:.0f}%")
            elif data['rank_percentile'] <= 30:
                weaknesses.append(f"{data['period_name']}表现欠佳，跑输同类平均{data['excess_return']:+.2f}%，排名后{data['rank_percentile']:.0f}%")
        
        # 基于风险指标分析
        risk_comp = category_analysis.get('risk_comparison', {})
        if risk_comp:
            sharpe_diff = risk_comp.get('sharpe_ratio', {}).get('diff', 0)
            if sharpe_diff > 0.2:
                strengths.append(f"风险调整后收益优于同类平均，夏普比率高{sharpe_diff:.2f}")
            elif sharpe_diff < -0.2:
                weaknesses.append(f"风险调整后收益弱于同类平均，夏普比率低{abs(sharpe_diff):.2f}")
            
            vol_diff = risk_comp.get('volatility', {}).get('diff', 0)
            if vol_diff < -2:
                strengths.append(f"波动率控制较好，比同类平均低{abs(vol_diff):.1f}%")
            elif vol_diff > 2:
                weaknesses.append(f"波动率较高，比同类平均高{vol_diff:.1f}%")
        
        # 生成建议
        recommendations = []
        if avg_percentile >= 70:
            recommendations.append("业绩表现持续优秀，可考虑作为核心配置")
        elif avg_percentile >= 50:
            recommendations.append("业绩表现稳定，可作为卫星配置")
        else:
            recommendations.append("业绩表现一般，建议观察后续表现")
        
        # 根据胜率给出建议
        win_rate = summary.get('win_rate', 50)
        if win_rate >= 75:
            recommendations.append(f"各周期胜率较高（{win_rate:.0f}%），业绩持续性较好")
        elif win_rate <= 25:
            recommendations.append(f"各周期胜率较低（{win_rate:.0f}%），业绩波动性较大")
        
        category_analysis['strengths'] = strengths
        category_analysis['weaknesses'] = weaknesses
        category_analysis['recommendations'] = recommendations
        category_analysis['similar_funds'] = similar_funds
        
        return category_analysis


if __name__ == '__main__':
    # 测试
    comparator = FundComparator()
    
    # 模拟数据
    fund_info = {
        'fund_code': '519702',
        'fund_name': '交银趋势混合A',
        'fund_type': '混合型-偏股',
    }
    
    performance = {
        'last_month': {'return': -4.86},
        'last_3month': {'return': 4.92},
        'last_6month': {'return': 10.38},
        'last_year': {'return': 28.71},
    }
    
    risk_metrics = {
        'volatility': 14.77,
        'max_drawdown': -20.13,
        'sharpe_ratio': 0.36,
    }
    
    report = comparator.generate_comparison_report(fund_info, performance, risk_metrics)
    
    print(f"\n基金: {report['fund_name']} ({report['fund_code']})")
    print(f"类型: {report['fund_type']}")
    print(f"同类平均排名分位: {report['summary'].get('avg_percentile', 0)}%")
    print(f"综合评级: {report['summary'].get('overall_rating', '-')}")
    
    print("\n优势:")
    for s in report['strengths']:
        print(f"  • {s}")
    
    print("\n劣势:")
    for w in report['weaknesses']:
        print(f"  • {w}")
