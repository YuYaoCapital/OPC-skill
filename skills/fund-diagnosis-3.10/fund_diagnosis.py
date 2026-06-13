#!/usr/bin/env python3
"""
基金诊断3.10 - 季报深度分析工具
用于分析基金过去一年的季报数据，追踪十大重仓股变化
"""

import re
import json
import sys
import argparse
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Holding:
    """持仓数据类"""
    rank: int
    code: str
    name: str
    ratio: float  # 占净值比（百分比）
    shares: str   # 持股数
    value: str    # 持仓市值

@dataclass
class QuarterData:
    """季度数据类"""
    quarter: str  # 如 "2024Q1"
    holdings: List[Holding]
    total_ratio: float  # 前十大合计占比

class FundDiagnosis:
    """基金诊断主类"""
    
    # 行业分类映射
    INDUSTRY_MAP = {
        # 化工/农药
        "润丰股份": "化工", "国光股份": "化工", "聚合顺": "化工", 
        "瑞丰新材": "化工", "安利股份": "化工",
        # 建材/地产链
        "东方雨虹": "建材", "兔宝宝": "建材", "三棵树": "建材",
        "江河集团": "建筑", "太阳纸业": "造纸",
        # 电力
        "华能国际": "电力", "华电国际": "电力", "皖能电力": "电力",
        "大唐发电": "电力",
        # 医疗
        "英科医疗": "医疗器械",
        # 黄金/有色
        "中金黄金": "黄金", "山金国际": "黄金", "鑫铂股份": "有色",
        # 航空
        "中国国航": "航空", "南方航空": "航空",
        # 农业
        "海大集团": "农林牧渔",
        # 机械
        "杰瑞股份": "机械", "中际联合": "风电设备",
        # 其他
        "咸亨国际": "仪器仪表", "九号公司": "智能出行",
    }
    
    def __init__(self, fund_code: str):
        self.fund_code = fund_code
        self.quarters_data: Dict[str, QuarterData] = {}
        self.fund_info = {}
        
    def fetch_data(self) -> bool:
        """获取基金数据（模拟实现，实际使用时应调用API）"""
        # 这里应该调用东方财富API获取真实数据
        # 为演示 purposes，使用模拟数据
        print(f"正在获取基金 {self.fund_code} 的数据...")
        return True
    
    def analyze_concentration(self) -> Dict:
        """分析持仓集中度"""
        results = {}
        for q, data in self.quarters_data.items():
            results[q] = {
                'total_ratio': data.total_ratio,
                'top1_ratio': data.holdings[0].ratio if data.holdings else 0
            }
        return results
    
    def analyze_turnover(self) -> List[Dict]:
        """分析季度调仓"""
        quarters = sorted(self.quarters_data.keys())
        turnover_analysis = []
        
        for i in range(len(quarters) - 1):
            q1, q2 = quarters[i], quarters[i+1]
            stocks1 = {h.code: h for h in self.quarters_data[q1].holdings}
            stocks2 = {h.code: h for h in self.quarters_data[q2].holdings}
            
            new_stocks = [stocks2[code] for code in stocks2 if code not in stocks1]
            removed_stocks = [stocks1[code] for code in stocks1 if code not in stocks2]
            kept_stocks = [stocks1[code] for code in stocks1 if code in stocks2]
            
            turnover_analysis.append({
                'from': q1,
                'to': q2,
                'new_count': len(new_stocks),
                'removed_count': len(removed_stocks),
                'kept_count': len(kept_stocks),
                'new_stocks': new_stocks,
                'removed_stocks': removed_stocks,
                'intensity': '大调' if len(new_stocks) >= 4 else ('调整' if len(new_stocks) >= 2 else '微调')
            })
        
        return turnover_analysis
    
    def analyze_stability(self) -> Dict[str, Dict]:
        """分析持仓稳定性"""
        stock_quarters = {}
        stock_names = {}
        
        for q, data in self.quarters_data.items():
            for h in data.holdings:
                stock_names[h.code] = h.name
                if h.code not in stock_quarters:
                    stock_quarters[h.code] = []
                stock_quarters[h.code].append(q)
        
        stability = {}
        for code, quarters in stock_quarters.items():
            count = len(quarters)
            bar = "█" * count + "░" * (8 - count)
            stability[code] = {
                'name': stock_names[code],
                'count': count,
                'quarters': quarters,
                'bar': bar,
                'level': self._get_stability_level(count)
            }
        
        return dict(sorted(stability.items(), key=lambda x: x[1]['count'], reverse=True))
    
    def _get_stability_level(self, count: int) -> str:
        """获取稳定性等级"""
        levels = {
            8: "核心持仓，长期看好",
            7: "稳定持仓，信心较强",
            6: "主要配置，阶段性调整",
            5: "一般配置，灵活操作",
            4: "波段操作，时机敏感"
        }
        return levels.get(count, "短期配置，试探性买入")
    
    def analyze_industry_allocation(self) -> Dict[str, Dict[str, float]]:
        """分析行业配置"""
        industry_allocation = {}
        
        for q, data in self.quarters_data.items():
            industry_ratio = {}
            for h in data.holdings:
                industry = self.INDUSTRY_MAP.get(h.name, "其他")
                industry_ratio[industry] = industry_ratio.get(industry, 0) + h.ratio
            industry_allocation[q] = dict(sorted(industry_ratio.items(), 
                                                  key=lambda x: x[1], 
                                                  reverse=True))
        
        return industry_allocation
    
    def identify_theme_evolution(self) -> List[Dict]:
        """识别配置主线演变"""
        themes = []
        quarters = sorted(self.quarters_data.keys())
        
        # 简单规则识别主题
        for q in quarters:
            industry_data = self.analyze_industry_allocation()
            top_industries = list(industry_data.get(q, {}).keys())[:3]
            
            if any(ind in ['电力'] for ind in top_industries):
                theme = "防御为主"
            elif any(ind in ['建材', '建筑'] for ind in top_industries):
                theme = "地产链复苏"
            elif any(ind in ['化工'] for ind in top_industries):
                theme = "周期配置"
            else:
                theme = "均衡配置"
            
            themes.append({'quarter': q, 'theme': theme, 'industries': top_industries})
        
        return themes
    
    def calculate_effectiveness_score(self) -> Dict:
        """计算有效性评分"""
        scores = {
            'core_holding_stability': 0,
            'industry_rotation_timing': 0,
            'turnover_control': 0,
            'risk_control': 0,
            'overall': 0
        }
        
        # 核心持仓持续性评分
        stability = self.analyze_stability()
        top_holdings = [s for s in stability.values() if s['count'] >= 7]
        scores['core_holding_stability'] = min(5, len(top_holdings))
        
        # 换手率控制评分（模拟）
        scores['turnover_control'] = 4  # 默认中低换手
        
        # 风险控制评分
        concentration = self.analyze_concentration()
        ratios = [c['total_ratio'] for c in concentration.values()]
        if ratios:
            volatility = max(ratios) - min(ratios)
            scores['risk_control'] = 5 if volatility < 8 else (4 if volatility < 12 else 3)
        
        # 综合评分
        scores['overall'] = round(sum(scores.values()) / len([s for s in scores.values() if s > 0]), 1)
        
        return scores
    
    def generate_report(self) -> str:
        """生成诊断报告"""
        report = []
        report.append("=" * 80)
        report.append(f"基金诊断报告 - {self.fund_code}")
        report.append("=" * 80)
        
        # 1. 持仓集中度
        report.append("\n【一、持仓集中度分析】")
        concentration = self.analyze_concentration()
        for q, data in concentration.items():
            report.append(f"{q}: 前十大合计 {data['total_ratio']:.2f}%，第一大 {data['top1_ratio']:.2f}%")
        
        # 2. 调仓分析
        report.append("\n【二、季度调仓分析】")
        turnover = self.analyze_turnover()
        for t in turnover:
            report.append(f"\n{t['from']} → {t['to']} ({t['intensity']}):")
            report.append(f"  新增: {t['new_count']}只 ({', '.join([s.name for s in t['new_stocks']])})")
            report.append(f"  退出: {t['removed_count']}只 ({', '.join([s.name for s in t['removed_stocks']])})")
        
        # 3. 稳定性
        report.append("\n【三、持仓稳定性分析】")
        stability = self.analyze_stability()
        for code, data in list(stability.items())[:15]:
            report.append(f"  {data['name']:<10} ({code}): {data['bar']} {data['count']}/8 - {data['level']}")
        
        # 4. 行业配置
        report.append("\n【四、行业配置演变】")
        themes = self.identify_theme_evolution()
        for t in themes:
            report.append(f"{t['quarter']}: {t['theme']} - {', '.join(t['industries'])}")
        
        # 5. 有效性评分
        report.append("\n【五、有效性评估】")
        scores = self.calculate_effectiveness_score()
        report.append(f"核心持仓持续性: {'⭐' * scores['core_holding_stability']}")
        report.append(f"换手率控制: {'⭐' * scores['turnover_control']}")
        report.append(f"风险控制: {'⭐' * scores['risk_control']}")
        report.append(f"综合评分: {'⭐' * int(scores['overall'])} ({scores['overall']}/5.0)")
        
        return "\n".join(report)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="基金诊断3.10 - 季报深度分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例: python fund_diagnosis.py 519702"
    )
    parser.add_argument("fund_code", help="基金代码，如 519702")
    
    args = parser.parse_args()
    
    diagnosis = FundDiagnosis(args.fund_code)
    
    if diagnosis.fetch_data():
        report = diagnosis.generate_report()
        print(report)
    else:
        print(f"获取基金 {args.fund_code} 数据失败")


if __name__ == "__main__":
    main()
