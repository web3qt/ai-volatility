#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据可视化模块 - 负责绘制波动率趋势图和其他相关图表
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.dates import DateFormatter


class VolatilityVisualizer:
    """
    波动率可视化类
    负责绘制波动率趋势图和其他相关图表
    """
    
    def __init__(self, style='darkgrid'):
        """
        初始化可视化器
        
        Args:
            style (str): seaborn绘图风格，默认为'darkgrid'
        """
        sns.set_style(style)
        # 设置中文字体，按优先级尝试不同字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'Heiti SC', 'Arial Unicode MS', 'DejaVu Sans']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        
    def plot_price_history(self, price_data, token_symbol, figsize=(12, 6)):
        """
        绘制价格历史走势图
        
        Args:
            price_data (pandas.DataFrame): 包含价格数据的DataFrame
            token_symbol (str): 代币符号
            figsize (tuple): 图形大小
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.plot(price_data.index, price_data['price'], linewidth=2)
        ax.set_title(f'{token_symbol}价格走势图', fontsize=15)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('价格 (USD)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # 格式化日期
        date_format = DateFormatter('%Y-%m-%d')
        ax.xaxis.set_major_formatter(date_format)
        fig.autofmt_xdate()
        
        plt.tight_layout()
        return fig
    
    def plot_volatility_trend(self, volatility_series, token_symbol, figsize=(12, 6)):
        """
        绘制波动率趋势图
        
        Args:
            volatility_series (pandas.Series): 波动率序列
            token_symbol (str): 代币符号
            figsize (tuple): 图形大小
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.plot(volatility_series.index, volatility_series, linewidth=2, color='orange')
        ax.set_title(f'{token_symbol}波动率趋势图', fontsize=15)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('波动率', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # 添加移动平均线
        if len(volatility_series) > 7:
            ma7 = volatility_series.rolling(window=7).mean()
            ax.plot(ma7.index, ma7, linewidth=1.5, linestyle='--', color='red', label='7日移动平均')
            ax.legend()
        
        # 格式化日期
        date_format = DateFormatter('%Y-%m-%d')
        ax.xaxis.set_major_formatter(date_format)
        fig.autofmt_xdate()
        
        plt.tight_layout()
        return fig
    
    def plot_volatility(self, volatility_series, token_symbol, figsize=(12, 6)):
        """
        绘制波动率图
        
        Args:
            volatility_series (pandas.Series): 波动率序列
            token_symbol (str): 代币符号
            figsize (tuple): 图形大小
        """
        plt.figure(figsize=figsize)
        plt.plot(volatility_series.index, volatility_series * 100, linewidth=2, color='orange')
        plt.title(f'{token_symbol}波动率', fontsize=15)
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('波动率 (%)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        return plt
    
    def plot_returns(self, returns, token_symbol, figsize=(12, 6)):
        """
        绘制收益率时间序列图
        
        Args:
            returns (pandas.Series): 收益率序列
            token_symbol (str): 代币符号
            figsize (tuple): 图形大小
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.plot(returns.index, returns, linewidth=1, color='blue')
        ax.set_title(f'{token_symbol}收益率时间序列', fontsize=15)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('收益率', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # 格式化日期
        date_format = DateFormatter('%Y-%m-%d')
        ax.xaxis.set_major_formatter(date_format)
        fig.autofmt_xdate()
        
        plt.tight_layout()
        return fig
    
    def plot_returns_distribution(self, returns, token_symbol, figsize=(12, 6)):
        """
        绘制收益率分布图
        
        Args:
            returns (pandas.Series): 收益率序列
            token_symbol (str): 代币符号
            figsize (tuple): 图形大小
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        sns.histplot(returns, kde=True, ax=ax)
        ax.set_title(f'{token_symbol}收益率分布', fontsize=15)
        ax.set_xlabel('收益率', fontsize=12)
        ax.set_ylabel('频率', fontsize=12)
        
        # 添加正态分布拟合曲线
        x = np.linspace(returns.min(), returns.max(), 100)
        mean = returns.mean()
        std = returns.std()
        y = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std) ** 2)
        ax.plot(x, y * len(returns) * (returns.max() - returns.min()) / 10, 
                linewidth=2, color='red', label='正态分布拟合')
        ax.legend()
        
        plt.tight_layout()
        return fig
    
    def plot_volatility_comparison(self, volatility_dict, figsize=(12, 6)):
        """
        绘制多个代币的波动率比较图
        
        Args:
            volatility_dict (dict): 代币符号到波动率序列的映射
            figsize (tuple): 图形大小
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        for token, vol_series in volatility_dict.items():
            ax.plot(vol_series.index, vol_series, linewidth=2, label=token)
        
        ax.set_title('代币波动率比较', fontsize=15)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('波动率', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # 格式化日期
        date_format = DateFormatter('%Y-%m-%d')
        ax.xaxis.set_major_formatter(date_format)
        fig.autofmt_xdate()
        
        plt.tight_layout()
        return fig
    
    def plot_risk_heatmap(self, correlation_matrix, figsize=(10, 8)):
        """
        绘制风险热力图（相关性矩阵）
        
        Args:
            correlation_matrix (pandas.DataFrame): 相关性矩阵
            figsize (tuple): 图形大小
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        cmap = sns.diverging_palette(230, 20, as_cmap=True)
        
        sns.heatmap(correlation_matrix, mask=mask, cmap=cmap, vmax=1, vmin=-1, center=0,
                    annot=True, fmt='.2f', square=True, linewidths=.5, ax=ax)
        
        ax.set_title('代币收益率相关性热力图', fontsize=15)
        
        plt.tight_layout()
        return fig
    
    def save_figure(self, fig, filename):
        """
        保存图形到文件
        
        Args:
            fig (matplotlib.figure.Figure): 图形对象
            filename (str): 文件名
        """
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"图形已保存至: {filename}")


# 测试代码
if __name__ == "__main__":
    # 创建一些模拟数据
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    # 模拟价格数据
    price = 100 + np.cumsum(np.random.normal(0, 1, 100))
    price_data = pd.DataFrame({'price': price}, index=dates)
    
    # 模拟收益率数据
    returns = pd.Series(np.random.normal(0, 0.02, 100), index=dates)
    
    # 模拟波动率数据
    volatility = pd.Series(0.05 + 0.03 * np.sin(np.linspace(0, 4*np.pi, 100)), index=dates)
    
    # 初始化可视化器
    visualizer = VolatilityVisualizer()
    
    # 测试绘图功能
    fig1 = visualizer.plot_price_history(price_data, 'BTC')
    fig2 = visualizer.plot_volatility_trend(volatility, 'BTC')
    fig3 = visualizer.plot_returns_distribution(returns, 'BTC')
    
    plt.show()