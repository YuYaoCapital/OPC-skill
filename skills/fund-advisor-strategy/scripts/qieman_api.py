#!/usr/bin/env python3
"""
且慢(盈米)API客户端
提供基金数据查询、持仓分析、策略推荐等功能
文档: https://www.yingmi.cn
"""

import requests
import json
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
import pandas as pd


class QiemanAPIClient:
    """且慢API客户端"""
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.qieman.com"):
        """
        初始化且慢API客户端
        
        Args:
            api_key: API密钥
            api_secret: API密钥密码
            base_url: API基础URL
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def _get_headers(self) -> Dict[str, str]:
        """构造请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-API-Secret": self.api_secret
        }
    
    def _request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法 (GET/POST)
            endpoint: API端点
            params: URL参数
            data: 请求体数据
            
        Returns:
            API响应数据
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, params=params, timeout=30)
            else:
                response = self.session.post(url, headers=headers, json=data, timeout=30)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "failed"}
    
    # ========== 基金数据接口 ==========
    
    def get_fund_info(self, fund_code: str) -> Dict:
        """
        获取基金基本信息
        
        Args:
            fund_code: 基金代码 (如: 000001)
            
        Returns:
            基金基本信息
        """
        return self._request("GET", "/v1/fund/info", {"code": fund_code})
    
    def get_fund_nav(self, fund_code: str, start_date: str = None, end_date: str = None, limit: int = 252) -> pd.DataFrame:
        """
        获取基金净值数据
        
        Args:
            fund_code: 基金代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            limit: 返回条数限制
            
        Returns:
            净值数据DataFrame (columns: date, nav, acc_nav)
        """
        params = {
            "code": fund_code,
            "limit": limit
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
            
        result = self._request("GET", "/v1/fund/nav", params)
        
        if "data" in result and result["data"]:
            df = pd.DataFrame(result["data"])
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)
            return df
        return pd.DataFrame()
    
    def get_fund_holding(self, fund_code: str, date: str = None) -> Dict:
        """
        获取基金持仓数据
        
        Args:
            fund_code: 基金代码
            date: 报告期日期 (YYYY-MM-DD)，不传则返回最新
            
        Returns:
            持仓数据
        """
        params = {"code": fund_code}
        if date:
            params["date"] = date
        return self._request("GET", "/v1/fund/holding", params)
    
    def search_funds(self, keyword: str, fund_type: str = None, limit: int = 20) -> List[Dict]:
        """
        搜索基金
        
        Args:
            keyword: 搜索关键词（基金名称/代码）
            fund_type: 基金类型筛选 (stock/bond/mixed/qdii/index)
            limit: 返回条数
            
        Returns:
            基金列表
        """
        params = {
            "keyword": keyword,
            "limit": limit
        }
        if fund_type:
            params["type"] = fund_type
            
        result = self._request("GET", "/v1/fund/search", params)
        return result.get("data", [])
    
    def get_fund_performance(self, fund_code: str, period: str = "1y") -> Dict:
        """
        获取基金业绩表现
        
        Args:
            fund_code: 基金代码
            period: 统计周期 (1m/3m/6m/1y/3y/5y/all)
            
        Returns:
            业绩数据 (收益率、波动率、夏普比率等)
        """
        return self._request("GET", "/v1/fund/performance", {
            "code": fund_code,
            "period": period
        })
    
    # ========== 组合分析接口 ==========
    
    def analyze_portfolio(self, holdings: List[Dict]) -> Dict:
        """
        分析投资组合
        
        Args:
            holdings: 持仓列表 [{"code": "000001", "weight": 0.3}, ...]
            
        Returns:
            组合分析结果
        """
        return self._request("POST", "/v1/portfolio/analyze", data={"holdings": holdings})
    
    def get_portfolio_risk(self, holdings: List[Dict]) -> Dict:
        """
        计算组合风险指标
        
        Args:
            holdings: 持仓列表
            
        Returns:
            风险指标 (波动率、最大回撤、VaR等)
        """
        return self._request("POST", "/v1/portfolio/risk", data={"holdings": holdings})
    
    def get_rebalance_suggestion(self, current: List[Dict], target: List[Dict]) -> Dict:
        """
        获取再平衡建议
        
        Args:
            current: 当前持仓 [{"code": "000001", "weight": 0.25}, ...]
            target: 目标持仓 [{"code": "000001", "weight": 0.30}, ...]
            
        Returns:
            再平衡建议
        """
        return self._request("POST", "/v1/portfolio/rebalance", data={
            "current": current,
            "target": target
        })
    
    # ========== 智能投顾接口 ==========
    
    def get_strategy_recommendation(self, risk_profile: str, amount: float, horizon: str = "long") -> Dict:
        """
        获取策略推荐
        
        Args:
            risk_profile: 风险偏好 (conservative/moderate/balanced/growth/aggressive)
            amount: 投资金额
            horizon: 投资期限 (short/medium/long)
            
        Returns:
            推荐策略
        """
        return self._request("POST", "/v1/strategy/recommend", data={
            "risk_profile": risk_profile,
            "amount": amount,
            "horizon": horizon
        })
    
    def get_investment_plan(self, fund_codes: List[str], amount: float, frequency: str = "monthly") -> Dict:
        """
        生成定投计划
        
        Args:
            fund_codes: 基金代码列表
            amount: 每期金额
            frequency: 定投频率 (weekly/monthly)
            
        Returns:
            定投计划
        """
        return self._request("POST", "/v1/plan/investment", data={
            "funds": fund_codes,
            "amount": amount,
            "frequency": frequency
        })
    
    # ========== 市场数据接口 ==========
    
    def get_market_overview(self) -> Dict:
        """获取市场概览数据"""
        return self._request("GET", "/v1/market/overview")
    
    def get_sector_performance(self, sector: str = None) -> List[Dict]:
        """
        获取行业/板块表现
        
        Args:
            sector: 行业代码，不传返回全部
            
        Returns:
            行业表现列表
        """
        params = {}
        if sector:
            params["sector"] = sector
        result = self._request("GET", "/v1/market/sector", params)
        return result.get("data", [])
    
    def get_macro_indicators(self) -> Dict:
        """获取宏观经济指标"""
        return self._request("GET", "/v1/market/macro")


class QiemanDataCache:
    """且慢数据缓存管理器"""
    
    def __init__(self, cache_dir: str = ".qieman_cache"):
        """
        初始化缓存
        
        Args:
            cache_dir: 缓存目录
        """
        self.cache_dir = cache_dir
        import os
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> str:
        """获取缓存文件路径"""
        import hashlib
        filename = hashlib.md5(key.encode()).hexdigest() + ".json"
        import os
        return os.path.join(self.cache_dir, filename)
    
    def get(self, key: str, max_age_hours: int = 24) -> Optional[Dict]:
        """
        获取缓存数据
        
        Args:
            key: 缓存键
            max_age_hours: 最大缓存时间(小时)
            
        Returns:
            缓存数据或None
        """
        import os
        path = self._get_cache_path(key)
        if not os.path.exists(path):
            return None
        
        # 检查是否过期
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        if datetime.now() - mtime > timedelta(hours=max_age_hours):
            return None
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def set(self, key: str, data: Dict):
        """
        设置缓存数据
        
        Args:
            key: 缓存键
            data: 缓存数据
        """
        path = self._get_cache_path(key)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, default=str)
    
    def clear(self):
        """清空缓存"""
        import os
        import glob
        for f in glob.glob(os.path.join(self.cache_dir, "*.json")):
            os.remove(f)


# ========== 便捷函数 ==========

def create_client_from_env() -> QiemanAPIClient:
    """从环境变量创建客户端"""
    import os
    api_key = os.getenv("QIEMAN_API_KEY")
    api_secret = os.getenv("QIEMAN_API_SECRET")
    base_url = os.getenv("QIEMAN_BASE_URL", "https://api.qieman.com")
    
    if not api_key or not api_secret:
        raise ValueError("请设置 QIEMAN_API_KEY 和 QIEMAN_API_SECRET 环境变量")
    
    return QiemanAPIClient(api_key, api_secret, base_url)


def fetch_fund_nav_series(client: QiemanAPIClient, fund_code: str, days: int = 365) -> pd.Series:
    """
    获取基金净值序列
    
    Args:
        client: 且慢API客户端
        fund_code: 基金代码
        days: 获取天数
        
    Returns:
        净值序列 (index: date, values: nav)
    """
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    df = client.get_fund_nav(fund_code, start_date=start_date, end_date=end_date)
    
    if df.empty:
        return pd.Series(dtype=float)
    
    return df["nav"]


def batch_fetch_funds(client: QiemanAPIClient, fund_codes: List[str]) -> Dict[str, pd.Series]:
    """
    批量获取多只基金净值
    
    Args:
        client: 且慢API客户端
        fund_codes: 基金代码列表
        
    Returns:
        基金净值字典 {code: nav_series}
    """
    result = {}
    for code in fund_codes:
        nav = fetch_fund_nav_series(client, code)
        if not nav.empty:
            result[code] = nav
    return result


if __name__ == "__main__":
    print("且慢(盈米)API客户端")
    print("\n使用示例:")
    print("```python")
    print("from qieman_api import QiemanAPIClient, create_client_from_env")
    print("")
    print("# 方式1: 直接创建")
    print("client = QiemanAPIClient('your_api_key', 'your_api_secret')")
    print("")
    print("# 方式2: 从环境变量创建")
    print("# export QIEMAN_API_KEY=your_key")
    print("# export QIEMAN_API_SECRET=your_secret")
    print("client = create_client_from_env()")
    print("")
    print("# 获取基金信息")
    print("info = client.get_fund_info('000001')")
    print("")
    print("# 获取净值数据")
    print("nav_df = client.get_fund_nav('000001', limit=252)")
    print("")
    print("# 搜索基金")
    print("funds = client.search_funds('沪深300', fund_type='index')")
    print("```")
    print("\n注意: 使用前请先联系且慢/盈米申请API密钥")