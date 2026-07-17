# -*- coding: utf-8 -*-
"""
批量生成10只基金PDF报告
从 funds_data_pdf.json（已补全字段的PDF专用数据）中读取基金数据，逐个生成PDF
"""
import json, sys, os

sys.path.insert(0, r'D:/OPC-skill/skills/fund-weekly-review/templates')
from fund_weekly_pdf import generate_report

# 使用已补全字段的PDF专用数据（由 generate_funds_data.py 生成）
DATA_PATH = r"D:/OPC-skill/skills/fund-weekly-review/data/funds_data_pdf.json"
OUTPUT_DIR = r"D:/OPC-skill/skills/portfolio-week-companion/site/reports"

FUNDS_TO_GENERATE = [
    "002692", "100055", "014736", "005550", "001816",
    "025702", "110029", "025208", "020876", "024836"
]

def main():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # funds_data_pdf.json 格式: {"report_week": "...", "funds": {"002692": {...}}}
    all_funds = data.get("funds", data)
    
    for code in FUNDS_TO_GENERATE:
        if code not in all_funds:
            print(f"SKIP: {code} not found in data")
            continue
        
        fund = all_funds[code]
        fund['code'] = code  # 确保code字段存在
        
        output_name = fund['name'].replace(' ', '') + '_周度回顾.pdf'
        output_path = os.path.join(OUTPUT_DIR, output_name)
        chart_dir = os.path.join(OUTPUT_DIR, 'charts')
        
        print(f"Generating PDF: {code} {fund['name']} -> {output_path}")
        try:
            generate_report(fund, output_path, chart_dir)
            print(f"  OK: {output_path}")
        except Exception as e:
            import traceback
            print(f"  ERROR: {e}")
            traceback.print_exc()
    
    print("\nDone!")

if __name__ == '__main__':
    main()
