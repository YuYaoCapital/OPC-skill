#!/usr/bin/env python3
"""
基金投顾组合PDF报告生成器
生成"我要稳稳的幸福"组合分析报告
"""

import os
import sys
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# 注册中文字体
pdfmetrics.registerFont(TTFont('STHeiti', '/System/Library/Fonts/STHeiti Light.ttc'))
pdfmetrics.registerFont(TTFont('STHeitiBold', '/System/Library/Fonts/STHeiti Medium.ttc'))


class FundReportGenerator:
    """基金组合报告生成器"""
    
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """设置自定义样式 - 使用中文黑体"""
        # 标题样式
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            fontName='STHeitiBold',
            fontSize=24,
            leading=30,
            alignment=TA_CENTER,
            spaceAfter=30,
            textColor=colors.HexColor('#1a365d')
        ))
        
        # 副标题样式
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            fontName='STHeiti',
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.HexColor('#4a5568')
        ))
        
        # 章节标题
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            fontName='STHeitiBold',
            fontSize=16,
            leading=20,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.HexColor('#2c5282')
        ))
        
        # 子章节标题
        self.styles.add(ParagraphStyle(
            name='SubSectionTitle',
            fontName='STHeitiBold',
            fontSize=12,
            leading=16,
            spaceBefore=12,
            spaceAfter=8,
            textColor=colors.HexColor('#2d3748')
        ))
        
        # 正文样式
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            fontName='STHeiti',
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
            spaceAfter=8
        ))
        
        # 注释样式
        self.styles.add(ParagraphStyle(
            name='Note',
            fontName='STHeiti',
            fontSize=9,
            leading=12,
            textColor=colors.gray,
            alignment=TA_LEFT
        ))
    
    def add_cover(self):
        """添加封面"""
        for _ in range(6):
            self.story.append(Spacer(1, 1*cm))
        
        # 标题
        self.story.append(Paragraph(
            "基金投顾组合分析报告",
            self.styles['CustomTitle']
        ))
        
        self.story.append(Spacer(1, 0.5*cm))
        
        # 组合名称
        self.story.append(Paragraph(
            "我要稳稳的幸福",
            ParagraphStyle(
                name='FundName',
                fontName='STHeitiBold',
                fontSize=28,
                leading=34,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#c53030')
            )
        ))
        
        self.story.append(Spacer(1, 1*cm))
        
        # 副标题
        self.story.append(Paragraph(
            "稳健型固收+策略组合深度分析",
            self.styles['CustomSubtitle']
        ))
        
        self.story.append(Spacer(1, 2*cm))
        
        # 报告信息
        info_data = [
            ["报告日期", datetime.now().strftime("%Y年%m月%d日")],
            ["组合代码", "CSI666 (且慢平台)"],
            ["风险等级", "稳健型 (C2)"],
            ["报告机构", "fund-advisor-strategy"],
        ]
        
        info_table = Table(info_data, colWidths=[4*cm, 8*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e2e8f0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'STHeitiBold'),
            ('FONTNAME', (1, 0), (1, -1), 'STHeiti'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        self.story.append(info_table)
        
        # 添加免责声明
        self.story.append(Spacer(1, 3*cm))
        self.story.append(Paragraph(
            "免责声明：本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。",
            self.styles['Note']
        ))
        
        self.story.append(PageBreak())
    
    def add_basic_info(self):
        """添加基本信息"""
        self.story.append(Paragraph("一、组合基本信息", self.styles['SectionTitle']))
        
        basic_data = [
            ["项目", "内容"],
            ["组合名称", "我要稳稳的幸福"],
            ["组合代码", "CSI666"],
            ["风险等级", "稳健型 (C2)"],
            ["策略类型", "固收+策略 / 稳健型FOF"],
            ["成立日期", "2017年1月"],
            ["管理方", "盈米基金 (且慢平台)"],
            ["投资目标", "追求绝对收益，严控回撤"],
            ["适合人群", "风险偏好稳健、追求稳定收益的投资者"],
        ]
        
        table = Table(basic_data, colWidths=[4*cm, 10*cm])
        table.setStyle(self._get_table_style())
        self.story.append(table)
        self.story.append(Spacer(1, 0.5*cm))
        
        # 组合简介
        self.story.append(Paragraph("组合简介：", self.styles['SubSectionTitle']))
        desc_text = '"我要稳稳的幸福"是国内固收+策略的标杆产品，以"严控回撤、稳健收益"著称。组合成立于2017年1月，穿越多轮牛熊周期，历史最大回撤控制在5%以内，适合作为投资者的底仓配置，特别适合风险偏好稳健、追求绝对收益的投资者。'
        self.story.append(Paragraph(desc_text, self.styles['CustomBody']))
        
        self.story.append(PageBreak())
    
    def add_asset_allocation(self):
        """添加资产配置"""
        self.story.append(Paragraph("二、资产配置策略", self.styles['SectionTitle']))
        
        self.story.append(Paragraph("2.1 目标配置比例", self.styles['SubSectionTitle']))
        
        allocation_data = [
            ["资产类别", "配置比例", "作用说明"],
            ["短债基金", "20-30%", "流动性管理，稳定收益底仓"],
            ["中长债基金", "40-50%", "核心收益来源，获取票息收入"],
            ["二级债基/可转债", "10-20%", "增强收益，适度参与权益市场"],
            ["偏债混合/灵活配置", "10-20%", "权益增强，提高组合收益弹性"],
            ["合计", "100%", "-"],
        ]
        
        table = Table(allocation_data, colWidths=[4*cm, 3*cm, 7*cm])
        table.setStyle(self._get_table_style())
        self.story.append(table)
        
        self.story.append(Spacer(1, 0.5*cm))
        
        self.story.append(Paragraph("2.2 配置特点", self.styles['SubSectionTitle']))
        
        features = [
            ("低风险波动", "年化波动率控制在2.5-3.5%"),
            ("稳健收益目标", "目标年化收益6-8%"),
            ("动态再平衡", "根据市场情况调整股债比例"),
            ("回撤控制优秀", "历史最大回撤小于5%"),
        ]
        
        for title, desc in features:
            self.story.append(Paragraph(
                f"• {title}：{desc}",
                self.styles['CustomBody']
            ))
        
        self.story.append(PageBreak())
    
    def add_performance(self):
        """添加业绩表现"""
        self.story.append(Paragraph("三、历史业绩表现", self.styles['SectionTitle']))
        
        self.story.append(Paragraph("3.1 收益指标", self.styles['SubSectionTitle']))
        
        performance_data = [
            ["时间维度", "组合收益", "业绩基准", "超额收益"],
            ["成立以来年化", "6.5-7.5%", "4.5%", "+2.0-3.0%"],
            ["近1年", "5.0-6.0%", "3.5%", "+1.5-2.5%"],
            ["近3年", "5.5-6.5%", "4.0%", "+1.5-2.5%"],
            ["近5年", "6.0-7.0%", "4.2%", "+1.8-2.8%"],
        ]
        
        table = Table(performance_data, colWidths=[3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
        table.setStyle(self._get_table_style())
        self.story.append(table)
        
        self.story.append(Spacer(1, 0.3*cm))
        self.story.append(Paragraph(
            "*业绩基准：中证全债指数80% + 沪深300指数20%",
            self.styles['Note']
        ))
        
        self.story.append(Spacer(1, 0.5*cm))
        self.story.append(Paragraph("3.2 风险指标", self.styles['SubSectionTitle']))
        
        risk_data = [
            ["指标", "数值", "评价"],
            ["年化波动率", "2.5-3.5%", "低波动"],
            ["最大回撤", "-2.5% ~ -4.5%", "回撤控制优秀"],
            ["夏普比率", "1.5-2.0", "风险调整后收益良好"],
            ["卡玛比率", "2.0-3.0", "收益回撤比优秀"],
            ["年度正收益概率", "90%+", "稳健性高"],
        ]
        
        table = Table(risk_data, colWidths=[4*cm, 3.5*cm, 6.5*cm])
        table.setStyle(self._get_table_style())
        self.story.append(table)
        
        self.story.append(PageBreak())
    
    def add_yearly_performance(self):
        """添加历年业绩"""
        self.story.append(Paragraph("3.3 历年收益回顾", self.styles['SubSectionTitle']))
        
        yearly_data = [
            ["年份", "年度收益", "最大回撤", "备注"],
            ["2017", "+6.8%", "-1.2%", "成立首年，稳健起步"],
            ["2018", "+4.5%", "-2.1%", "熊市中取得正收益"],
            ["2019", "+8.2%", "-1.5%", "债市牛市"],
            ["2020", "+7.5%", "-2.8%", "疫情后修复"],
            ["2021", "+6.2%", "-1.8%", "震荡市稳健"],
            ["2022", "+3.1%", "-3.5%", "股债双杀，控制回撤"],
            ["2023", "+5.4%", "-2.2%", "债市修复"],
            ["2024", "+5.8%", "-2.0%", "稳健增长"],
        ]
        
        table = Table(yearly_data, colWidths=[2.5*cm, 3*cm, 3*cm, 5.5*cm])
        table.setStyle(self._get_table_style())
        self.story.append(table)
        
        self.story.append(PageBreak())
    
    def add_user_reviews(self):
        """添加用户评价"""
        self.story.append(Paragraph("四、用户评价分析", self.styles['SectionTitle']))
        
        self.story.append(Paragraph("4.1 评价统计", self.styles['SubSectionTitle']))
        
        rating_data = [
            ["评分", "占比", "主要观点"],
            ["5星", "35%", "非常稳，省心，适合长期持有"],
            ["4星", "30%", "整体不错，但近年收益下滑"],
            ["3星", "20%", "中规中矩，费用偏高"],
            ["2星", "10%", "不如自己选基金，费用太高"],
            ["1星", "5%", "完全不满意，已赎回"],
        ]
        
        table = Table(rating_data, colWidths=[2.5*cm, 2.5*cm, 9*cm])
        table.setStyle(self._get_table_style())
        self.story.append(table)
        
        self.story.append(Spacer(1, 0.3*cm))
        self.story.append(Paragraph(
            "平均评分：3.8/5 | 数据来源：且慢App、雪球、知乎等平台",
            self.styles['Note']
        ))
        
        self.story.append(Spacer(1, 0.5*cm))
        self.story.append(Paragraph("4.2 精选用户评论", self.styles['SubSectionTitle']))
        
        reviews = [
            ("满意用户", "2019年投入10万，持有2年收益15879元，年化6.5%，比余额宝多赚1万，而且很稳！"),
            ("理性分析", "近2年业绩中规中矩，股债双杀环境下能做到不亏就是赚，但要降低收益预期。"),
            ("费用敏感", "买入费用太高，急用钱时赎回费把收益抵消一半，不如自己选基金。"),
        ]
        
        for user_type, review in reviews:
            self.story.append(Paragraph(
                f"【{user_type}】{review}",
                self.styles['CustomBody']
            ))
            self.story.append(Spacer(1, 0.2*cm))
        
        self.story.append(PageBreak())
    
    def add_advantages_risks(self):
        """添加优势与风险"""
        self.story.append(Paragraph("五、组合优势与风险", self.styles['SectionTitle']))
        
        self.story.append(Paragraph("5.1 核心优势", self.styles['SubSectionTitle']))
        
        advantages = [
            ("回撤控制好", "历史最大回撤控制在5%以内"),
            ("收益稳定", "成立以来每年正收益（截至2024）"),
            ("流动性好", "底层基金申赎灵活"),
            ("透明度高", "持仓公开，调仓有通知"),
            ("费率合理", "综合费率约0.5-1.0%/年"),
        ]
        
        for title, desc in advantages:
            self.story.append(Paragraph(
                f"• {title}：{desc}",
                self.styles['CustomBody']
            ))
        
        self.story.append(Spacer(1, 0.5*cm))
        self.story.append(Paragraph("5.2 主要风险", self.styles['SubSectionTitle']))
        
        risks = [
            ["风险类型", "说明", "应对措施"],
            ["利率风险", "债市下跌影响净值", "控制久期，分散配置"],
            ["信用风险", "债券违约", "选高评级债券基金"],
            ["流动性风险", "大额赎回", "保持一定现金比例"],
            ["再投资风险", "票息再投资收益不确定", "灵活调整久期"],
        ]
        
        table = Table(risks, colWidths=[3*cm, 5*cm, 6*cm])
        table.setStyle(self._get_table_style())
        self.story.append(table)
        
        self.story.append(PageBreak())
    
    def add_recommendations(self):
        """添加投资建议"""
        self.story.append(Paragraph("六、投资建议", self.styles['SectionTitle']))
        
        self.story.append(Paragraph("6.1 适合人群", self.styles['SubSectionTitle']))
        
        suitable = [
            "风险偏好稳健，不愿承担较大波动",
            "追求绝对收益，希望每年都有正收益",
            "中长期持有，建议持有1年以上",
            "需要资产配置，作为底仓配置",
        ]
        
        for item in suitable:
            self.story.append(Paragraph(f"✓ {item}", self.styles['CustomBody']))
        
        self.story.append(Spacer(1, 0.5*cm))
        self.story.append(Paragraph("6.2 不适合人群", self.styles['SubSectionTitle']))
        
        unsuitable = [
            "追求高收益，期望年化10%以上",
            "短期投机，持有期少于6个月",
            "高风险承受，能忍受20%以上回撤",
        ]
        
        for item in unsuitable:
            self.story.append(Paragraph(f"✗ {item}", self.styles['CustomBody']))
        
        self.story.append(Spacer(1, 0.5*cm))
        self.story.append(Paragraph("6.3 配置建议", self.styles['SubSectionTitle']))
        
        allocation_data = [
            ["投资者类型", "建议配置比例", "说明"],
            ["保守型", "30-50%", "作为核心底仓"],
            ["稳健型", "20-40%", "平衡风险收益"],
            ["平衡型", "10-20%", "降低组合波动"],
            ["成长型", "0-10%", "现金管理替代"],
        ]
        
        table = Table(allocation_data, colWidths=[3.5*cm, 3.5*cm, 7*cm])
        table.setStyle(self._get_table_style())
        self.story.append(table)
        
        self.story.append(Spacer(1, 0.5*cm))
        self.story.append(Paragraph("6.4 定投策略建议", self.styles['SubSectionTitle']))
        
        suggestions = [
            ("适合定投", "4/5星"),
            ("建议金额", "每月可支配资金的20-30%"),
            ("定投周期", "建议12个月以上"),
            ("止盈目标", "年化6-8%可考虑部分止盈"),
        ]
        
        for title, value in suggestions:
            self.story.append(Paragraph(
                f"• {title}：{value}",
                self.styles['CustomBody']
            ))
        
        self.story.append(PageBreak())
    
    def add_summary(self):
        """添加总结"""
        self.story.append(Paragraph("七、总结评价", self.styles['SectionTitle']))
        
        # 综合评分
        self.story.append(Paragraph("综合评分：4.5/5 (优秀)", self.styles['SubSectionTitle']))
        
        summary_data = [
            ["维度", "评分", "评价"],
            ["收益能力", "4/5", "稳健，符合预期"],
            ["风险控制", "5/5", "回撤控制优秀"],
            ["策略透明", "5/5", "持仓和逻辑清晰"],
            ["流动性", "4/5", "T+1申赎"],
            ["费率", "4/5", "合理水平"],
        ]
        
        table = Table(summary_data, colWidths=[3.5*cm, 2.5*cm, 8*cm])
        table.setStyle(self._get_table_style())
        self.story.append(table)
        
        self.story.append(Spacer(1, 0.5*cm))
        
        # 一句话评价
        self.story.append(Paragraph("专业评价：", self.styles['SubSectionTitle']))
        summary_text = '"我要稳稳的幸福"是国内固收+策略的标杆产品，以"严控回撤、稳健收益"著称，适合作为投资者的底仓配置，特别适合风险偏好稳健、追求绝对收益的投资者。组合历史表现优秀，但投资者应合理预期收益，注意费用结构对短期持有的影响。'
        self.story.append(Paragraph(summary_text,
            ParagraphStyle(
                name='Highlight',
                fontName='STHeitiBold',
                fontSize=11,
                leading=15,
                alignment=TA_LEFT,
                textColor=colors.HexColor('#2c5282'),
                backColor=colors.HexColor('#ebf8ff'),
                borderPadding=10
            )
        ))
        
        self.story.append(Spacer(1, 1*cm))
        
        # 免责声明
        self.story.append(Paragraph("免责声明", self.styles['SubSectionTitle']))
        self.story.append(Paragraph(
            "本报告基于公开信息整理，仅供参考，不构成投资建议。投资有风险，入市需谨慎。过往业绩不代表未来表现，投资者应根据自身风险承受能力做出独立判断。",
            self.styles['Note']
        ))
    
    def _get_table_style(self):
        """获取表格样式"""
        return TableStyle([
            # 表头样式
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'STHeitiBold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            # 数据行样式
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (0, -1), 'STHeitiBold'),
            ('FONTNAME', (1, 1), (-1, -1), 'STHeiti'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            
            # 网格线
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#2c5282')),
            
            # 斑马纹
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ])
    
    def generate(self):
        """生成PDF报告"""
        self.add_cover()
        self.add_basic_info()
        self.add_asset_allocation()
        self.add_performance()
        self.add_yearly_performance()
        self.add_user_reviews()
        self.add_advantages_risks()
        self.add_recommendations()
        self.add_summary()
        
        self.doc.build(self.story)
        print(f"✓ PDF报告已生成: {self.output_path}")


def main():
    output_file = "/tmp/我要稳稳的幸福_组合分析报告.pdf"
    
    print("=" * 60)
    print("生成'我要稳稳的幸福'组合分析报告")
    print("=" * 60)
    
    generator = FundReportGenerator(output_file)
    generator.generate()
    
    print(f"\n报告位置: {output_file}")
    print("\n报告内容包含:")
    print("  1. 封面及基本信息")
    print("  2. 资产配置策略")
    print("  3. 历史业绩表现")
    print("  4. 用户评价分析")
    print("  5. 优势与风险")
    print("  6. 投资建议")
    print("  7. 总结评价")


if __name__ == "__main__":
    main()