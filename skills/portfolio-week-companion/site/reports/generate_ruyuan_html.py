# -*- coding: utf-8 -*-
"""生成睿远成长价值混合A的HTML周度回顾报告"""
import sys
sys.path.insert(0, r"D:/OPC-skill/skills/portfolio-week-companion/site/reports")
from generate_htmls import generate_fund_html

# 睿远成长价值混合A 完整数据
ruyuan_fund = {
    "name": "睿远成长价值混合A",
    "type": "混合型-偏股",
    "nav": 2.5020,
    "nav_date": "2026-07-10",
    "weekly_return": -3.22,
    "manager": "傅鹏博、朱璘",
    "scale": "165.00亿",
    "benchmark": "沪深300指数收益率×55% + 中证港股通综合指数(人民币)收益率×35% + 中证债券指数收益率×5% + 银行活期存款利率×5%",
    "holdings": [
        {"name": "宁德时代", "industry": "电力设备", "weight": "9.84%"},
        {"name": "中际旭创", "industry": "通信", "weight": "9.12%"},
        {"name": "新易盛", "industry": "通信", "weight": "9.45%"},
        {"name": "胜宏科技", "industry": "电子", "weight": "8.59%"},
        {"name": "东山精密", "industry": "电子", "weight": "9.72%"},
        {"name": "迈为股份", "industry": "电力设备", "weight": "7.39%"},
        {"name": "立讯精密", "industry": "电子", "weight": "7.19%"},
        {"name": "腾讯控股", "industry": "传媒", "weight": "7.15%"},
        {"name": "巨星科技", "industry": "机械设备", "weight": "3.62%"},
        {"name": "大族激光", "industry": "机械设备", "weight": "2.67%"},
    ],
    "nav_history": [
        {"date": "2019-03-26", "nav": 1.0000},
        {"date": "2020-03-26", "nav": 1.2075},
        {"date": "2021-01-22", "nav": 2.2720},
        {"date": "2022-03-26", "nav": 1.5760},
        {"date": "2023-03-26", "nav": 1.2610},
        {"date": "2024-03-26", "nav": 1.2800},
        {"date": "2025-03-26", "nav": 2.1100},
        {"date": "2026-03-26", "nav": 2.5000},
        {"date": "2026-07-01", "nav": 2.5850},
        {"date": "2026-07-10", "nav": 2.5020},
    ],
    "annual_returns": {
        "2019": "20.75%",
        "2020": "71.00%",
        "2021": "2.61%",
        "2022": "-30.70%",
        "2023": "-20.06%",
        "2024": "1.83%",
        "2025": "64.70%",
        "2026": "25.02%",
    }
}

OUTPUT_DIR = r"D:/OPC-skill/skills/portfolio-week-companion/site/reports"

if __name__ == '__main__':
    html = generate_fund_html(ruyuan_fund, "007119")
    output_path = f"{OUTPUT_DIR}/睿远成长价值混合A_周度回顾.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated: {output_path}")
