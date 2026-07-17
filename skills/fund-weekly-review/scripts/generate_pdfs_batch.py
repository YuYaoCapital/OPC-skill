# -*- coding: utf-8 -*-
"""
批量生成10只基金PDF报告
从funds_data.json中读取指定基金数据，逐个生成PDF
"""
import json, sys, os

sys.path.insert(0, r'D:/OPC-skill/skills/fund-weekly-review/templates')
from fund_weekly_pdf import generate_report

DATA_PATH = r"D:/OPC-skill/skills/portfolio-week-companion/site/reports/funds_data.json"
OUTPUT_DIR = r"D:/OPC-skill/skills/portfolio-week-companion/site/reports"

FUNDS_TO_GENERATE = [
    "002692", "100055", "014736", "005550", "001816",
    "025702", "110029", "025208", "020876", "024836"
]

def main():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        all_data = json.load(f)
    
    for code in FUNDS_TO_GENERATE:
        if code not in all_data:
            print(f"SKIP: {code} not found in data")
            continue
        
        fund = all_data[code]
        fund['code'] = code  # 确保code字段存在
        
        output_name = fund['name'].replace(' ', '') + '_周度回顾.pdf'
        output_path = os.path.join(OUTPUT_DIR, output_name)
        chart_dir = os.path.join(OUTPUT_DIR, 'charts')
        
        print(f"Generating PDF: {code} {fund['name']} -> {output_path}")
        try:
            generate_report(fund, output_path, chart_dir)
            print(f"  OK: {output_path}")
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print("\nDone!")

if __name__ == '__main__':
    main()
