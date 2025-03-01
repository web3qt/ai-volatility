#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据获取模块 - 负责从CoinGecko API获取加密货币的历史价格数据
"""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from pycoingecko import CoinGeckoAPI
from tqdm import tqdm


class DataFetcher:
    """
    加密货币数据获取类
    负责从CoinGecko API获取指定token的历史价格数据
    """
    
    def __init__(self):
        """
        初始化数据获取器
        """
        self.cg = CoinGeckoAPI()
        self.supported_tokens = None
        
    def get_supported_tokens(self):
        """
        获取CoinGecko支持的所有加密货币列表
        
        Returns:
            dict: 代币ID到代币名称的映射
        """
        if self.supported_tokens is None:
            try:
                coins_list = self.cg.get_coins_list()
                self.supported_tokens = {coin['symbol'].upper(): coin['id'] for coin in coins_list}
            except Exception as e:
                print(f"获取支持的代币列表时出错: {e}")
                self.supported_tokens = {}
        
        return self.supported_tokens
    
    def get_token_id(self, symbol):
        """
        根据代币符号获取CoinGecko API中的代币ID
        
        Args:
            symbol (str): 代币符号，如'BTC'、'ETH'
            
        Returns:
            str: 代币ID，如果不支持则返回None
        """
        tokens = self.get_supported_tokens()
        symbol = symbol.upper()
        
        if symbol in tokens:
            return tokens[symbol]
        else:
            print(f"不支持的代币: {symbol}。请检查代币符号是否正确。")
            return None
    
    def get_historical_prices(self, token, days=30):
        """
        获取指定代币的历史价格数据
        
        Args:
            token (str): 代币符号或ID，如'BTC'、'ETH'
            days (int): 获取历史数据的天数，默认30天
            
        Returns:
            pandas.DataFrame: 包含时间戳、价格和交易量的数据框
        """
        try:
            # 获取代币ID
            if token.upper() in self.get_supported_tokens():
                token_id = self.get_token_id(token)
            else:
                token_id = token  # 如果已经是ID，则直接使用
            
            if token_id is None:
                return None
                
            # 从CoinGecko获取市场数据
            print(f"正在获取{token_id}的{days}天历史数据...")
            market_data = self.cg.get_coin_market_chart_by_id(
                id=token_id,
                vs_currency='usd',
                days=days
            )
            
            # 提取价格和交易量数据
            prices = market_data['prices']
            volumes = market_data['total_volumes']
            
            # 创建DataFrame
            df_prices = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df_volumes = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
            
            # 合并价格和交易量数据
            df = pd.merge(df_prices, df_volumes, on='timestamp')
            
            # 转换时间戳为日期时间
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # 按小时重采样数据
            df = df.resample('1H').mean()
            df.dropna(inplace=True)
            
            print(f"成功获取{token_id}的历史数据，共{len(df)}条记录")
            return df
            
        except Exception as e:
            print(f"获取历史价格数据时出错: {e}")
            return None
    
    def get_daily_returns(self, token, days=30):
        """
        计算指定代币的每日收益率
        
        Args:
            token (str): 代币符号，如'BTC'、'ETH'
            days (int): 获取历史数据的天数，默认30天
            
        Returns:
            pandas.Series: 每日收益率序列
        """
        df = self.get_historical_prices(token, days)
        if df is not None:
            # 计算对数收益率
            df['returns'] = df['price'].pct_change()
            df.dropna(inplace=True)
            return df['returns']
        return None


# 测试代码
if __name__ == "__main__":
    fetcher = DataFetcher()
    # 测试获取BTC的30天历史数据
    df = fetcher.get_historical_prices('BTC', 30)
    if df is not None:
        print(df.head())
        
    # 测试获取每日收益率
    returns = fetcher.get_daily_returns('ETH', 30)
    if returns is not None:
        print("每日收益率统计:")
        print(returns.describe())