#!/usr/bin/env python3
"""
基金组合调仓发车内容生成脚本

使用示例：
    python generate_launch_content.py --portfolio "稳稳的幸福" --style simple
    python generate_launch_content.py --portfolio "进取成长" --style professional --format graphic
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


def get_template_structure(style: str) -> dict:
    """获取不同风格的内容结构"""
    
    structures = {
        "professional": {
            "name": "专业严谨型",
            "sections": [
                "一、市场环境分析",
                "二、组合现状诊断", 
                "三、调仓逻辑阐述",
                "四、具体调仓方案",
                "五、调仓后组合特征",
                "六、风险提示与后续跟踪"
            ],
            "tone": "专业、数据驱动、逻辑严密",
            "audience": "有一定投资经验的投资者"
        },
        "simple": {
            "name": "通俗易懂型",
            "sections": [
                "为什么要调？",
                "具体怎么调？",
                "调完会怎样？",
                "操作建议",
                "风险提示"
            ],
            "tone": "口语化、用比喻解释、清单化",
            "audience": "普通投资者、理财新手"
        },
        "fun": {
            "name": "轻松幽默型",
            "sections": [
                "开场（制造氛围）",
                "正文（讲故事）",
                "调仓清单",
                "风险提示",
                "互动引导"
            ],
            "tone": "有趣、生动、用梗",
            "audience": "年轻用户、社交媒体用户"
        }
    }
    
    return structures.get(style, structures["simple"])


def generate_content_outline(portfolio_name: str, style: str, format_type: str) -> str:
    """生成内容大纲"""
    
    template = get_template_structure(style)
    current_date = datetime.now().strftime("%Y年%m月")
    
    outline = f"""
# {portfolio_name} 调仓发车内容大纲

## 基本信息
- **组合名称**: {portfolio_name}
- **内容风格**: {template['name']}
- **目标受众**: {template['audience']}
- **调仓时间**: {current_date}
- **输出格式**: {format_type}

## 内容结构

"""
    
    for i, section in enumerate(template['sections'], 1):
        outline += f"{i}. {section}\n"
    
    outline += f"""
## 风格特点
- **语气**: {template['tone']}

## 内容要点检查清单

### 调仓维度（需确认）
- [ ] 大类资产配置调整（股债比例）
- [ ] 行业/风格轮动调整
- [ ] 具体基金标的调整
- [ ] 仓位管理建议

### 必备元素
- [ ] 调仓理由（1-3条核心逻辑）
- [ ] 具体操作方案（清晰可执行）
- [ ] 风险提示
- [ ] 互动引导

### 优化建议
- [ ] 标题吸引人
- [ ] 开头有钩子
- [ ] 使用数据支撑
- [ ] 段落清晰易读
- [ ] 结尾有call to action

---
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    return outline


def generate_title_suggestions(portfolio_name: str) -> list:
    """生成标题建议"""
    
    templates = [
        "这次调仓，我加了X%的仓位",
        "{portfolio}调仓：卖出X只，买入X只",
        "X个信号告诉我，该调仓了",
        "这次调仓，可能会影响你下半年的收益",
        "市场震荡，{portfolio}这样调仓更稳健",
        "别人割肉，我们加仓：{portfolio}调仓思路",
        "{portfolio}发车啦！这次怎么调？一文看懂",
        "🚗 {portfolio}发车！这趟车开往'财富自由'站",
        "不调仓，可能会错过这波行情",
        "{portfolio}年度首次调仓，我做了X个调整"
    ]
    
    return [t.format(portfolio=portfolio_name) for t in templates]


def save_outline(outline: str, portfolio_name: str, output_dir: str = "."):
    """保存大纲到文件"""
    
    # 清理组合名称中的特殊字符
    safe_name = "".join(c for c in portfolio_name if c.isalnum() or c in (' ', '-', '_'))
    filename = f"{safe_name}_调仓大纲_{datetime.now().strftime('%Y%m%d')}.md"
    
    output_path = Path(output_dir) / filename
    output_path.write_text(outline, encoding='utf-8')
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="基金组合调仓发车内容生成工具"
    )
    parser.add_argument(
        "--portfolio", "-p",
        required=True,
        help="组合名称，如'稳稳的幸福'"
    )
    parser.add_argument(
        "--style", "-s",
        choices=["professional", "simple", "fun"],
        default="simple",
        help="内容风格: professional(专业)/simple(通俗)/fun(幽默)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "graphic", "poster", "all"],
        default="text",
        help="输出格式: text(文案)/graphic(图文)/poster(海报)/all(全部)"
    )
    parser.add_argument(
        "--output", "-o",
        default=".",
        help="输出目录"
    )
    
    args = parser.parse_args()
    
    # 生成大纲
    outline = generate_content_outline(
        args.portfolio, 
        args.style, 
        args.format
    )
    
    # 生成标题建议
    titles = generate_title_suggestions(args.portfolio)
    
    # 添加标题建议到大纲
    outline += "\n## 标题建议\n\n"
    for i, title in enumerate(titles[:5], 1):
        outline += f"{i}. {title}\n"
    
    # 保存文件
    output_path = save_outline(outline, args.portfolio, args.output)
    
    print(f"✅ 内容大纲已生成: {output_path}")
    print(f"\n📋 基本信息:")
    print(f"   组合名称: {args.portfolio}")
    print(f"   内容风格: {get_template_structure(args.style)['name']}")
    print(f"   输出格式: {args.format}")
    print(f"\n💡 使用建议:")
    print("   1. 根据大纲填充具体内容")
    print("   2. 参考SKILL.md中的模板和话术")
    print("   3. 确保包含所有必备元素")
    print("   4. 添加适当的数据支撑")


if __name__ == "__main__":
    main()
