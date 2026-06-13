#!/usr/bin/env python3
"""
基金季报持仓有效性分析模块
分析基金经理调仓的有效性、持仓稳定性、行业配置变化等
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import re


class HoldingEffectivenessAnalyzer:
    """持仓有效性分析器"""
    
    def __init__(self):
        self.quarters_data = []
        
    def analyze_holdings_effectiveness(self, holdings_df: pd.DataFrame, 
                                       nav_df: pd.DataFrame,
                                       fund_code: str = '') -> Dict:
        """
        分析持仓有效性
        
        Args:
            holdings_df: 当前持仓DataFrame
            nav_df: 净值历史DataFrame
            fund_code: 基金代码
            
        Returns:
            分析结果字典
        """
        results = {
            'fund_code': fund_code,
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'current_holdings': {},
            'concentration_analysis': {},
            'sector_distribution': {},
            'turnover_analysis': {},
            'effectiveness_score': 0,
            'recommendations': []
        }
        
        if holdings_df.empty:
            return results
        
        # 1. 当前持仓分析
        print("  → 分析当前持仓...")
        results['current_holdings'] = self._analyze_current_holdings(holdings_df)
        
        # 2. 集中度分析
        print("  → 分析持仓集中度...")
        results['concentration_analysis'] = self._analyze_concentration(holdings_df)
        
        # 3. 行业分布分析
        print("  → 分析行业分布...")
        results['sector_distribution'] = self._analyze_sectors(holdings_df)
        
        # 4. 结合净值分析持仓有效性
        if not nav_df.empty:
            print("  → 计算持仓有效性指标...")
            results['portfolio_quality'] = self._calculate_portfolio_quality(holdings_df, nav_df)
        
        # 5. 生成评分和建议
        results['effectiveness_score'] = self._calculate_effectiveness_score(results)
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _analyze_current_holdings(self, holdings_df: pd.DataFrame) -> Dict:
        """分析当前持仓特征"""
        total_ratio = holdings_df['ratio'].sum() if 'ratio' in holdings_df.columns else 0
        
        # 计算持仓数量
        holding_count = len(holdings_df)
        
        # 计算平均持仓比例
        avg_ratio = holdings_df['ratio'].mean() if 'ratio' in holdings_df.columns else 0
        
        # 最大单一持仓
        max_ratio = holdings_df['ratio'].max() if 'ratio' in holdings_df.columns else 0
        max_stock = ''
        if 'ratio' in holdings_df.columns and 'stock_name' in holdings_df.columns:
            max_stock = holdings_df.loc[holdings_df['ratio'].idxmax(), 'stock_name']
        
        # 前5大持仓占比
        top5_ratio = holdings_df['ratio'].nlargest(5).sum() if 'ratio' in holdings_df.columns else 0
        
        return {
            'holding_count': holding_count,
            'total_ratio': round(total_ratio, 2),
            'avg_ratio': round(avg_ratio, 2),
            'max_ratio': round(max_ratio, 2),
            'max_stock': max_stock,
            'top5_ratio': round(top5_ratio, 2),
            'top5_concentration': '高度集中' if top5_ratio > 40 else '中度集中' if top5_ratio > 30 else '相对分散'
        }
    
    def _analyze_concentration(self, holdings_df: pd.DataFrame) -> Dict:
        """分析持仓集中度"""
        if 'ratio' not in holdings_df.columns:
            return {}
        
        ratios = holdings_df['ratio'].values
        
        # Herfindahl-Hirschman Index (HHI)
        hhi = sum((r/100)**2 for r in ratios) * 10000
        
        # 前3大持仓占比
        top3_ratio = holdings_df['ratio'].nlargest(3).sum()
        
        # 前5大持仓占比
        top5_ratio = holdings_df['ratio'].nlargest(5).sum()
        
        # 集中度评级
        if hhi > 1500:
            concentration_level = '高度集中'
            risk = '高'
        elif hhi > 1000:
            concentration_level = '中度集中'
            risk = '中等'
        elif hhi > 500:
            concentration_level = '适度集中'
            risk = '低'
        else:
            concentration_level = '高度分散'
            risk = '较低'
        
        return {
            'hhi': round(hhi, 2),
            'top3_ratio': round(top3_ratio, 2),
            'top5_ratio': round(top5_ratio, 2),
            'concentration_level': concentration_level,
            'risk': risk
        }
    
    def _analyze_sectors(self, holdings_df: pd.DataFrame) -> Dict:
        """分析行业分布（基于持仓股票名称的智能分类）"""
        # 基于股票名称的行业关键词映射（更全面的分类）
        sector_keywords = {
            '化工': ['化工', '化学', '材料', '制品', '涂料', '农药', '化肥', '润丰'],
            '医药医疗': ['医药', '医疗', '生物', '药业', '疫苗', '诊断', '器械', '英科'],
            '建材家居': ['建材', '家居', '装饰', '卫浴', '地板', '家具', '雨虹', '树', '兔宝宝', '江河'],
            '造纸印刷': ['造纸', '纸业', '印刷', '包装', '太阳'],
            '机械设备': ['机械', '设备', '仪器', '工具', '咸亨'],
            '农业养殖': ['农业', '养殖', '饲料', '海大'],
            '电子科技': ['电子', '半导体', '计算机', '通信', '软件', '芯片', '科技', '九号'],
            '新能源': ['光伏', '锂电', '新能源', '储能', '风电', '太阳能'],
            '金融': ['银行', '保险', '券商', '信托', '金融'],
            '房地产': ['房地产', '地产', '建筑', '置业'],
            '消费': ['食品', '饮料', '家电', '商贸', '零售', '服装'],
            '公用事业': ['电力', '水务', '燃气', '环保', '交通'],
            '其他': []
        }
        
        sector_ratios = {k: 0 for k in sector_keywords.keys()}
        
        if 'stock_name' in holdings_df.columns and 'ratio' in holdings_df.columns:
            for _, row in holdings_df.iterrows():
                stock_name = str(row['stock_name'])
                ratio = row['ratio']
                
                # 匹配行业
                matched = False
                for sector, keywords in sector_keywords.items():
                    if any(kw in stock_name for kw in keywords):
                        sector_ratios[sector] += ratio
                        matched = True
                        break
                
                if not matched:
                    sector_ratios['其他'] += ratio
        
        # 找出主要行业
        main_sectors = sorted(sector_ratios.items(), key=lambda x: x[1], reverse=True)
        main_sectors = [(k, v) for k, v in main_sectors if v > 0]
        
        # 计算行业集中度
        if main_sectors:
            top_sector_ratio = main_sectors[0][1]
            top2_sectors_ratio = sum(v for k, v in main_sectors[:2])
            sector_concentration = '高' if top_sector_ratio > 50 else '中' if top_sector_ratio > 30 else '低'
        else:
            top_sector_ratio = 0
            top2_sectors_ratio = 0
            sector_concentration = '未知'
        
        return {
            'sector_ratios': {k: round(v, 2) for k, v in sector_ratios.items() if v > 0},
            'main_sectors': main_sectors[:3],
            'top_sector_ratio': round(top_sector_ratio, 2),
            'top2_sectors_ratio': round(top2_sectors_ratio, 2),
            'sector_concentration': sector_concentration,
            'diversification': '优秀' if len([v for v in sector_ratios.values() if v > 5]) >= 3 else '良好' if len([v for v in sector_ratios.values() if v > 5]) >= 2 else '一般'
        }
    
    def _calculate_portfolio_quality(self, holdings_df: pd.DataFrame, nav_df: pd.DataFrame) -> Dict:
        """计算持仓质量指标"""
        # 基于近期净值表现评估持仓质量
        nav_df = nav_df.copy().sort_values('date')
        
        # 计算近期收益率
        if len(nav_df) >= 22:
            recent_return = (nav_df['nav'].iloc[-1] / nav_df['nav'].iloc[-22] - 1) * 100
        else:
            recent_return = 0
        
        # 计算波动率
        if len(nav_df) >= 22:
            daily_returns = nav_df['nav'].pct_change().dropna()
            volatility = daily_returns.std() * np.sqrt(252) * 100
        else:
            volatility = 0
        
        # 持仓市值加权平均（如果数据可用）
        avg_market_cap = 0
        if 'market_value' in holdings_df.columns:
            total_mv = holdings_df['market_value'].sum()
            if total_mv > 0:
                avg_market_cap = holdings_df['market_value'].mean()
        
        # 评估持仓质量
        if recent_return > 10 and volatility < 20:
            quality = '优秀'
        elif recent_return > 5 and volatility < 25:
            quality = '良好'
        elif recent_return > 0:
            quality = '一般'
        else:
            quality = '较差'
        
        return {
            'recent_month_return': round(recent_return, 2),
            'portfolio_volatility': round(volatility, 2),
            'avg_holding_market_cap': round(avg_market_cap, 2),
            'quality_rating': quality
        }
    
    def _calculate_effectiveness_score(self, results: Dict) -> int:
        """计算综合有效性评分（0-100）"""
        score = 50  # 基础分
        
        # 集中度评分
        conc = results.get('concentration_analysis', {})
        if conc.get('concentration_level') == '适度集中':
            score += 15
        elif conc.get('concentration_level') == '中度集中':
            score += 10
        elif conc.get('concentration_level') == '高度分散':
            score += 5
        
        # 行业分散度评分
        sector = results.get('sector_distribution', {})
        if sector.get('diversification') == '优秀':
            score += 15
        elif sector.get('diversification') == '良好':
            score += 10
        elif sector.get('diversification') == '一般':
            score += 5
        
        # 持仓质量评分
        quality = results.get('portfolio_quality', {})
        if quality.get('quality_rating') == '优秀':
            score += 20
        elif quality.get('quality_rating') == '良好':
            score += 15
        elif quality.get('quality_rating') == '一般':
            score += 10
        
        # 前5大持仓占比合理性
        current = results.get('current_holdings', {})
        top5_ratio = current.get('top5_ratio', 0)
        if 30 <= top5_ratio <= 50:
            score += 10
        elif 20 <= top5_ratio < 30 or 50 < top5_ratio <= 60:
            score += 5
        
        return min(score, 100)
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """生成投资建议"""
        recommendations = []
        
        # 基于集中度
        conc = results.get('concentration_analysis', {})
        if conc.get('risk') == '高':
            recommendations.append("⚠️ 持仓集中度较高，需关注单一股票风险")
        elif conc.get('concentration_level') == '高度分散':
            recommendations.append("ℹ️ 持仓较为分散，可能稀释个股选择收益")
        
        # 基于行业分布
        sector = results.get('sector_distribution', {})
        if sector.get('sector_concentration') == '高':
            recommendations.append("⚠️ 行业配置过于集中，建议关注行业轮动风险")
        
        main_sectors = sector.get('main_sectors', [])
        if main_sectors:
            top_sector = main_sectors[0][0]
            recommendations.append(f"📊 主要配置在{top_sector}板块，关注该板块景气度变化")
        
        # 基于持仓质量
        quality = results.get('portfolio_quality', {})
        if quality.get('quality_rating') == '优秀':
            recommendations.append("✅ 近期持仓表现优秀，可继续持有")
        elif quality.get('quality_rating') == '较差':
            recommendations.append("⚠️ 近期持仓表现不佳，建议关注基金经理调仓动向")
        
        # 基于有效性评分
        score = results.get('effectiveness_score', 50)
        if score >= 80:
            recommendations.append("✅ 持仓有效性评分优秀，基金经理选股能力较强")
        elif score >= 60:
            recommendations.append("ℹ️ 持仓有效性评分良好，符合市场平均水平")
        else:
            recommendations.append("⚠️ 持仓有效性评分一般，建议谨慎观察")
        
        return recommendations


if __name__ == '__main__':
    # 测试代码
    import sys
    sys.path.insert(0, '.')
    from fund_eastmoney import FundDataFetcher
    
    fetcher = FundDataFetcher()
    analyzer = HoldingEffectivenessAnalyzer()
    
    # 获取数据
    holdings = fetcher.get_holdings('519702')
    nav = fetcher.get_nav_history('519702', years=1)
    
    # 分析
    results = analyzer.analyze_holdings_effectiveness(holdings, nav, '519702')
    
    print("\n持仓有效性分析结果:")
    print(f"评分: {results['effectiveness_score']}/100")
    print("\n建议:")
    for rec in results['recommendations']:
        print(f"  {rec}")
