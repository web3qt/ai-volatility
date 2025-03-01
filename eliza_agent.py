#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基于Eliza框架的波动率预测智能体实现
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from eliza import Agent, Message, Response
from data_fetcher import DataFetcher
from volatility_model import VolatilityModel
from visualization import VolatilityVisualizer


class VolatilityAgent(Agent):
    """
    波动率预测智能体
    基于Eliza框架实现的加密货币波动率预测智能体
    """
    
    def __init__(self, lambda_param=0.94):
        """
        初始化波动率预测智能体
        
        Args:
            lambda_param (float): EWMA模型的衰减因子，默认为0.94
        """
        super().__init__()
        self.data_fetcher = DataFetcher()
        self.volatility_model = VolatilityModel(lambda_param=lambda_param)
        self.visualizer = VolatilityVisualizer()
        self.current_token = None
        self.price_data = None
        self.returns = None
        self.volatility = None
        self.output_dir = "output"
        
        # 创建输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def process(self, message):
        """
        处理用户消息
        
        Args:
            message (Message): 用户消息对象
            
        Returns:
            Response: 智能体响应对象
        """
        # 解析用户消息
        content = message.content.strip().lower()
        
        # 处理帮助命令
        if content == "help" or content == "帮助":
            return self._help_response()
        
        # 处理分析命令
        if content.startswith("analyze") or content.startswith("分析"):
            return self._analyze_token(content)
        
        # 处理预测命令
        if content.startswith("predict") or content.startswith("预测"):
            return self._predict_volatility(content)
        
        # 处理比较命令
        if content.startswith("compare") or content.startswith("比较"):
            return self._compare_tokens(content)
        
        # 处理风险评估命令
        if content.startswith("risk") or content.startswith("风险"):
            return self._assess_risk()
        
        # 处理未知命令
        return Response(f"我是波动率预测智能体，可以帮助您分析加密货币的波动率。\n请输入 'help' 或 '帮助' 查看支持的命令。")
    
    def _help_response(self):
        """
        生成帮助信息响应
        
        Returns:
            Response: 帮助信息响应对象
        """
        help_text = """
## 波动率预测智能体使用指南

支持的命令：

1. **分析代币波动率**
   - 格式：`analyze <token> [days]` 或 `分析 <token> [days]`
   - 示例：`analyze BTC 30` 或 `分析 ETH 60`
   - 说明：分析指定代币的历史波动率，可选择天数（默认30天）

2. **预测未来波动率**
   - 格式：`predict <token> [days] [horizon]` 或 `预测 <token> [days] [horizon]`
   - 示例：`predict BTC 30 7` 或 `预测 ETH 60 14`
   - 说明：预测指定代币未来的波动率，可选择历史天数（默认30天）和预测天数（默认7天）

3. **比较多个代币波动率**
   - 格式：`compare <token1>,<token2>... [days]` 或 `比较 <token1>,<token2>... [days]`
   - 示例：`compare BTC,ETH,SOL 30` 或 `比较 BTC,ETH 60`
   - 说明：比较多个代币的波动率，代币符号用逗号分隔，可选择天数（默认30天）

4. **评估当前风险**
   - 格式：`risk <token>` 或 `风险 <token>`
   - 示例：`risk BTC` 或 `风险 ETH`
   - 说明：评估指定代币的当前风险水平

5. **帮助**
   - 格式：`help` 或 `帮助`
   - 说明：显示此帮助信息
"""
        return Response(help_text)
    
    def _analyze_token(self, content):
        """
        分析指定代币的波动率
        
        Args:
            content (str): 用户消息内容
            
        Returns:
            Response: 分析结果响应对象
        """
        # 解析命令参数
        parts = content.split()
        if len(parts) < 2:
            return Response("请指定要分析的代币符号，例如：`analyze BTC` 或 `分析 ETH`")
        
        token = parts[1].upper()
        days = 30  # 默认30天
        
        if len(parts) >= 3 and parts[2].isdigit():
            days = int(parts[2])
        
        try:
            # 获取历史价格数据
            self.price_data = self.data_fetcher.get_historical_prices(token, days)
            if self.price_data is None:
                return Response(f"获取{token}的历史价格数据失败，请检查代币符号是否正确。")
            
            # 计算收益率
            self.returns = self.data_fetcher.get_daily_returns(token, days)
            if self.returns is None:
                return Response(f"计算{token}的收益率失败。")
            
            # 计算波动率
            self.volatility = self.volatility_model.calculate_ewma_volatility(self.returns)
            self.current_token = token
            
            # 生成图表
            price_fig = self.visualizer.plot_price_history(self.price_data, token)
            vol_fig = self.visualizer.plot_volatility_trend(self.volatility, token)
            ret_fig = self.visualizer.plot_returns_distribution(self.returns, token)
            
            # 保存图表
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            price_path = os.path.join(self.output_dir, f"{token}_price_{timestamp}.png")
            vol_path = os.path.join(self.output_dir, f"{token}_volatility_{timestamp}.png")
            ret_path = os.path.join(self.output_dir, f"{token}_returns_{timestamp}.png")
            
            self.visualizer.save_figure(price_fig, price_path)
            self.visualizer.save_figure(vol_fig, vol_path)
            self.visualizer.save_figure(ret_fig, ret_path)
            
            # 生成分析报告
            current_vol = self.volatility.iloc[-1]
            avg_vol = self.volatility.mean()
            max_vol = self.volatility.max()
            min_vol = self.volatility.min()
            
            report = f"""
## {token}波动率分析报告

### 基本信息
- 分析周期：过去{days}天
- 数据点数：{len(self.price_data)}个

### 波动率统计
- 当前波动率：{current_vol:.6f}
- 平均波动率：{avg_vol:.6f}
- 最大波动率：{max_vol:.6f}
- 最小波动率：{min_vol:.6f}

### 风险评估
- 风险等级：{self.volatility_model.evaluate_risk_level(current_vol, self.volatility)}

### 图表
- 价格走势图已保存至：{price_path}
- 波动率趋势图已保存至：{vol_path}
- 收益率分布图已保存至：{ret_path}
"""
            
            return Response(report)
            
        except Exception as e:
            return Response(f"分析{token}波动率时出错：{str(e)}")
    
    def _predict_volatility(self, content):
        """
        预测指定代币的未来波动率
        
        Args:
            content (str): 用户消息内容
            
        Returns:
            Response: 预测结果响应对象
        """
        # 解析命令参数
        parts = content.split()
        if len(parts) < 2:
            return Response("请指定要预测的代币符号，例如：`predict BTC` 或 `预测 ETH`")
        
        token = parts[1].upper()
        days = 30  # 默认30天
        horizon = 7  # 默认预测未来7天
        
        if len(parts) >= 3 and parts[2].isdigit():
            days = int(parts[2])
        
        if len(parts) >= 4 and parts[3].isdigit():
            horizon = int(parts[3])
        
        try:
            # 如果当前没有数据或者代币不同，重新获取数据
            if self.current_token != token or self.volatility is None:
                # 获取历史价格数据
                self.price_data = self.data_fetcher.get_historical_prices(token, days)
                if self.price_data is None:
                    return Response(f"获取{token}的历史价格数据失败，请检查代币符号是否正确。")
                
                # 计算收益率
                self.returns = self.data_fetcher.get_daily_returns(token, days)
                if self.returns is None:
                    return Response(f"计算{token}的收益率失败。")
                
                # 计算波动率
                self.volatility = self.volatility_model.calculate_ewma_volatility(self.returns)
                self.current_token = token
            
            # 获取当前波动率
            current_vol = self.volatility.iloc[-1]
            
            # 预测未来波动率
            forecast_vol = self.volatility_model.forecast_volatility(current_vol, horizon)
            
            # 计算风险价值
            var_95 = self.volatility_model.calculate_var(forecast_vol, confidence_level=0.95, investment=1.0)
            var_99 = self.volatility_model.calculate_var(forecast_vol, confidence_level=0.99, investment=1.0)
            
            # 生成预测报告
            report = f"""
## {token}波动率预测报告

### 基本信息
- 分析周期：过去{days}天
- 预测周期：未来{horizon}天

### 波动率预测
- 当前波动率：{current_vol:.6f}
- 预测波动率：{forecast_vol:.6f}

### 风险价值(VaR)预测
- 95%置信水平下的每日VaR：{var_95:.6f} (相当于每投资1美元可能的最大损失)
- 99%置信水平下的每日VaR：{var_99:.6f} (相当于每投资1美元可能的最大损失)

### 风险评估
- 风险等级：{self.volatility_model.evaluate_risk_level(forecast_vol, self.volatility)}
"""
            
            return Response(report)
            
        except Exception as e:
            return Response(f"预测{token}波动率时出错：{str(e)}")
    
    def _compare_tokens(self, content):
        """
        比较多个代币的波动率
        
        Args:
            content (str): 用户消息内容
            
        Returns:
            Response: 比较结果响应对象
        """
        # 解析命令参数
        parts = content.split()
        if len(parts) < 2:
            return Response("请指定要比较的代币符号，例如：`compare BTC,ETH` 或 `比较 BTC,ETH,SOL`")
        
        tokens = parts[1].upper().split(',')
        days = 30  # 默认30天
        
        if len(parts) >= 3 and parts[2].isdigit():
            days = int(parts[2])
        
        try:
            # 获取每个代币的波动率
            volatility_dict = {}
            for token in tokens:
                # 获取收益率
                returns = self.data_fetcher.get_daily_returns(token, days)
                if returns is None:
                    return Response(f"获取{token}的收益率失败，请检查代币符号是否正确。")
                
                # 计算波动率
                volatility = self.volatility_model.calculate_ewma_volatility(returns)
                volatility_dict[token] = volatility
            
            # 生成比较图表
            compare_fig = self.visualizer.plot_volatility_comparison(volatility_dict)
            
            # 保存图表
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            compare_path = os.path.join(self.output_dir, f"volatility_comparison_{timestamp}.png")
            self.visualizer.save_figure(compare_fig, compare_path)
            
            # 生成比较报告
            report = f"""
## 波动率比较报告

### 基本信息
- 比较代币：{', '.join(tokens)}
- 分析周期：过去{days}天

### 当前波动率
"""
            
            # 添加每个代币的当前波动率
            for token, vol_series in volatility_dict.items():
                current_vol = vol_series.iloc[-1]
                risk_level = self.volatility_model.evaluate_risk_level(current_vol, vol_series)
                report += f"- {token}: {current_vol:.6f} ({risk_level})\n"
            
            report += f"\n### 图表\n- 波动率比较图已保存至：{compare_path}\n"
            
            return Response(report)
            
        except Exception as e:
            return Response(f"比较代币波动率时出错：{str(e)}")
    
    def _assess_risk(self):
        """
        评估当前代币的风险水平
        
        Returns:
            Response: 风险评估响应对象
        """
        if self.current_token is None or self.volatility is None:
            return Response("请先使用分析命令分析代币波动率，例如：`analyze BTC` 或 `分析 ETH`")
        
        try:
            # 获取当前波动率
            current_vol = self.volatility.iloc[-1]
            
            # 计算风险价值
            var_95 = self.volatility_model.calculate_var(current_vol, confidence_level=0.95, investment=1.0)
            var_99 = self.volatility_model.calculate_var(current_vol, confidence_level=0.99, investment=1.0)
            
            # 评估风险水平
            risk_level = self.volatility_model.evaluate_risk_level(current_vol, self.volatility)
            
            # 生成风险评估报告
            report = f"""
## {self.current_token}风险评估报告

### 波动率信息
- 当前波动率：{current_vol:.6f}
- 历史平均波动率：{self.volatility.mean():.6f}

### 风险价值(VaR)
- 95%置信水平下的每日VaR：{var_95:.6f} (相当于每投资1美元可能的最大损失)
- 99%置信水平下的每日VaR：{var_99:.6f} (相当于每投资1美元可能的最大损失)

### 风险评估
- 风险等级：{risk_level}
- 建议："""
            
            # 根据风险等级给出建议
            if risk_level == "低风险":
                report += "当前波动率较低，风险较小，可以考虑增加投资比例。"
            elif risk_level == "中等风险":
                report += "当前波动率处于中等水平，建议保持适度投资，注意风险控制。"
            else:  # 高风险
                report += "当前波动率较高，风险较大，建议减少投资比例或暂时观望。"
            
            return Response(report)
            
        except Exception as e:
            return Response(f"评估{self.current_token}风险时出错：{str(e)}")