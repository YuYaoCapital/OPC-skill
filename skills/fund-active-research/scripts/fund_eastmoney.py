#!/usr/bin/env python3
"""
东方财富基金数据抓取模块
数据来源：天天基金网 (fund.eastmoney.com)
"""

import requests
import pandas as pd
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time


class FundDataFetcher:
    """东方财富基金数据获取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://fund.eastmoney.com/'
        })
        self.base_url = 'https://fund.eastmoney.com'
        self.api_url = 'https://fundmobapi.eastmoney.com'
        
    def get_fund_info(self, fund_code: str) -> Dict:
        """
        获取基金基本信息
        
        Args:
            fund_code: 基金代码，如 '519702'
            
        Returns:
            基金基本信息字典
        """
        url = f'{self.base_url}/f10/F10DataApi.aspx?type=lsjz&code={fund_code}'
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 获取基金名称
            url_jzzzl = f'https://fundgz.1234567.com.cn/js/{fund_code}.js'
            resp_jzzzl = self.session.get(url_jzzzl, timeout=30)
            
            fund_name = ""
            if resp_jzzzl.status_code == 200:
                match = re.search(r'name":"([^"]+)"', resp_jzzzl.text)
                if match:
                    fund_name = match.group(1)
            
            # 获取详细F10信息
            url_f10 = f'{self.base_url}/f10/jbgk_{fund_code}.html'
            resp_f10 = self.session.get(url_f10, timeout=30)
            
            # 解析基础信息
            info = {
                'fund_code': fund_code,
                'fund_name': fund_name,
                'fund_type': '',
                'establish_date': '',
                'manage_scale': '',
                'company': '',
                'manager': '',
                'manager_date': '',
                'benchmark': '',
            }
            
            if resp_f10.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp_f10.text, 'html.parser')
                
                # 解析表格数据
                table = soup.find('table', {'class': 'info w790'})
                if table:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['th', 'td'])
                        for i in range(0, len(cells)-1, 2):
                            if i+1 < len(cells):
                                key = cells[i].text.strip()
                                value = cells[i+1].text.strip()
                                
                                if '基金类型' in key:
                                    info['fund_type'] = value
                                elif '成立日期' in key:
                                    info['establish_date'] = value
                                elif '资产规模' in key:
                                    info['manage_scale'] = value
                                elif '基金管理人' in key and '经理' not in key:
                                    info['company'] = value
                                elif '基金经理' in key and '人' not in key:
                                    info['manager'] = value
                                elif '管理费率' in key:
                                    info['manage_fee'] = value
                                elif '托管费率' in key:
                                    info['trustee_fee'] = value
            
            # 获取基金经理信息
            url_manager = f'{self.base_url}/f10/jjjl_{fund_code}.html'
            resp_manager = self.session.get(url_manager, timeout=30)
            
            if resp_manager.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp_manager.text, 'html.parser')
                
                # 尝试多种方式获取基金经理
                # 方式1: 从表格中获取（最新基金经理在第一行，结束日期为"至今"）
                manager_table = soup.find('table', {'class': 'w782'})
                if manager_table:
                    rows = manager_table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            # 第一列是起始日期，第二列是结束日期，第三列是基金经理
                            start_date = cells[0].text.strip()
                            end_date = cells[1].text.strip()
                            name_cell = cells[2]
                            
                            # 找当前在任的经理（结束日期为"至今"）
                            if end_date == '至今' or '至今' in end_date:
                                name_link = name_cell.find('a')
                                if name_link:
                                    info['current_manager'] = name_link.text.strip()
                                    info['manager_date'] = start_date
                                    break
                                elif name_cell.text.strip():
                                    info['current_manager'] = name_cell.text.strip()
                                    info['manager_date'] = start_date
                                    break
                
                # 方式2: 从简介区域获取
                if not info.get('current_manager'):
                    jl_intro = soup.find('div', {'class': 'jl_intro'})
                    if jl_intro:
                        name_a = jl_intro.find('a', {'class': 'fname'})
                        if name_a:
                            info['current_manager'] = name_a.text.strip()
                    
                # 方式3: 正则匹配
                if not info.get('current_manager'):
                    manager_match = re.search(r'基金经理[：:]\s*<a[^>]*>([^<]+)</a>', resp_manager.text)
                    if manager_match:
                        info['current_manager'] = manager_match.group(1).strip()
                
                # 获取任职日期（如果还没有）
                if not info.get('manager_date'):
                    date_match = re.search(r'任职日期[：:]\s*(\d{4}-\d{2}-\d{2})', resp_manager.text)
                    if date_match:
                        info['manager_date'] = date_match.group(1)
            
            return info
            
        except Exception as e:
            print(f"获取基金信息失败: {e}")
            return {'fund_code': fund_code, 'error': str(e)}
    
    def get_nav_history(self, fund_code: str, years: int = 3) -> pd.DataFrame:
        """
        获取历史净值数据
        
        Args:
            fund_code: 基金代码
            years: 获取年数，默认3年
            
        Returns:
            净值DataFrame，包含日期、单位净值、累计净值、日增长率
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365*years)
        
        all_data = []
        page = 1
        per_page = 100  # 每页条数
        max_pages = 50  # 最多获取50页，防止无限循环
        
        print(f"  开始获取净值数据: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
        
        while page <= max_pages:
            # 不带日期参数，获取全部数据，然后通过分页控制
            url = (f'{self.base_url}/f10/F10DataApi.aspx?type=lsjz&code={fund_code}'
                   f'&page={page}&per={per_page}')
            
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # 解析JSONP响应
                # 匹配 content:"..." 中的内容，结束标记是 ",records 或 ",pages 或 "}
                match = re.search(r'var apidata=\{\s*content:"(.+?)"(,records|,pages|,arryear|\}\})', response.text, re.DOTALL)
                if not match:
                    break
                    
                content = match.group(1)
                # HTML内容中可能有转义的引号
                content = content.replace('\\"', '"').replace('\\n', '').replace('\\t', '')
                
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                table = soup.find('table', {'class': 'w782'})
                
                if not table:
                    break
                    
                rows = table.find_all('tr')[1:]  # 跳过表头
                
                if not rows:
                    break
                    
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        try:
                            date_str = cells[0].text.strip()
                            nav_str = cells[1].text.strip()
                            accum_nav_str = cells[2].text.strip()
                            daily_return_str = cells[3].text.strip()
                            
                            all_data.append({
                                'date': date_str,
                                'nav': float(nav_str) if nav_str and nav_str != '--' else None,
                                'accum_nav': float(accum_nav_str) if accum_nav_str and accum_nav_str != '--' else None,
                                'daily_return': float(daily_return_str.replace('%', '')) 
                                if daily_return_str and daily_return_str not in ['--', ''] else None
                            })
                        except (ValueError, IndexError) as e:
                            continue
                
                # 检查是否还有更多数据（API每页实际返回约20条）
                if len(rows) < 10:  # 如果少于10条，说明是最后一页
                    break
                    
                page += 1
                time.sleep(0.3)  # 避免请求过快
                
            except Exception as e:
                print(f"获取净值数据失败 (page {page}): {e}")
                break
        
        df = pd.DataFrame(all_data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            # 过滤日期范围
            df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            df = df.sort_values('date').reset_index(drop=True)
            print(f"  成功获取 {len(df)} 条净值记录")
        
        return df
    
    def get_performance(self, fund_code: str, nav_df: pd.DataFrame = None) -> Dict:
        """
        获取业绩表现数据
        
        Args:
            fund_code: 基金代码
            nav_df: 净值DataFrame，如果提供则直接计算，否则尝试从API获取
            
        Returns:
            包含各周期收益率和排名的字典
        """
        # 如果有净值数据，直接计算业绩
        if nav_df is not None and not nav_df.empty:
            return self._calculate_performance_from_nav(nav_df)
        
        # 否则尝试从网络获取
        try:
            # 尝试从F10页面获取
            url = f'{self.base_url}/f10/jdzf_{fund_code}.html'
            response = self.session.get(url, timeout=30)
            
            performance = {
                'fund_code': fund_code,
                'last_month': {'return': None, 'rank': None},
                'last_3month': {'return': None, 'rank': None},
                'last_6month': {'return': None, 'rank': None},
                'last_year': {'return': None, 'rank': None},
                'last_2year': {'return': None, 'rank': None},
                'last_3year': {'return': None, 'rank': None},
                'last_5year': {'return': None, 'rank': None},
                'since_start': {'return': None, 'rank': None},
            }
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找业绩表格
                tables = soup.find_all('table', {'class': 'w782'})
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            period = cells[0].text.strip()
                            value = cells[1].text.strip().replace('%', '')
                            try:
                                ret = float(value)
                                if '近1月' in period or '近一月' in period:
                                    performance['last_month']['return'] = ret
                                elif '近3月' in period or '近三月' in period:
                                    performance['last_3month']['return'] = ret
                                elif '近6月' in period or '近六月' in period:
                                    performance['last_6month']['return'] = ret
                                elif '近1年' in period or '近一年' in period:
                                    performance['last_year']['return'] = ret
                                elif '近2年' in period:
                                    performance['last_2year']['return'] = ret
                                elif '近3年' in period:
                                    performance['last_3year']['return'] = ret
                                elif '近5年' in period:
                                    performance['last_5year']['return'] = ret
                                elif '成立来' in period:
                                    performance['since_start']['return'] = ret
                            except:
                                continue
            
            return performance
            
        except Exception as e:
            print(f"获取业绩数据失败: {e}")
            return {}
    
    def _calculate_performance_from_nav(self, nav_df: pd.DataFrame) -> Dict:
        """从净值数据计算各周期业绩"""
        nav_df = nav_df.copy()
        nav_df = nav_df.sort_values('date')
        
        def calc_return(days):
            if len(nav_df) < days + 1:
                return None
            end_nav = nav_df['nav'].iloc[-1]
            start_nav = nav_df['nav'].iloc[-(days+1)]
            return round((end_nav / start_nav - 1) * 100, 2)
        
        # 计算各周期收益（按交易日估算：月≈22天，季≈66天，年≈252天）
        performance = {
            'fund_code': '',
            'last_month': {'return': calc_return(22), 'rank': None},
            'last_3month': {'return': calc_return(66), 'rank': None},
            'last_6month': {'return': calc_return(126), 'rank': None},
            'last_year': {'return': calc_return(252), 'rank': None},
            'last_2year': {'return': calc_return(504), 'rank': None},
            'last_3year': {'return': calc_return(756), 'rank': None},
            'last_5year': {'return': calc_return(1260), 'rank': None},
            'since_start': {'return': round((nav_df['nav'].iloc[-1] / nav_df['nav'].iloc[0] - 1) * 100, 2), 'rank': None},
        }
        
        return performance
    
    def get_holdings(self, fund_code: str, year: int = None, quarter: int = None) -> pd.DataFrame:
        """
        获取基金持仓数据（十大重仓股）
        
        Args:
            fund_code: 基金代码
            year: 年份，默认最新
            quarter: 季度 1-4，默认最新
            
        Returns:
            持仓DataFrame
        """
        # 首先尝试从本地CSV文件读取
        import os
        csv_files = [
            f'{fund_code}_{year}{quarter}Q_holdings.csv' if year and quarter else None,
            f'/Users/r9/{fund_code}_20254Q_holdings.csv',
            f'{fund_code}_holdings.csv',
            f'{fund_code}_latest_holdings.csv',
        ]
        
        for csv_file in csv_files:
            if csv_file and os.path.exists(csv_file):
                try:
                    # 手动解析CSV（处理千分位逗号问题）
                    with open(csv_file, 'r', encoding='utf-8-sig') as f:
                        lines = f.readlines()
                    
                    data = []
                    for line in lines[1:]:  # 跳过表头
                        parts = line.strip().split(',')
                        
                        rank = parts[0]
                        code = parts[1]
                        name = parts[2]
                        ratio = parts[3]
                        remaining = parts[4:]
                        
                        # 智能分割持股数和持仓市值
                        best_split = None
                        max_market_value = 0
                        
                        for split_pos in range(1, len(remaining)):
                            shares_str = ','.join(remaining[:split_pos])
                            market_value_str = ','.join(remaining[split_pos:])
                            
                            try:
                                shares = float(shares_str.replace(',', ''))
                                market_value = float(market_value_str.replace(',', ''))
                                
                                if shares > 0 and market_value > shares:
                                    price = market_value / shares
                                    if 0.1 <= price <= 10000:
                                        if market_value > max_market_value:
                                            max_market_value = market_value
                                            best_split = (shares_str, market_value_str)
                            except:
                                continue
                        
                        if best_split:
                            shares, market_value = best_split
                        else:
                            shares = ','.join(remaining[:-1])
                            market_value = remaining[-1]
                        
                        data.append({
                            '排名': int(rank),
                            '股票代码': code,
                            '股票名称': name,
                            '占净值比': float(ratio.replace('%', '')),
                            '持股数(万股)': float(shares.replace(',', '')),
                            '持仓市值(万元)': float(market_value.replace(',', '')),
                        })
                    
                    df = pd.DataFrame(data)
                    
                    # 标准化列名
                    df = df.rename(columns={
                        '股票代码': 'stock_code',
                        '股票名称': 'stock_name',
                        '占净值比': 'ratio',
                        '持股数(万股)': 'shares',
                        '持仓市值(万元)': 'market_value',
                    })
                    
                    print(f"从本地文件加载持仓数据: {csv_file}")
                    return df
                except Exception as e:
                    print(f"读取本地持仓文件失败: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
        
        # 如果本地文件不存在，尝试从网络获取
        url = f'{self.base_url}/f10/FundArchivesDatas.aspx?type=jjcc&code={fund_code}'
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 解析JSON数据
            match = re.search(r'var apidata=\{\s*content:"(.+?)"(,records|,pages|,arryear|\}\})', response.text, re.DOTALL)
            if not match:
                return pd.DataFrame()
                
            content = match.group(1)
            content = content.replace('\\"', '"').replace('\\n', '').replace('\\t', '')
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # 找到最新的持仓表格
            boxes = soup.find_all('div', {'class': 'box'})
            
            holdings = []
            for box in boxes[:1]:  # 取最新的
                date_label = box.find('label', {'class': 'left'})
                report_date = date_label.text.strip() if date_label else ''
                
                table = box.find('table', {'class': 'w782'})
                if table:
                    rows = table.find_all('tr')[1:]  # 跳过表头
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 7:
                            try:
                                holdings.append({
                                    'report_date': report_date,
                                    'stock_code': cells[1].text.strip(),
                                    'stock_name': cells[2].text.strip(),
                                    'ratio': float(cells[6].text.strip().replace('%', '')) 
                                    if cells[6].text.strip() and cells[6].text.strip() != '--' else None,
                                    'shares': cells[4].text.strip(),
                                    'market_value': cells[5].text.strip(),
                                })
                            except (ValueError, IndexError):
                                continue
            
            return pd.DataFrame(holdings)
            
        except Exception as e:
            print(f"获取持仓数据失败: {e}")
            return pd.DataFrame()
    
    def get_asset_allocation(self, fund_code: str) -> Dict:
        """
        获取资产配置数据（股票/债券/现金占比）
        
        Returns:
            资产配置字典
        """
        url = f'{self.base_url}/f10/FundArchivesDatas.aspx?type=zcpz&code={fund_code}'
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            match = re.search(r'var apidata=\{\s*content:"(.+?)"(,records|,pages|,arryear|\}\})', response.text, re.DOTALL)
            if not match:
                return {}
                
            content = match.group(1)
            content = content.replace('\\"', '"').replace('\\n', '').replace('\\t', '')
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            table = soup.find('table', {'class': 'w782'})
            allocation = {}
            
            if table:
                rows = table.find_all('tr')[1:]  # 跳过表头
                
                for row in rows[:1]:  # 最新一期
                    cells = row.find_all('td')
                    if len(cells) >= 5:
                        allocation = {
                            'report_date': cells[0].text.strip(),
                            'stock_ratio': cells[1].text.strip(),
                            'bond_ratio': cells[2].text.strip(),
                            'cash_ratio': cells[3].text.strip(),
                            'other_ratio': cells[4].text.strip(),
                        }
            
            return allocation
            
        except Exception as e:
            print(f"获取资产配置失败: {e}")
            return {}
    
    def get_manager_info(self, manager_name: str) -> Dict:
        """
        获取基金经理详细信息
        
        Args:
            manager_name: 基金经理姓名
            
        Returns:
            基金经理信息
        """
        # 先搜索基金经理
        search_url = 'https://fundapi.eastmoney.com/fundtradenewapi/fund/FundMApi/GetFundList'
        params = {
            'keyword': manager_name,
            'pageindex': 1,
            'pagesize': 10
        }
        
        try:
            response = self.session.get(search_url, params=params, timeout=30)
            data = response.json()
            
            # 获取基金经理档案URL
            url_manager = f'{self.base_url}/manager/{manager_name}.html'
            resp = self.session.get(url_manager, timeout=30)
            
            info = {
                'name': manager_name,
                'company': '',
                'tenure': '',  # 从业年限
                'current_funds': [],  # 当前管理基金
                'total_scale': '',  # 管理总规模
            }
            
            if resp.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # 解析管理规模等
                info_div = soup.find('div', {'class': 'content_out'})
                if info_div:
                    # 从业年限
                    tenure_match = re.search(r'(\d+)年', info_div.text)
                    if tenure_match:
                        info['tenure'] = tenure_match.group(1) + '年'
            
            return info
            
        except Exception as e:
            print(f"获取基金经理信息失败: {e}")
            return {'name': manager_name}
    
    def calculate_risk_metrics(self, nav_df: pd.DataFrame) -> Dict:
        """
        计算风险指标
        
        Args:
            nav_df: 净值DataFrame
            
        Returns:
            风险指标字典
        """
        if nav_df.empty or len(nav_df) < 30:
            return {}
        
        # 计算日收益率
        nav_df = nav_df.copy()
        nav_df['daily_return'] = nav_df['nav'].pct_change() * 100
        
        returns = nav_df['daily_return'].dropna()
        
        # 年化波动率
        volatility = returns.std() * (252 ** 0.5)
        
        # 计算最大回撤
        nav_df['cummax'] = nav_df['nav'].cummax()
        nav_df['drawdown'] = (nav_df['nav'] - nav_df['cummax']) / nav_df['cummax'] * 100
        max_drawdown = nav_df['drawdown'].min()
        
        # 夏普比率（假设无风险利率2.5%）
        annual_return = (nav_df['nav'].iloc[-1] / nav_df['nav'].iloc[0]) ** (252 / len(nav_df)) - 1
        annual_return *= 100
        sharpe_ratio = (annual_return - 2.5) / volatility if volatility > 0 else 0
        
        # 卡玛比率
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        return {
            'annual_return': round(annual_return, 2),
            'volatility': round(volatility, 2),
            'max_drawdown': round(max_drawdown, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'calmar_ratio': round(calmar_ratio, 2),
        }
    
    def get_all_data(self, fund_code: str, years: int = 3) -> Dict:
        """
        获取基金所有数据（整合接口）
        
        Args:
            fund_code: 基金代码
            years: 历史数据年数
            
        Returns:
            包含所有数据的字典
        """
        print(f"正在获取基金 {fund_code} 的数据...")
        
        # 基础信息
        print("  → 获取基金基本信息...")
        fund_info = self.get_fund_info(fund_code)
        
        # 净值历史
        print("  → 获取净值历史...")
        nav_history = self.get_nav_history(fund_code, years)
        
        # 业绩表现
        print("  → 获取业绩数据...")
        performance = self.get_performance(fund_code, nav_history)
        
        # 持仓数据
        print("  → 获取持仓数据...")
        holdings = self.get_holdings(fund_code)
        
        # 资产配置
        print("  → 获取资产配置...")
        asset_allocation = self.get_asset_allocation(fund_code)
        
        # 风险指标
        print("  → 计算风险指标...")
        risk_metrics = self.calculate_risk_metrics(nav_history)
        
        # 基金经理信息
        manager_info = {}
        if fund_info.get('current_manager'):
            print(f"  → 获取基金经理 {fund_info['current_manager']} 信息...")
            manager_info = self.get_manager_info(fund_info['current_manager'])
        
        return {
            'fund_info': fund_info,
            'nav_history': nav_history,
            'performance': performance,
            'holdings': holdings,
            'asset_allocation': asset_allocation,
            'risk_metrics': risk_metrics,
            'manager_info': manager_info,
            'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


if __name__ == '__main__':
    # 测试代码
    fetcher = FundDataFetcher()
    
    # 测试获取数据
    fund_code = '519702'
    data = fetcher.get_all_data(fund_code)
    
    print("\n基金信息:")
    print(json.dumps(data['fund_info'], ensure_ascii=False, indent=2))
    
    print("\n风险指标:")
    print(json.dumps(data['risk_metrics'], ensure_ascii=False, indent=2))
