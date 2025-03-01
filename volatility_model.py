#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
波动率模型模块 - 实现基于EWMA模型的波动率计算
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats


class VolatilityModel:
    """
    波动率模型类
    实现基于EWMA(指数加权移动平均)的波动率计算
    """
    
    def __init__(self, lambda_param=0.94):
        """
        初始化波动率模型
        
        Args:
            lambda_param (float): EWMA模型的衰减因子，默认为0.94（RiskMetrics标准）
        """
        self.lambda_param = lambda_param
        
    def calculate_ewma_volatility(self, returns):
        """
        使用EWMA模型计算波动率
        
        Args:
            returns (pandas.Series): 收益率序列
            
        Returns:
            pandas.Series: 波动率序列
        """
        # 计算平方收益率
        squared_returns = returns ** 2
        
        # 初始化波动率序列
        volatility = pd.Series(index=returns.index)
        
        # 设置初始波动率（使用前20个观测值的样本方差）
        if len(returns) >= 20:
            volatility.iloc[0] = squared_returns[:20].mean()
        else:
            volatility.iloc[0] = squared_returns.mean()
        
        # 使用EWMA递归计算波动率
        for t in range(1, len(returns)):
            volatility.iloc[t] = self.lambda_param * volatility.iloc[t-1] + \
                               (1 - self.lambda_param) * squared_returns.iloc[t-1]
        
        # 转换为标准差形式（开平方）
        volatility = np.sqrt(volatility)
        
        return volatility
    
    def forecast_volatility(self, current_volatility, horizon=1):
        """
        基于当前波动率预测未来波动率
        
        Args:
            current_volatility (float): 当前波动率
            horizon (int): 预测时间范围（天数）
            
        Returns:
            float: 预测的波动率
        """
        # EWMA模型下，h步预测等于当前波动率
        return current_volatility
    
    def calculate_var(self, volatility, confidence_level=0.95, investment=1.0):
        """
        计算风险价值(Value at Risk)
        
        Args:
            volatility (float): 波动率
            confidence_level (float): 置信水平，默认0.95
            investment (float): 投资金额，默认1.0
            
        Returns:
            float: 风险价值
        """
        # 计算对应置信水平的z值
        z_score = stats.norm.ppf(confidence_level)
        
        # 计算VaR
        var = investment * z_score * volatility
        
        return var
    
    def evaluate_risk_level(self, volatility, historical_volatility):
        """
        评估当前风险水平
        
        Args:
            volatility (float): 当前波动率
            historical_volatility (pandas.Series): 历史波动率序列
            
        Returns:
            str: 风险评级（低、中、高）
        """
        # 计算历史波动率的分位数
        low_threshold = historical_volatility.quantile(0.33)
        high_threshold = historical_volatility.quantile(0.67)
        
        if volatility < low_threshold:
            return "低风险"
        elif volatility > high_threshold:
            return "高风险"
        else:
            return "中等风险"


# 测试代码
if __name__ == "__main__":
    # 创建一些模拟的收益率数据
    np.random.seed(42)
    returns = pd.Series(np.random.normal(0, 0.01, 100))
    
    # 初始化波动率模型
    model = VolatilityModel(lambda_param=0.94)
    
    # 计算波动率
    volatility = model.calculate_ewma_volatility(returns)
    
    # 打印结果
    print("波动率统计:")
    print(volatility.describe())
    
    # 预测未来波动率
    current_vol = volatility.iloc[-1]
    forecast_vol = model.forecast_volatility(current_vol, horizon=5)
    print(f"\n当前波动率: {current_vol:.6f}")
    print(f"5天后预测波动率: {forecast_vol:.6f}")
    
    # 计算风险价值
    var_95 = model.calculate_var(current_vol, confidence_level=0.95, investment=1000)
    print(f"\n95%置信水平下的风险价值: ${var_95:.2f}")
    
    # 评估风险水平
    risk_level = model.evaluate_risk_level(current_vol, volatility)
    print(f"当前风险评级: {risk_level}")