#!/usr/bin/env python3
"""
且慢MCP SSE客户端
通过MCP协议接入且慢基金投顾服务
"""

import json
import requests
import sseclient
from typing import Dict, List, Optional, Callable
from urllib.parse import urljoin


class QiemanMCPClient:
    """
    且慢MCP客户端 (SSE模式)
    
    通过Server-Sent Events协议与且慢MCP服务通信
    支持实时获取基金数据、组合分析、策略推荐等功能
    """
    
    def __init__(self, api_key: str, base_url: str = "https://stargate.yingmi.com/mcp"):
        """
        初始化MCP客户端
        
        Args:
            api_key: MCP API密钥
            base_url: MCP服务基础URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.sse_url = f"{self.base_url}/sse?apiKey={api_key}"
        self.message_url = None  # 从SSE连接中获取
        self.session = requests.Session()
        self.tools = []
        
    def connect(self) -> bool:
        """
        建立SSE连接并初始化
        
        Returns:
            是否连接成功
        """
        try:
            response = self.session.get(self.sse_url, stream=True, timeout=30)
            response.raise_for_status()
            
            client = sseclient.SSEClient(response)
            
            # 等待endpoint事件
            for event in client.events():
                data = json.loads(event.data)
                
                if event.event == "endpoint":
                    self.message_url = urljoin(self.base_url, data.get("endpoint", ""))
                    print(f"MCP连接成功: {self.message_url}")
                    
                elif event.event == "message":
                    if data.get("type") == "tools":
                        self.tools = data.get("tools", [])
                        print(f"可用工具: {len(self.tools)}个")
                        for tool in self.tools:
                            print(f"  - {tool.get('name')}: {tool.get('description', '')[:50]}...")
                        return True
                        
        except Exception as e:
            print(f"MCP连接失败: {e}")
            return False
        
        return False
    
    def call_tool(self, tool_name: str, params: Dict) -> Dict:
        """
        调用MCP工具
        
        Args:
            tool_name: 工具名称
            params: 工具参数
            
        Returns:
            工具执行结果
        """
        if not self.message_url:
            raise RuntimeError("MCP未连接，请先调用connect()")
        
        payload = {
            "type": "tool_call",
            "tool": tool_name,
            "params": params
        }
        
        try:
            response = self.session.post(
                self.message_url,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    # ========== 便捷方法 ==========
    
    def get_fund_info(self, fund_code: str) -> Dict:
        """获取基金信息"""
        return self.call_tool("get_fund_info", {"code": fund_code})
    
    def get_fund_nav(self, fund_code: str, limit: int = 252) -> Dict:
        """获取基金净值"""
        return self.call_tool("get_fund_nav", {
            "code": fund_code,
            "limit": limit
        })
    
    def search_funds(self, keyword: str, fund_type: str = None, limit: int = 20) -> Dict:
        """搜索基金"""
        params = {
            "keyword": keyword,
            "limit": limit
        }
        if fund_type:
            params["fund_type"] = fund_type
        return self.call_tool("search_funds", params)
    
    def analyze_portfolio(self, holdings: List[Dict]) -> Dict:
        """
        分析投资组合
        
        Args:
            holdings: [{"code": "000001", "weight": 0.3}, ...]
        """
        return self.call_tool("analyze_portfolio", {"holdings": holdings})
    
    def get_strategy_recommendation(self, risk_profile: str, amount: float) -> Dict:
        """
        获取策略推荐
        
        Args:
            risk_profile: conservative/moderate/balanced/growth/aggressive
            amount: 投资金额
        """
        return self.call_tool("get_strategy_recommendation", {
            "risk_profile": risk_profile,
            "amount": amount
        })
    
    def get_investment_plan(self, fund_codes: List[str], amount: float, frequency: str = "monthly") -> Dict:
        """
        生成定投计划
        
        Args:
            fund_codes: 基金代码列表
            amount: 每期金额
            frequency: weekly/monthly
        """
        return self.call_tool("get_investment_plan", {
            "fund_codes": fund_codes,
            "amount": amount,
            "frequency": frequency
        })
    
    def get_market_overview(self) -> Dict:
        """获取市场概览"""
        return self.call_tool("get_market_overview", {})
    
    def get_fund_performance(self, fund_code: str, period: str = "1y") -> Dict:
        """获取基金业绩"""
        return self.call_tool("get_fund_performance", {
            "code": fund_code,
            "period": period
        })


class QiemanMCPSimpleClient:
    """
    且慢MCP简化客户端 (HTTP模式)
    
    适用于不支持SSE的场景，通过标准HTTP POST调用
    """
    
    def __init__(self, api_key: str, base_url: str = "https://stargate.yingmi.com/mcp"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"  # 假设的REST端点
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def call(self, tool: str, params: Dict) -> Dict:
        """调用工具"""
        payload = {
            "tool": tool,
            "params": params
        }
        
        try:
            response = self.session.post(
                self.api_url,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}


def create_mcp_client(api_key: Optional[str] = None) -> QiemanMCPClient:
    """
    创建MCP客户端
    
    Args:
        api_key: API密钥，不传则从环境变量获取
        
    Returns:
        MCP客户端实例
    """
    import os
    
    if api_key is None:
        api_key = os.getenv("QIEMAN_MCP_API_KEY")
    
    if not api_key:
        raise ValueError("请提供api_key或设置 QIEMAN_MCP_API_KEY 环境变量")
    
    return QiemanMCPClient(api_key)


# ========== 使用示例 ==========

if __name__ == "__main__":
    print("=" * 60)
    print("且慢MCP SSE客户端")
    print("=" * 60)
    print("\n使用示例:")
    print("```python")
    print("from qieman_mcp_client import create_mcp_client")
    print("")
    print("# 创建客户端")
    print("client = create_mcp_client('your_api_key')")
    print("")
    print("# 连接MCP服务")
    print("if client.connect():")
    print("    # 获取基金信息")
    print("    info = client.get_fund_info('000001')")
    print("    print(info)")
    print("    ")
    print("    # 搜索基金")
    print("    funds = client.search_funds('沪深300', fund_type='index')")
    print("    print(funds)")
    print("    ")
    print("    # 分析组合")
    print("    holdings = [")
    print("        {'code': '000001', 'weight': 0.3},")
    print("        {'code': '110020', 'weight': 0.7}")
    print("    ]")
    print("    result = client.analyze_portfolio(holdings)")
    print("    print(result)")
    print("```")
    print("\n或直接运行测试:")
    print("  python qieman_mcp_client.py --test YOUR_API_KEY")