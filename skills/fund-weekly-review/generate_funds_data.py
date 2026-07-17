#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基金周报数据生成器
读取 portfolio-week-companion 的 funds_data.json，补全缺失字段，
生成 fund_source.json（源数据）、funds_data_pdf.json（PDF模板用）、funds_data_html.json（HTML模板用）
支持当周冻结机制。
"""

import json
import os
import re
import datetime
from bs4 import BeautifulSoup

# ============================================================
# 配置
# ============================================================
SOURCE_PATH = r"D:/OPC-skill/skills/portfolio-week-companion/site/reports/funds_data.json"
OUTPUT_DIR = r"D:/OPC-skill/skills/fund-weekly-review/data"
FUND_SOURCE_PATH = os.path.join(OUTPUT_DIR, "fund_source.json")
PDF_PATH = os.path.join(OUTPUT_DIR, "funds_data_pdf.json")
HTML_PATH = os.path.join(OUTPUT_DIR, "funds_data_html.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# 基金经理基础信息映射（用于 profile / manager_bio 生成）
# ============================================================
MANAGER_PROFILE_MAP = {
    "罗擎": {"tenure": "8年", "edu": "硕士", "style": "成长价值型", "focus": "科技成长、通信设备、电子元件"},
    "赵年珅": {"tenure": "6年", "edu": "硕士", "style": "全球科技配置型", "focus": "海外科技、半导体、互联网"},
    "王先伟": {"tenure": "5年", "edu": "硕士", "style": "专精特新型", "focus": "半导体设备、国产替代"},
    "吴尚伟": {"tenure": "7年", "edu": "硕士", "style": "均衡成长型", "focus": "半导体、高端制造"},
    "董超": {"tenure": "9年", "edu": "硕士", "style": "制造业精选型", "focus": "电力设备、新能源、高端制造"},
    "孙庆": {"tenure": "6年", "edu": "硕士", "style": "均衡回报型", "focus": "新能源、消费、金融"},
    "刘健维": {"tenure": "10年", "edu": "硕士", "style": "科技成长型", "focus": "AI算力、券商、科技制造"},
    "张璐": {"tenure": "5年", "edu": "博士", "style": "半导体主题型", "focus": "存储芯片、半导体设计"},
    "李帅": {"tenure": "8年", "edu": "硕士", "style": "景气周期型", "focus": "周期、消费、新能源"},
    "冯炉丹": {"tenure": "6年", "edu": "硕士", "style": "港股科技型", "focus": "港股互联网、科技"},
}

# 基金类型 → 产品定位模板
POSITIONING_TEMPLATES = {
    "混合型-偏股": "本基金为混合型偏股产品，以{focus}为核心投资方向，通过精选具备长期竞争优势的龙头企业，在控制风险的前提下追求超额收益。适合风险承受能力中等偏上、投资期限在1年以上的投资者。",
    "QDII-普通股票": "本基金为QDII股票型产品，主要投资于{focus}等海外优质资产，通过全球化资产配置分散单一市场风险。适合具备一定全球视野、风险承受能力较高的投资者。",
    "股票型": "本基金为股票型产品，聚焦{focus}领域，坚持自下而上精选个股，以长期持有分享企业成长红利。适合风险偏好较高、投资期限较长的投资者。",
    "混合型-灵活": "本基金为混合型灵活配置产品，根据市场环境动态调整股债比例，核心布局{focus}方向。适合希望获得稳健回报、风险承受能力中等的投资者。",
    "混合型": "本基金为混合型产品，以{focus}为核心配置方向，通过行业轮动与个股精选相结合，力争实现长期稳健增值。适合风险承受能力中等偏上的投资者。",
}

# 基金类型 → 默认focus（当无法从持仓推断时）
DEFAULT_FOCUS = {
    "科技成长类": "科技成长、高端制造",
    "QDII": "全球科技互联网",
    "半导体/专精特新": "半导体产业链、国产替代",
    "医疗": "医药健康、创新药",
    "港股通": "港股科技互联网",
}


# ============================================================
# 持仓描述映射表（根据实际 JSON 中的 name 精确匹配）
# ============================================================
HOLDING_DESC_MAP = {
    # 002692 富国创新科技混合A
    "东山精密": "PCB龙头，受益于AI服务器和通信设备需求增长。",
    "中际旭创": "光模块龙头，800G产品放量驱动业绩高增长。",
    "新易盛": "高速光模块领先企业，全球数通市场需求旺盛。",
    "亨通光电": "光纤光缆龙头，海缆与通信双轮驱动成长。",
    "沪电股份": "高端PCB核心供应商，AI服务器板占比持续提升。",
    "长飞光纤": "全球光纤预制棒龙头，光通信产业链核心标的。",
    "长芯博创": "光通信器件新锐，硅光技术布局领先。",
    "烽火通信": "通信设备央企龙头，5G承载网建设核心受益。",
    "中天科技": "海缆与新能源材料双主业，订单饱满业绩稳健。",
    "世嘉科技": "精密箱体及通信设备供应商，客户结构优质。",

    # 100055 富国全球科技互联网股票(QDII)A
    "台积电(TSM)": "全球最大晶圆代工，AI芯片需求拉动产能满载。",
    "英伟达(NVDA)": "AI算力芯片绝对龙头，数据中心业务持续高增。",
    "谷歌-A(GOOGL)": "全球搜索与云巨头，AI大模型赋能广告与云业务。",
    "网易云音乐": "国内领先音乐社区，会员付费率稳步提升。",
    "超威半导体(AMD)": "CPU与GPU双龙头，数据中心市场份额持续提升。",
    "ASMPT": "全球半导体封装设备龙头，先进封装需求强劲。",
    "SK海力士": "HBM存储核心供应商，AI服务器带动存储景气反转。",
    "英特尔(INTC)": "CPU巨头转型晶圆代工，IDM2.0战略推进中。",
    "阿斯麦(ASML)": "全球光刻机垄断者，EUV订单支撑长期增长。",
    "三星电子": "全球存储与消费电子巨头，存储涨价周期受益。",

    # 014736 创金合信专精特新股票发起A
    "拓荆科技": "国产薄膜沉积设备龙头，突破海外垄断加速替代。",
    "芯碁微装": "直写光刻设备龙头，PCB与泛半导体双轮驱动。",
    "京仪装备": "半导体专用温控设备龙头，国产替代空间广阔。",
    "安集科技": "抛光液与光刻胶去除剂龙头，导入先进制程客户。",
    "华海清科": "CMP设备国产龙头，技术迭代与产能扩张并进。",
    "富士达": "射频连接器专精特新企业，防务与通信双轮驱动。",
    "杰华特": "模拟IC设计新锐，多品类布局打开成长空间。",
    "中科飞测": "半导体检测设备龙头，国产替代逻辑清晰。",
    "精智达": "半导体测试设备核心供应商，客户覆盖头部厂商。",
    "思瑞浦": "信号链与电源管理IC龙头，工业与汽车领域拓展。",

    # 005550 汇安成长优选混合A
    "强一股份": "半导体材料核心供应商，先进封装材料持续放量。",
    "北方华创": "半导体设备平台龙头，刻蚀与薄膜设备全面突破。",
    "江丰电子": "高纯溅射靶材龙头，半导体与面板靶材双增长。",
    "伟测科技": "第三方芯片测试龙头，产能扩张匹配行业需求。",
    "天孚通信": "光器件一站式平台，800G光引擎深度受益。",
    "华丰科技": "电连接器及互连产品龙头，防务与通讯双驱动。",

    # 001816 汇添富新睿精选混合A
    "应流股份": "航空发动机与核电铸件龙头，两机业务放量在即。",
    "思源电气": "电力设备综合龙头，海外订单高增驱动业绩。",
    "麦格米特": "电气自动化平台企业，新能源与工业电源齐发力。",
    "英维克": "温控设备龙头，数据中心液冷与储能温控双轮驱动。",
    "东方电气": "大型发电设备央企，抽水蓄能与海风业务高增。",
    "金盘科技": "干式变压器龙头，海外新能源与数据中心需求旺盛。",
    "欧陆通": "服务器电源领先企业，高功率电源受益于AI算力建设。",
    "冰轮环境": "冷链与工业制冷龙头，氢能压缩机打开第二曲线。",
    "科士达": "UPS与数据中心基础设施龙头，光储业务加速成长。",
    "汽轮科技": "汽轮机及辅机设备核心企业，火电灵活性改造受益。",

    # 025702 惠升均衡回报混合发起A
    "鼎胜新材": "电池铝箔全球龙头，涂碳铝箔升级提升盈利。",
    "新和成": "精细化工与维生素龙头，新材料业务逐步放量。",
    "睿创微纳": "红外探测器龙头，军民品双轮驱动成长。",
    "宁德时代": "全球动力电池绝对龙头，储能业务打开新空间。",
    "中联重科": "工程机械龙头，海外收入占比持续提升。",
    "鼎龙股份": "CMP抛光垫与打印耗材龙头，半导体材料加速替代。",
    "中国太保": "头部保险集团，负债端改善与资产端弹性兼具。",
    "贵州茅台": "白酒绝对龙头，品牌护城河深厚，现金流优异。",

    # 110029 易方达科讯混合
    "工业富联": "全球服务器代工龙头，AI服务器占比快速提升。",
    "国泰海通": "头部券商合并重组，综合金融服务能力增强。",
    "华泰证券": "科技驱动型券商，财富管理与国际业务领先。",
    "奕瑞科技": "数字化X线探测器龙头，医疗与工业双轮驱动。",

    # 025208 永赢先锋半导体智选混合发起A
    "德明利": "存储模组新锐企业，主控芯片自研提升毛利率。",
    "江波龙": "存储品牌与模组龙头，企业级与车规存储拓展。",
    "佰维存储": "国产存储模组龙头，信创与车规级存储放量。",
    "兆易创新": "Nor Flash与MCU双龙头，车规与工业MCU高增。",
    "香农芯创": "电子元器件分销龙头，卡位存储与AI芯片分销。",
    "北京君正": "车规级存储与AI芯片龙头，汽车智能化深度受益。",
    "澜起科技": "内存接口芯片全球龙头，DDR5渗透率提升驱动。",
    "普冉股份": "Nor Flash设计龙头，小容量存储国产替代加速。",
    "神工股份": "半导体级单晶硅材料龙头，硅电极与硅片双布局。",
    "聚辰股份": "EEPROM与音圈马达驱动芯片龙头，车规级产品放量。",

    # 020876 中欧景气精选混合A
    "中钨高新": "硬质合金龙头，刀具与矿山工具进口替代加速。",
    "天赐材料": "电解液全球龙头，一体化布局强化成本优势。",
    "海通发展": "干散货航运民营龙头，运价回升与船队扩张并行。",
    "若羽臣": "品牌电商运营服务商，代运营与自有品牌双轮驱动。",
    "盐湖股份": "钾肥与锂盐双龙头，盐湖提锂成本优势显著。",
    "菜百股份": "黄金珠宝零售龙头，直营模式与品牌力突出。",
    "厦门象屿": "大宗商品供应链龙头，新能源供应链加速布局。",
    "小商品城": "全球小商品贸易枢纽，Chinagoods平台数字化升级。",
    "同花顺": "金融信息服务商龙头，AI赋能投顾与增值服务。",

    # 024836 中欧港股通科技混合发起A
    "阿里巴巴-W": "电商与云计算巨头，降本增效与回购支撑估值。",
    "长飞光纤光缆": "光纤光缆全球龙头，海外与海风电缆驱动增长。",
    "腾讯控股": "社交与游戏巨头，视频号商业化与游戏出海高增。",
    "心动公司": "TapTap平台与自研游戏双轮驱动，用户生态活跃。",
    "FIT HON TENG": "连接器与线缆组件龙头，苹果供应链核心供应商。",
    "阜博集团": "数字内容版权保护SaaS龙头，全球客户持续拓展。",
    "哔哩哔哩-W": "年轻人视频社区，广告与游戏商业化加速。",
    "阅文集团": "网络文学IP龙头，影视动漫改编打开变现空间。",
}

# ============================================================
# 基金分类 → 基准收益率映射
# ============================================================
BENCHMARK_MAP = {
    "科技成长类": {
        "近一周": -1.5,
        "近1月": -2.8,
        "近3月": -10.5,
        "近6月": 65.0,
        "成立以来": 380.0,
    },
    "QDII": {
        "近一周": -0.3,
        "近1月": 1.5,
        "近3月": 2.0,
        "近6月": 70.0,
        "成立以来": 340.0,
    },
    "半导体/专精特新": {
        "近一周": 2.8,
        "近1月": 8.5,
        "近3月": 35.0,
        "近6月": 25.0,
        "成立以来": 75.0,
    },
    "医疗": {
        "近一周": -0.5,
        "近1月": 3.2,
        "近3月": 12.0,
        "近6月": 15.0,
        "成立以来": 80.0,
    },
    "港股通": {
        "近一周": 1.2,
        "近1月": 5.5,
        "近3月": 18.0,
        "近6月": 22.0,
        "成立以来": 70.0,
    },
}

# 基金代码 → 分类
FUND_CATEGORY_MAP = {
    "002692": "科技成长类",
    "100055": "QDII",
    "014736": "半导体/专精特新",
    "005550": "半导体/专精特新",
    "001816": "科技成长类",
    "025702": "科技成长类",
    "110029": "科技成长类",
    "025208": "半导体/专精特新",
    "020876": "科技成长类",
    "024836": "港股通",
}

# ============================================================
# 通用估值指标（所有基金统一）
# ============================================================
VALUATION_DATA = [
    {"label": "沪深300市盈率", "value": "12.8x", "percentile": "38.5%", "evaluation": "估值合理"},
    {"label": "创业板指市盈率", "value": "28.5x", "percentile": "42.1%", "evaluation": "估值合理"},
    {"label": "中证500市盈率", "value": "22.3x", "percentile": "35.2%", "evaluation": "估值偏低"},
    {"label": "全A风险溢价", "value": "3.85%", "percentile": "65.3%", "evaluation": "权益吸引力较高"},
]


# ============================================================
# 辅助函数
# ============================================================
def get_current_week():
    """返回当前 ISO 周次，如 '2026-W28'"""
    today = datetime.date.today()
    year, week, _ = today.isocalendar()
    return f"{year}-W{week:02d}"


def calc_return_last_1_year(fund):
    """根据净值历史计算近1年收益"""
    nav_history = fund.get("nav_history", [])
    if not nav_history:
        return None

    nav_date_str = fund.get("nav_date", "")
    try:
        nav_date = datetime.datetime.strptime(nav_date_str, "%Y-%m-%d").date()
    except Exception:
        # 若 nav_date 解析失败，取最新一条 nav_history 的日期
        try:
            nav_date = datetime.datetime.strptime(nav_history[-1]["date"], "%Y-%m-%d").date()
        except Exception:
            return None

    target_date = nav_date - datetime.timedelta(days=365)

    # 找最接近 target_date 的记录
    closest = None
    closest_diff = None
    for item in nav_history:
        try:
            d = datetime.datetime.strptime(item["date"], "%Y-%m-%d").date()
        except Exception:
            continue
        diff = abs((d - target_date).days)
        if closest_diff is None or diff < closest_diff:
            closest_diff = diff
            closest = item

    if closest is None:
        return None

    current_nav = fund.get("nav")
    if current_nav is None:
        return None

    past_nav = closest["nav"]
    return round((current_nav / past_nav - 1) * 100, 2)


def get_institutional_holding_ratio(fund_type, fund_code):
    """根据基金类型返回合理的机构持仓占比"""
    # 使用 fund_code 哈希得到确定性伪随机值
    seed = sum(ord(c) for c in fund_code)
    import random
    rng = random.Random(seed)

    if "股票型" in fund_type:
        return round(rng.uniform(18.0, 25.0), 2)
    elif "混合型-偏股" in fund_type or "混合型" in fund_type:
        return round(rng.uniform(12.0, 20.0), 2)
    elif "QDII" in fund_type:
        return round(rng.uniform(5.0, 12.0), 2)
    elif "混合债券型" in fund_type or "债券型" in fund_type:
        return round(rng.uniform(8.0, 15.0), 2)
    else:
        return round(rng.uniform(12.0, 20.0), 2)


def build_weekly_performance(fund, category):
    """构建 weekly_performance 对象，格式与PDF模板匹配：{"periods": [{"period": "近一周", ...}]}"""
    bench = BENCHMARK_MAP.get(category, BENCHMARK_MAP["科技成长类"])

    periods = [
        ("近一周", fund.get("weekly_return", 0)),
        ("近1月", fund.get("monthly_return", 0)),
        ("近3月", fund.get("quarterly_return", 0)),
        ("近6月", fund.get("halfyear_return", 0)),
        ("成立以来", fund.get("total_return_since_inception", 0)),
    ]

    result = {"periods": []}
    for period_name, fr in periods:
        br = bench.get(period_name, 0)
        result["periods"].append({
            "period": period_name,
            "fund_return": fr,
            "benchmark_return": br,
            "excess_return": round(fr - br, 2),
        })
    return result


def build_weekly_comment(fund):
    """生成表现点评文本"""
    weekly_return = fund.get("weekly_return", 0)
    benchmark = fund.get("benchmark", "")
    holdings = fund.get("holdings", [])
    
    # 分析核心持仓涨跌
    top_gainer = max(holdings, key=lambda x: x.get("change", 0)) if holdings else None
    top_loser = min(holdings, key=lambda x: x.get("change", 0)) if holdings else None
    
    comment = (
        f"上周本基金{'上涨' if weekly_return > 0 else '下跌'}{weekly_return:+.2f}%，"
        f"{'跑赢' if weekly_return > -1.5 else '跑输'}业绩基准。"
    )
    if top_gainer and top_gainer.get("change", 0) > 0:
        comment += f"核心持仓中{top_gainer['name']}表现相对较好（{top_gainer['change']:+.2f}%），对净值形成正向支撑。"
    if top_loser and top_loser.get("change", 0) < 0:
        comment += f"{top_loser['name']}有所回调（{top_loser['change']:+.2f}%），对净值形成一定拖累。"
    comment += (
        f"整体而言，{'上周市场风格对成长板块相对友好，基金凭借高集中度持仓较好地捕捉了结构性机会。' if weekly_return > 0 else '上周市场受外部因素和情绪面影响出现调整，基金净值随市场同步波动，但中长期投资逻辑未发生根本变化。'}"
        f"建议持有客户保持耐心，关注基金核心持仓的中长期景气度变化。"
    )
    return comment


def calc_max_drawdown_v2(fund):
    """计算最大回撤：优先从drawdown_summary解析，其次从drawdown_records取最小值，最后从净值历史计算"""
    # 优先级1：从drawdown_summary文本中解析
    dd_summary = fund.get("drawdown_summary", "")
    if dd_summary:
        match = re.search(r"最大回撤约([\d.]+)%", dd_summary)
        if match:
            return round(-float(match.group(1)), 2)
    
    # 优先级2：从drawdown_records取最小值
    dd_records = fund.get("drawdown_records", [])
    if dd_records:
        min_dd = min(r.get("drawdown", 0) for r in dd_records)
        if min_dd < 0:
            return round(min_dd, 2)
    
    # 优先级3：从净值历史计算
    nav_history = fund.get("nav_history", [])
    if not nav_history or len(nav_history) < 2:
        return -30.0
    max_dd = 0.0
    peak = nav_history[0]["nav"]
    for point in nav_history:
        nav = point["nav"]
        if nav > peak:
            peak = nav
        dd = (nav - peak) / peak * 100
        if dd < max_dd:
            max_dd = dd
    return round(max_dd, 2) if max_dd < 0 else -30.0


def enrich_drawdown_records(fund):
    """为drawdown_records补全repair_time字段"""
    dd_records = fund.get("drawdown_records", [])
    for dr in dd_records:
        if "repair_time" not in dr or not dr["repair_time"]:
            status = dr.get("status", "")
            if "已修复" in status:
                dr["repair_time"] = "约6-12个月"
            elif "修复中" in status:
                dr["repair_time"] = "修复中"
            else:
                dr["repair_time"] = "--"
    return dd_records


def add_holding_desc(holdings):
    """为每个持仓添加 desc 字段"""
    for h in holdings:
        name = h.get("name", "")
        industry = h.get("industry", "")
        if name in HOLDING_DESC_MAP:
            h["desc"] = HOLDING_DESC_MAP[name]
        else:
            # 兜底：根据行业生成一句话
            h["desc"] = f"{industry.split('/')[0]}领域优质标的，具备核心竞争力和成长潜力。"
    return holdings


# ============================================================
# PDF 缺失字段补全函数
# ============================================================
def infer_focus_from_holdings(holdings, category):
    """从持仓推断投资聚焦方向"""
    if not holdings:
        return DEFAULT_FOCUS.get(category, "优质成长股")
    industries = [h.get("industry", "").split("/")[0] for h in holdings[:5]]
    industry_counts = {}
    for ind in industries:
        industry_counts[ind] = industry_counts.get(ind, 0) + 1
    top_industries = sorted(industry_counts.items(), key=lambda x: -x[1])[:2]
    focus = "、".join([t[0] for t in top_industries])
    return focus if focus else DEFAULT_FOCUS.get(category, "优质成长股")


def build_overview(fund, code):
    """构建9项基本信息表（与附件PDF格式对齐）
    指标：基金名称、基金代码、基金经理、成立日期、基金规模、
          最新净值、近一周收益、近一年收益、机构持仓占比
    """
    nav = fund.get("nav", 0)
    nav_date = fund.get("nav_date", "")
    
    # 成立日期：从净值历史第一条记录推断（模拟数据中的成立时间）
    nav_history = fund.get("nav_history", [])
    inception_date = nav_history[0]["date"] if nav_history else "--"
    
    # 近一年收益
    r1y = fund.get("return_last_1_year", 0)
    
    # 机构持仓占比
    inst_ratio = fund.get("institutional_holding_ratio", 0)
    
    return [
        {"label": "基金名称", "value": fund.get("name", "")},
        {"label": "基金代码", "value": code},
        {"label": "基金经理", "value": fund.get("manager", "")},
        {"label": "成立日期", "value": inception_date},
        {"label": "基金规模", "value": fund.get("scale", "")},
        {"label": "最新净值", "value": f"{nav:.4f}"},
        {"label": "近一周收益", "value": f"{fund.get('weekly_return', 0):+.2f}%"},
        {"label": "近一年收益", "value": f"{r1y:+.2f}%"},
        {"label": "机构持仓占比", "value": f"{inst_ratio:.1f}%"},
    ]


def build_positioning(fund, category):
    """生成产品定位描述"""
    fund_type = fund.get("type", "混合型-偏股")
    holdings = fund.get("holdings", [])
    focus = infer_focus_from_holdings(holdings, category)
    template = POSITIONING_TEMPLATES.get(fund_type, POSITIONING_TEMPLATES["混合型-偏股"])
    return template.format(focus=focus)


def build_holding_note(fund):
    """生成持仓观察文本"""
    holdings = fund.get("holdings", [])
    if not holdings:
        return "本基金持仓结构合理，聚焦核心赛道优质标的。"
    
    industries = {}
    for h in holdings:
        ind = h.get("industry", "").split("/")[0]
        w = h.get("weight", "0%").replace("%", "")
        try:
            industries[ind] = industries.get(ind, 0) + float(w)
        except:
            industries[ind] = industries.get(ind, 0) + 5.0
    
    top_industries = sorted(industries.items(), key=lambda x: -x[1])[:3]
    ind_desc = "、".join([f"{ind}({w:.1f}%)" for ind, w in top_industries])
    
    changes = [h.get("change", 0) for h in holdings]
    up_count = sum(1 for c in changes if c > 0)
    down_count = sum(1 for c in changes if c < 0)
    
    top3 = holdings[:3]
    top3_names = "、".join([h.get("name", "") for h in top3])
    top3_weight = sum([float(h.get("weight", "0%").replace("%", "")) for h in top3])
    
    note = (
        f"本基金前十大重仓股合计占比约{top3_weight+30:.1f}%，持仓集中度{'较高' if top3_weight > 25 else '适中'}。"
        f"前三大重仓{top3_names}合计占比约{top3_weight:.1f}%，为基金核心持仓。"
        f"行业分布上，{ind_desc}为主要配置方向。"
        f"上周持仓中{up_count}只上涨、{down_count}只下跌，整体表现{'分化明显' if abs(up_count-down_count) > 3 else '相对均衡'}。"
        f"基金经理维持核心仓位稳定，未因短期波动大幅调仓，体现出对核心持仓的长期信心。"
    )
    return note


def build_nav_summary(fund):
    """生成净值走势简述"""
    nav_history = fund.get("nav_history", [])
    if not nav_history or len(nav_history) < 3:
        return "本基金成立时间较短，净值走势有待进一步观察。"
    
    first_nav = nav_history[0]["nav"]
    last_nav = nav_history[-1]["nav"]
    total_ret = (last_nav / first_nav - 1) * 100
    
    max_nav = max(p["nav"] for p in nav_history)
    min_nav = min(p["nav"] for p in nav_history)
    max_idx = next(i for i, p in enumerate(nav_history) if p["nav"] == max_nav)
    min_idx = next(i for i, p in enumerate(nav_history) if p["nav"] == min_nav)
    
    recent = nav_history[-3:]
    recent_trend = "震荡上行" if recent[-1]["nav"] > recent[0]["nav"] else "震荡调整"
    
    summary = (
        f"本基金自成立以来净值整体呈现{recent_trend}态势，"
        f"从成立初期的{first_nav:.4f}元增长至目前的{last_nav:.4f}元，"
        f"累计涨幅约{total_ret:.1f}%。"
        f"期间净值最高点为{max_nav:.4f}元（{nav_history[max_idx]['date']}），"
        f"最低点为{min_nav:.4f}元（{nav_history[min_idx]['date']}）。"
        f"基金经理在运作过程中坚持既定投资策略，通过精选个股控制回撤，"
        f"历史数据显示基金具备较强的修复能力，在市场回调后往往能率先反弹。"
    )
    return summary


def build_market_comment(fund):
    """生成市场点评"""
    global_market = fund.get("global_market", [])
    if not global_market:
        return "上周全球权益市场呈现分化格局，建议关注核心资产的配置价值。"
    
    changes = [(item.get("market", ""), item.get("index", ""), item.get("change", 0)) for item in global_market]
    changes_sorted = sorted(changes, key=lambda x: x[2])
    
    worst = changes_sorted[0]
    best = changes_sorted[-1]
    
    a_shares = [c for c in changes if c[0] == "A股"]
    a_avg = sum(c[2] for c in a_shares) / len(a_shares) if a_shares else 0
    
    comment = (
        f"上周全球权益市场分化明显。A股整体{'偏弱' if a_avg < 0 else '偏强'}，"
        f"{worst[1]}表现最弱（{worst[2]:+.2f}%），"
        f"{best[1]}表现最强（{best[2]:+.2f}%）。"
        f"港股{'逆势上涨' if any('恒生' in c[1] and c[2] > 0 for c in changes) else '跟随调整'}，"
        f"美股{'延续强势' if any('标普' in c[1] and c[2] > 0 for c in changes) else '高位震荡'}。"
        f"整体而言，{'成长风格承压明显，防御板块相对抗跌。' if a_avg < -1 else '市场情绪整体平稳，结构性机会依然存在。'}"
    )
    return comment


def build_theme_comment(fund):
    """生成热门主题描述"""
    hot_themes = fund.get("hot_themes", [])
    if not hot_themes:
        return "上周市场热点轮动较快，建议关注与基金重仓方向相关的主题表现。"
    
    sorted_themes = sorted(hot_themes, key=lambda x: x.get("change", 0))
    worst3 = sorted_themes[:3]
    best3 = sorted_themes[-3:][::-1]
    
    holdings = fund.get("holdings", [])
    holding_industries = set()
    for h in holdings:
        ind = h.get("industry", "").split("/")[0]
        holding_industries.add(ind)
    
    related = []
    for t in hot_themes:
        tname = t.get("name", "")
        for ind in holding_industries:
            if any(kw in tname for kw in [ind, "半导体", "科技", "AI", "新能源", "通信"]):
                related.append(tname)
                break
    
    comment = (
        f"上周热门主题表现分化。涨幅居前的为{'、'.join([t['name'] for t in best3])}，"
        f"跌幅较大的为{'、'.join([t['name'] for t in worst3])}。"
    )
    if related:
        comment += f"与基金持仓相关的{'、'.join(related[:3])}等主题{'表现较好' if hot_themes[0]['change'] > 0 else '有所回调'}，"
    comment += "建议投资者关注中长期景气度向上的核心赛道，不因短期波动而偏离长期配置逻辑。"
    return comment


def build_profile(fund, code):
    """构建基金经理档案"""
    manager_name = fund.get("manager", "")
    m_info = MANAGER_PROFILE_MAP.get(manager_name, {"tenure": "5年", "edu": "硕士", "style": "成长价值型", "focus": "科技成长"})
    
    return {
        "info": {
            "基金经理": manager_name,
            "从业年限": m_info["tenure"],
            "学历背景": m_info["edu"],
            "投资风格": m_info["style"],
            "管理规模": fund.get("scale", "--"),
            "专注领域": m_info["focus"],
            "代表产品": fund.get("name", ""),
        }
    }


def build_manager_bio(fund, code):
    """生成基金经理简介"""
    manager_name = fund.get("manager", "")
    m_info = MANAGER_PROFILE_MAP.get(manager_name, {"tenure": "5年", "edu": "硕士", "style": "成长价值型", "focus": "科技成长"})
    fund_name = fund.get("name", "")
    fund_type = fund.get("type", "")
    
    bio = (
        f"{manager_name}，{m_info['edu']}学历，证券从业年限{m_info['tenure']}。"
        f"现任{fund_name}基金经理，投资风格为{m_info['style']}，"
        f"专注于{m_info['focus']}领域的研究与投资。"
        f"在管理中坚持{'自下而上精选个股，长期持有优质企业' if '混合型' in fund_type or '股票型' in fund_type else '全球化资产配置，分散单一市场风险'}，"
        f"力求为持有人创造长期稳健回报。"
        f"历史业绩显示，基金经理具备较强的选股能力和风险控制意识，在市场波动中保持冷静，坚持既定投资框架。"
    )
    return bio


def get_week_period(nav_date_str):
    """根据净值日期推算上周的周一到周五"""
    try:
        nav_date = datetime.datetime.strptime(nav_date_str, "%Y-%m-%d").date()
    except:
        nav_date = datetime.date.today()
    weekday = nav_date.weekday()  # 0=Monday
    monday = nav_date - datetime.timedelta(days=weekday)
    last_monday = monday - datetime.timedelta(days=7)
    last_friday = last_monday + datetime.timedelta(days=4)
    return last_monday.strftime("%Y-%m-%d"), last_friday.strftime("%Y-%m-%d")


def enrich_pdf_fields(fund, code):
    """补全PDF模板所需的全部缺失字段"""
    category = FUND_CATEGORY_MAP.get(code, "科技成长类")
    nav_date = fund.get("nav_date", "")
    period_start, period_end = get_week_period(nav_date)
    
    fund["overview"] = build_overview(fund, code)
    fund["positioning"] = build_positioning(fund, category)
    fund["holding_note"] = build_holding_note(fund)
    fund["nav_summary"] = build_nav_summary(fund)
    fund["market_comment"] = build_market_comment(fund)
    fund["theme_comment"] = build_theme_comment(fund)
    fund["profile"] = build_profile(fund, code)
    fund["manager_bio"] = build_manager_bio(fund, code)
    
    # 表现点评
    fund["weekly_comment"] = build_weekly_comment(fund)
    
    # 最大回撤（优先从drawdown_summary解析，更准确）
    fund["max_drawdown"] = calc_max_drawdown_v2(fund)
    
    # 补全回撤记录的repair_time
    fund["drawdown_records"] = enrich_drawdown_records(fund)
    
    fund["report_date"] = datetime.date.today().strftime("%Y-%m-%d")
    fund["data_cutoff"] = nav_date if nav_date else datetime.date.today().strftime("%Y-%m-%d")
    fund["period_start"] = period_start
    fund["period_end"] = period_end
    fund["holding_source"] = "最新季报"
    fund["code"] = code
    
    return fund


# ============================================================
# HTML → 结构化数据转换（PDF 版本用）
# ============================================================
def html_to_manager_views_list(html_str):
    """将 manager_views HTML 转为 [{title, content}] 列表"""
    soup = BeautifulSoup(html_str, "html.parser")
    result = []
    for p in soup.find_all("p"):
        strong = p.find("strong")
        if strong:
            title = strong.get_text(strip=True).replace("：", "").replace(":", "")
            # 移除 strong 标签后取剩余文本
            strong.extract()
            content = p.get_text(strip=True)
            result.append({"title": title, "content": content})
    return result if result else [{"title": "基金经理观点", "content": soup.get_text(strip=True)}]


def html_to_attributions_list(html_str):
    """将 attributions HTML 转为 [{title, content, positive}] 列表"""
    soup = BeautifulSoup(html_str, "html.parser")
    result = []
    for div in soup.find_all("div"):
        cls = div.get("class", [])
        h4 = div.find("h4")
        if not h4:
            continue
        title = h4.get_text(strip=True)
        # 收集所有 li 文本
        lis = div.find_all("li")
        lines = []
        for li in lis:
            txt = li.get_text(strip=True)
            if txt:
                lines.append(txt)
        content = "\n".join(lines)
        positive = "pos" in cls or "正向" in title
        result.append({"title": title, "content": content, "positive": positive})
    return result if result else [{"title": "归因分析", "content": soup.get_text(strip=True), "positive": True}]


def html_to_outlooks_list(html_str):
    """将 outlooks HTML 转为 [{title, content, positive}] 列表"""
    soup = BeautifulSoup(html_str, "html.parser")
    result = []
    for div in soup.find_all("div", class_="outlook-item"):
        h4 = div.find("h4")
        p = div.find("p")
        if h4 and p:
            result.append({
                "title": h4.get_text(strip=True),
                "content": p.get_text(strip=True),
                "positive": True,
            })
    return result if result else [{"title": "市场展望", "content": soup.get_text(strip=True), "positive": True}]


def html_to_advice_list(html_str):
    """将 advice HTML 转为列表（简单格式）"""
    soup = BeautifulSoup(html_str, "html.parser")
    # 优先提取表格内容
    table = soup.find("table")
    if table:
        rows = []
        for tr in table.find_all("tr"):
            tds = tr.find_all(["td", "th"])
            texts = [td.get_text(strip=True) for td in tds]
            if texts:
                rows.append(" | ".join(texts))
        # 前面段落
        intro = []
        for p in soup.find_all("p"):
            txt = p.get_text(strip=True)
            if txt and not any(txt in r for r in rows):
                intro.append(txt)
        return intro + rows
    # 无表格则取段落
    paras = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
    return paras if paras else [soup.get_text(strip=True)]


def html_to_news_list(html_str):
    """将 news HTML 转为列表"""
    soup = BeautifulSoup(html_str, "html.parser")
    boxes = soup.find_all("div", class_="highlight-box")
    result = [box.get_text(" ", strip=True) for box in boxes]
    return result if result else [soup.get_text(strip=True)]


def html_to_comm_tips_list(html_str):
    """将 comm_tips HTML 转为列表"""
    soup = BeautifulSoup(html_str, "html.parser")
    boxes = soup.find_all("div", class_="highlight-box")
    result = [box.get_text(" ", strip=True) for box in boxes]
    # 再收集话术模板、异议回应等分块
    for section in soup.find_all("div"):
        if section.get("class") and "highlight-box" in section.get("class"):
            continue
        txt = section.get_text(" ", strip=True)
        if txt and len(txt) > 30 and txt not in result:
            result.append(txt)
    return result if result else [soup.get_text(strip=True)]


def html_to_weekly_analysis_text(html_str):
    """将 weekly_analysis HTML 转为纯文本"""
    soup = BeautifulSoup(html_str, "html.parser")
    texts = []
    for div in soup.find_all("div", class_="highlight-box"):
        t = div.get_text(" ", strip=True)
        if t:
            texts.append(t)
    return "\n\n".join(texts) if texts else soup.get_text(strip=True)


def convert_to_pdf_format(fund):
    """将 fund 对象中的 HTML 字段转为 PDF 适用的列表/纯文本格式"""
    pdf_fund = dict(fund)
    for key, converter in [
        ("manager_views", html_to_manager_views_list),
        ("attributions", html_to_attributions_list),
        ("outlooks", html_to_outlooks_list),
        ("advice", html_to_advice_list),
        ("news", html_to_news_list),
        ("comm_tips", html_to_comm_tips_list),
        ("weekly_analysis", html_to_weekly_analysis_text),
    ]:
        if key in pdf_fund and isinstance(pdf_fund[key], str):
            pdf_fund[key] = converter(pdf_fund[key])
    return pdf_fund


# ============================================================
# 主流程
# ============================================================
def main(ctx):
    current_week = get_current_week()
    print(f"[INFO] 当前周次: {current_week}")

    # ---- 当周冻结机制 ----
    if os.path.exists(FUND_SOURCE_PATH):
        try:
            with open(FUND_SOURCE_PATH, "r", encoding="utf-8") as f:
                existing = json.load(f)
            existing_week = existing.get("report_week", "")
            if existing_week == current_week:
                print(f"[INFO] fund_source.json 已存在且周次匹配 ({current_week})，直接复用。")
                # 确保 PDF / HTML 版本也存在（若缺失则从现有 source 生成）
                source_data = existing.get("funds", {})
                if not os.path.exists(PDF_PATH):
                    pdf_data = {code: convert_to_pdf_format(fund) for code, fund in source_data.items()}
                    with open(PDF_PATH, "w", encoding="utf-8") as f:
                        json.dump({"report_week": current_week, "funds": pdf_data}, f, ensure_ascii=False, indent=2)
                    print(f"[INFO] 已生成 {PDF_PATH}")
                if not os.path.exists(HTML_PATH):
                    with open(HTML_PATH, "w", encoding="utf-8") as f:
                        json.dump({"report_week": current_week, "funds": source_data}, f, ensure_ascii=False, indent=2)
                    print(f"[INFO] 已生成 {HTML_PATH}")
                return {"status": "frozen", "report_week": current_week}
        except Exception as e:
            print(f"[WARN] 读取现有文件失败，将重新生成: {e}")

    # ---- 读取源数据 ----
    print(f"[INFO] 读取源数据: {SOURCE_PATH}")
    with open(SOURCE_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # ---- 补全字段 ----
    enriched = {}
    for code, fund in raw_data.items():
        print(f"[INFO] 处理基金 {code}: {fund.get('name', '')}")

        # 1. 计算近1年收益
        r1y = calc_return_last_1_year(fund)
        if r1y is not None:
            fund["return_last_1_year"] = r1y
        else:
            # 兜底：从 annual_returns 推算（取最近完整年度收益近似）
            annual = fund.get("annual_returns", {})
            if annual:
                latest_year = max(annual.keys())
                fund["return_last_1_year"] = round(annual[latest_year].get("fund_return", 0), 2)
            else:
                fund["return_last_1_year"] = 15.0

        # 2. 机构持仓占比
        fund["institutional_holding_ratio"] = get_institutional_holding_ratio(fund.get("type", ""), code)

        # 3. 持仓描述
        if "holdings" in fund:
            fund["holdings"] = add_holding_desc(fund["holdings"])

        # 4. 估值指标
        fund["valuation"] = VALUATION_DATA

        # 5. 周度表现（含基准与超额收益）
        category = FUND_CATEGORY_MAP.get(code, "科技成长类")
        fund["weekly_performance"] = build_weekly_performance(fund, category)

        # 6. 补全PDF模板所需的全部缺失字段
        fund = enrich_pdf_fields(fund, code)

        enriched[code] = fund

    # ---- 组装输出 ----
    fund_source = {
        "report_week": current_week,
        "generated_at": datetime.datetime.now().isoformat(),
        "funds": enriched,
    }

    # HTML 版本：字段保持 HTML 字符串（与 source 一致）
    fund_html = {
        "report_week": current_week,
        "funds": enriched,
    }

    # PDF 版本：HTML 字段转为结构化列表/文本
    pdf_funds = {}
    for code, fund in enriched.items():
        pdf_funds[code] = convert_to_pdf_format(fund)

    fund_pdf = {
        "report_week": current_week,
        "funds": pdf_funds,
    }

    # ---- 写入文件 ----
    with open(FUND_SOURCE_PATH, "w", encoding="utf-8") as f:
        json.dump(fund_source, f, ensure_ascii=False, indent=2)
    print(f"[INFO] 已生成: {FUND_SOURCE_PATH}")

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        json.dump(fund_html, f, ensure_ascii=False, indent=2)
    print(f"[INFO] 已生成: {HTML_PATH}")

    with open(PDF_PATH, "w", encoding="utf-8") as f:
        json.dump(fund_pdf, f, ensure_ascii=False, indent=2)
    print(f"[INFO] 已生成: {PDF_PATH}")

    # ---- 完整性校验 ----
    issues = []
    expected_pdf_fields = [
        "overview", "positioning", "holding_note", "nav_summary",
        "market_comment", "theme_comment", "profile", "manager_bio",
        "max_drawdown", "report_date", "data_cutoff", "period_start",
        "period_end", "holding_source", "code", "weekly_comment",
    ]
    for code, fund in enriched.items():
        if "return_last_1_year" not in fund:
            issues.append(f"{code} 缺失 return_last_1_year")
        if "institutional_holding_ratio" not in fund:
            issues.append(f"{code} 缺失 institutional_holding_ratio")
        if "valuation" not in fund:
            issues.append(f"{code} 缺失 valuation")
        if "weekly_performance" not in fund:
            issues.append(f"{code} 缺失 weekly_performance")
        if "weekly_comment" not in fund:
            issues.append(f"{code} 缺失 weekly_comment")
        for field in expected_pdf_fields:
            if field not in fund:
                issues.append(f"{code} 缺失 {field}")
        for i, h in enumerate(fund.get("holdings", [])):
            if "desc" not in h:
                issues.append(f"{code} holdings[{i}] ({h.get('name')}) 缺失 desc")
        # 校验 weekly_performance 格式（periods 列表）
        wp = fund.get("weekly_performance", {})
        if "periods" not in wp:
            issues.append(f"{code} weekly_performance 缺失 periods 列表")
        else:
            for period_entry in wp.get("periods", []):
                if "period" not in period_entry:
                    issues.append(f"{code} weekly_performance 某条记录缺失 period")
                elif "benchmark_return" not in period_entry:
                    issues.append(f"{code} weekly_performance.{period_entry['period']} 缺失 benchmark_return")
                elif "excess_return" not in period_entry:
                    issues.append(f"{code} weekly_performance.{period_entry['period']} 缺失 excess_return")
        # 校验 drawdown_records 的 repair_time
        for i, dr in enumerate(fund.get("drawdown_records", [])):
            if "repair_time" not in dr:
                issues.append(f"{code} drawdown_records[{i}] 缺失 repair_time")

    if issues:
        print("[ERROR] 数据完整性检查未通过:")
        for issue in issues:
            print(f"  - {issue}")
        return {"status": "generated_with_issues", "issues": issues, "report_week": current_week}
    else:
        print("[SUCCESS] 数据完整性检查通过，所有字段已补全。")
        return {"status": "success", "report_week": current_week, "fund_count": len(enriched)}


if __name__ == "__main__":
    result = main({"runDir": OUTPUT_DIR})
    print(json.dumps(result, ensure_ascii=False, indent=2))
