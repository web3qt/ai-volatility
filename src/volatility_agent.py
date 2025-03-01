#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基于LangChain的波动率预测智能体实现
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# LangChain imports
from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.pydantic_v1 import BaseModel, Field

# 项目组件导入
import matplotlib.pyplot as plt
from src.services.data_fetcher import DataFetcher
from src.models.volatility_model import VolatilityModel
from src.services.visualization import VolatilityVisualizer
from src.services.market_analysis import MarketAnalyzer
from src.utils.pdf_exporter import PDFExporter


class Message:
    """
    用户消息类
    表示用户发送给智能体的消息
    """

    def __init__(self, content):
        """
        初始化消息对象

        Args:
            content (str): 消息内容
        """
        self.content = content
        self.timestamp = datetime.now()
        self.metadata = {}


class Response:
    """
    智能体响应类
    表示智能体对用户消息的响应
    """

    def __init__(self, content):
        """
        初始化响应对象

        Args:
            content (str): 响应内容
        """
        self.content = content
        self.timestamp = datetime.now()
        self.metadata = {}


class VolatilityChain(Chain):
    """
    波动率分析链
    使用LangChain框架实现的波动率分析链
    """
    
    volatility_model: VolatilityModel = None

    def __init__(self, volatility_model: VolatilityModel):
        """
        初始化波动率分析链

        Args:
            volatility_model: 波动率模型实例
        """
        super().__init__()
        self.volatility_model = volatility_model

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行波动率分析

        Args:
            inputs: 输入参数，包含returns（收益率序列）

        Returns:
            包含volatility（波动率序列）的字典
        """
        returns = inputs.get("returns")
        if returns is None:
            return {"error": "未提供收益率数据"}

        volatility = self.volatility_model.calculate_ewma_volatility(returns)
        forecast = None

        # 如果请求了预测，则计算预测值
        horizon = inputs.get("horizon")
        if horizon is not None and isinstance(horizon, int) and horizon > 0:
            forecast = self.volatility_model.forecast_volatility(volatility, horizon)

        return {"volatility": volatility, "forecast": forecast}

    @property
    def _chain_type(self) -> str:
        return "volatility_chain"

    @property
    def input_keys(self) -> List[str]:
        """返回链的输入键列表"""
        return ["returns", "horizon"]

    @property
    def output_keys(self) -> List[str]:
        """返回链的输出键列表"""
        return ["volatility", "forecast"]


class VolatilityAgent:
    """
    波动率预测智能体
    基于LangChain框架实现的加密货币波动率预测智能体
    """

    def __init__(self, lambda_param=0.94):
        """
        初始化波动率预测智能体

        Args:
            lambda_param (float): EWMA模型的衰减因子，默认为0.94
        """
        self.data_fetcher = DataFetcher()
        self.volatility_model = VolatilityModel(lambda_param=lambda_param)
        self.visualizer = VolatilityVisualizer()
        self.market_analyzer = MarketAnalyzer()
        self.pdf_exporter = PDFExporter()

        # 创建波动率分析链
        self.volatility_chain = VolatilityChain(self.volatility_model)

        # 状态管理
        self.current_token = None
        self.price_data = None
        self.returns = None
        self.volatility = None
        self.forecast = None

        # 历史记录
        self.memory = []
        self.context = {}

        # 输出目录
        self.output_dir = "output"
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
        return Response(
            f"我是波动率预测智能体，可以帮助您分析加密货币的波动率。\n请输入 'help' 或 '帮助' 查看支持的命令。"
        )

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
   - 说明：比较多个代币的波动率，用逗号分隔代币符号，可选择天数（默认30天）

4. **评估代币风险**
   - 格式：`risk <token>` 或 `风险 <token>`
   - 示例：`risk BTC` 或 `风险 ETH`
   - 说明：评估指定代币的风险水平（需要先分析该代币）
"""
        return Response(help_text)

    def _analyze_token(self, content):
        """
        分析代币波动率

        Args:
            content (str): 用户消息内容

        Returns:
            Response: 分析结果响应对象
        """
        # 解析命令参数
        parts = content.split()
        if len(parts) < 2:
            return Response("请指定要分析的代币符号，例如：analyze BTC 或 分析 ETH")

        token_symbol = parts[1].upper()
        days = 30  # 默认30天

        if len(parts) >= 3 and parts[2].isdigit():
            days = int(parts[2])

        # 获取代币ID
        token_id = self.data_fetcher.get_token_id(token_symbol)
        if token_id is None:
            return Response(f"未找到代币 {token_symbol}，请检查代币符号是否正确。")

        # 获取历史价格数据
        try:
            self.price_data = self.data_fetcher.get_historical_prices(
                token_id, days=days
            )
            if self.price_data is None or len(self.price_data) == 0:
                return Response(f"获取 {token_symbol} 的历史价格数据失败，请稍后再试。")
        except Exception as e:
            return Response(f"获取价格数据时出错: {str(e)}")

        # 计算收益率
        self.returns = self.volatility_model.calculate_returns(self.price_data)

        # 使用波动率链计算波动率
        result = self.volatility_chain({"returns": self.returns, "horizon": 1})  # 添加默认的horizon参数
        if "error" in result:
            return Response(f"计算波动率时出错: {result['error']}")

        self.volatility = result["volatility"]
        self.current_token = token_symbol

        # 生成可视化图表
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        price_chart = f"{self.output_dir}/{token_symbol}_price_{timestamp}.png"
        returns_chart = f"{self.output_dir}/{token_symbol}_returns_{timestamp}.png"
        volatility_chart = (
            f"{self.output_dir}/{token_symbol}_volatility_{timestamp}.png"
        )

        self.visualizer.plot_price_history(self.price_data, token_symbol)
        plt.savefig(price_chart)
        plt.close()

        self.visualizer.plot_returns(self.returns, token_symbol)
        plt.savefig(returns_chart)
        plt.close()

        self.visualizer.plot_volatility_trend(self.volatility, token_symbol)
        plt.savefig(volatility_chart)
        plt.close()

        # 生成分析结果
        current_volatility = self.volatility.iloc[-1] * 100
        avg_volatility = self.volatility.mean() * 100
        max_volatility = self.volatility.max() * 100
        min_volatility = self.volatility.min() * 100

        # 获取其他主要加密货币的数据作为比较
        comparison_tokens = ['BTC', 'ETH'] if token_symbol not in ['BTC', 'ETH'] else ['ETH', 'BNB']
        comparison_assets = {}
        for comp_token in comparison_tokens:
            comp_data = self.data_fetcher.get_historical_prices(comp_token, days=days)
            if comp_data is not None:
                comparison_assets[comp_token] = comp_data['price']

        # 生成综合市场分析报告
        market_analysis = self.market_analyzer.generate_market_analysis(
            token_symbol,
            self.price_data,
            self.volatility,
            comparison_assets
        )

        result_text = f"""
## {token_symbol} 综合市场分析报告

### 基础波动率指标
- **分析周期**: 过去 {days} 天
- **当前波动率**: {current_volatility:.2f}%
- **平均波动率**: {avg_volatility:.2f}%
- **最大波动率**: {max_volatility:.2f}%
- **最小波动率**: {min_volatility:.2f}%

### 深度市场分析
{market_analysis}

### 可视化图表
以下图表已保存：
- {price_chart}
- {returns_chart}
- {volatility_chart}
"""

        response = Response(result_text)
        response.metadata["charts"] = [price_chart, returns_chart, volatility_chart]

        # 导出PDF报告
        pdf_path = self.pdf_exporter.export_analysis_to_pdf(
            token_symbol,
            result_text,
            [price_chart, returns_chart, volatility_chart],
            {"analysis_type": "market_analysis", "days": days}
        )
        response.metadata["pdf_report"] = pdf_path

        # 记住这次分析
        self.remember(Message(content), response)

        return response

    def _predict_volatility(self, content):
        """
        预测未来波动率

        Args:
            content (str): 用户消息内容

        Returns:
            Response: 预测结果响应对象
        """
        # 解析命令参数
        parts = content.split()
        if len(parts) < 2:
            return Response("请指定要预测的代币符号，例如：predict BTC 或 预测 ETH")

        token_symbol = parts[1].upper()
        days = 30  # 默认30天
        horizon = 7  # 默认预测7天

        if len(parts) >= 3 and parts[2].isdigit():
            days = int(parts[2])

        if len(parts) >= 4 and parts[3].isdigit():
            horizon = int(parts[3])

        # 获取代币ID
        token_id = self.data_fetcher.get_token_id(token_symbol)
        if token_id is None:
            return Response(f"未找到代币 {token_symbol}，请检查代币符号是否正确。")

        # 获取历史价格数据
        try:
            self.price_data = self.data_fetcher.get_historical_prices(
                token_id, days=days
            )
            if self.price_data is None or len(self.price_data) == 0:
                return Response(f"获取 {token_symbol} 的历史价格数据失败，请稍后再试。")
        except Exception as e:
            return Response(f"获取价格数据时出错: {str(e)}")

        # 计算收益率
        self.returns = self.volatility_model.calculate_returns(self.price_data)

        # 使用波动率链计算波动率和预测
        result = self.volatility_chain({"returns": self.returns, "horizon": horizon})
        if "error" in result:
            return Response(f"计算波动率时出错: {result['error']}")

        self.volatility = result["volatility"]
        self.forecast = result["forecast"]
        self.current_token = token_symbol

        # 生成可视化图表
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        price_chart = f"{self.output_dir}/{token_symbol}_price_{timestamp}.png"
        volatility_chart = (
            f"{self.output_dir}/{token_symbol}_volatility_{timestamp}.png"
        )
        forecast_chart = f"{self.output_dir}/{token_symbol}_forecast_{timestamp}.png"

        self.visualizer.plot_price_history(self.price_data, token_symbol)
        plt.savefig(price_chart)
        plt.close()

        self.visualizer.plot_volatility(self.volatility, token_symbol)
        plt.savefig(volatility_chart)
        plt.close()

        # 创建预测日期
        last_date = self.volatility.index[-1]
        forecast_dates = [last_date + timedelta(days=i + 1) for i in range(horizon)]
        forecast_series = pd.Series(self.forecast, index=forecast_dates)

        # 绘制历史波动率和预测波动率
        plt.figure(figsize=(12, 6))
        plt.plot(
            self.volatility.index,
            self.volatility * 100,
            label="历史波动率",
            color="blue",
        )
        plt.plot(
            forecast_series.index,
            forecast_series * 100,
            label="预测波动率",
            color="red",
            linestyle="--",
        )
        plt.title(f"{token_symbol} 波动率预测 (未来 {horizon} 天)", fontsize=15)
        plt.xlabel("日期", fontsize=12)
        plt.ylabel("波动率 (%)", fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(forecast_chart)
        plt.close()

        # 生成预测结果
        current_volatility = self.volatility.iloc[-1] * 100
        avg_forecast = forecast_series.mean() * 100
        max_forecast = forecast_series.max() * 100
        min_forecast = forecast_series.min() * 100
        
        # 使用DeepSeek API进行深度波动率预测分析
        deepseek_analysis = self.market_analyzer.predict_volatility_with_deepseek(
            token_symbol,
            self.price_data,
            self.volatility,
            horizon
        )

        result_text = f"""
## {token_symbol} 波动率预测结果

- **分析周期**: 过去 {days} 天
- **预测周期**: 未来 {horizon} 天
- **当前波动率**: {current_volatility:.2f}%
- **预测平均波动率**: {avg_forecast:.2f}%
- **预测最大波动率**: {max_forecast:.2f}%
- **预测最小波动率**: {min_forecast:.2f}%

波动率预测图已保存至：
- {price_chart}
- {volatility_chart}
- {forecast_chart}

## DeepSeek AI 波动率深度分析

{deepseek_analysis}
"""

        response = Response(result_text)
        response.metadata["charts"] = [price_chart, volatility_chart, forecast_chart]

        # 导出PDF报告
        pdf_path = self.pdf_exporter.export_analysis_to_pdf(
            token_symbol,
            result_text,
            [price_chart, volatility_chart, forecast_chart],
            {"analysis_type": "volatility_prediction", "days": days, "horizon": horizon}
        )
        response.metadata["pdf_report"] = pdf_path

        # 记住这次预测
        self.remember(Message(content), response)

        return response

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
            return Response(
                "请指定要比较的代币符号，例如：compare BTC,ETH 或 比较 BTC,ETH,SOL"
            )

        tokens_str = parts[1]
        token_symbols = [t.strip().upper() for t in tokens_str.split(",")]

        if len(token_symbols) < 2:
            return Response(
                "请至少指定两个代币进行比较，用逗号分隔，例如：compare BTC,ETH"
            )

        days = 30  # 默认30天
        if len(parts) >= 3 and parts[2].isdigit():
            days = int(parts[2])

        # 存储各代币的波动率数据
        volatilities = {}
        invalid_tokens = []

        # 获取每个代币的波动率
        for token_symbol in token_symbols:
            # 获取代币ID
            token_id = self.data_fetcher.get_token_id(token_symbol)
            if token_id is None:
                invalid_tokens.append(token_symbol)
                continue

            # 获取历史价格数据
            try:
                price_data = self.data_fetcher.get_historical_prices(
                    token_id, days=days
                )
                if price_data is None or len(price_data) == 0:
                    invalid_tokens.append(token_symbol)
                    continue
            except Exception:
                invalid_tokens.append(token_symbol)
                continue

            # 计算收益率和波动率
            returns = self.volatility_model.calculate_returns(price_data)
            result = self.volatility_chain({"returns": returns, "horizon": 1})  # 添加默认的horizon参数
            if "error" in result:
                invalid_tokens.append(token_symbol)
                continue

            volatilities[token_symbol] = result["volatility"]

        # 检查是否有有效的代币数据
        if len(volatilities) < 2:
            error_msg = "无法比较代币波动率，有效代币数量不足。\n"
            if invalid_tokens:
                error_msg += f"以下代币无效或数据获取失败: {', '.join(invalid_tokens)}"
            return Response(error_msg)

        # 生成比较图表
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        comparison_chart = f"{self.output_dir}/comparison_{timestamp}.png"

        # 绘制比较图
        import matplotlib.pyplot as plt

        plt.figure(figsize=(12, 6))

        for token, vol in volatilities.items():
            plt.plot(vol.index, vol * 100, label=token)

        plt.title(f"代币波动率比较 (过去 {days} 天)", fontsize=15)
        plt.xlabel("日期", fontsize=12)
        plt.ylabel("波动率 (%)", fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(comparison_chart)
        plt.close()

        # 生成比较结果
        result_text = f"## 代币波动率比较结果 (过去 {days} 天)\n\n"

        # 添加当前波动率比较
        result_text += "### 当前波动率比较\n\n"
        current_vols = {
            token: vol.iloc[-1] * 100 for token, vol in volatilities.items()
        }
        sorted_tokens = sorted(current_vols.items(), key=lambda x: x[1], reverse=True)

        for token, vol in sorted_tokens:
            result_text += f"- **{token}**: {vol:.2f}%\n"

        # 添加平均波动率比较
        result_text += "\n### 平均波动率比较\n\n"
        avg_vols = {token: vol.mean() * 100 for token, vol in volatilities.items()}
        sorted_tokens = sorted(avg_vols.items(), key=lambda x: x[1], reverse=True)

        for token, vol in sorted_tokens:
            result_text += f"- **{token}**: {vol:.2f}%\n"

        # 添加最大波动率比较
        result_text += "\n### 最大波动率比较\n\n"
        max_vols = {token: vol.max() * 100 for token, vol in volatilities.items()}
        sorted_tokens = sorted(max_vols.items(), key=lambda x: x[1], reverse=True)

        for token, vol in sorted_tokens:
            result_text += f"- **{token}**: {vol:.2f}%\n"

        result_text += f"\n波动率比较图已保存至：\n- {comparison_chart}"

        if invalid_tokens:
            result_text += (
                f"\n\n注意：以下代币无效或数据获取失败: {', '.join(invalid_tokens)}"
            )

        response = Response(result_text)
        response.metadata["chart"] = comparison_chart

        # 记住这次比较
        self.remember(Message(content), response)

        return response

    def _assess_risk(self):
        """
        评估当前代币的风险水平

        Returns:
            Response: 风险评估响应对象
        """
        if self.current_token is None or self.volatility is None:
            return Response("请先使用 analyze 命令分析一个代币，然后再进行风险评估。")

        # 计算风险指标
        current_volatility = self.volatility.iloc[-1] * 100
        avg_volatility = self.volatility.mean() * 100
        volatility_trend = (
            self.volatility.iloc[-1] / self.volatility.iloc[-10]
            if len(self.volatility) >= 10
            else 1.0
        )

        # 根据波动率确定风险等级
        risk_level = "未知"
        risk_description = ""

        if current_volatility < 1.0:
            risk_level = "极低"
            risk_description = "波动率极低，价格非常稳定，风险极小。"
        elif current_volatility < 2.5:
            risk_level = "低"
            risk_description = "波动率较低，价格相对稳定，风险较小。"
        elif current_volatility < 5.0:
            risk_level = "中低"
            risk_description = "波动率中低，价格波动适中，风险可控。"
        elif current_volatility < 7.5:
            risk_level = "中等"
            risk_description = "波动率中等，价格波动明显，风险中等。"
        elif current_volatility < 10.0:
            risk_level = "中高"
            risk_description = "波动率中高，价格波动较大，风险较高。"
        elif current_volatility < 15.0:
            risk_level = "高"
            risk_description = "波动率高，价格波动剧烈，风险高。"
        else:
            risk_level = "极高"
            risk_description = "波动率极高，价格波动非常剧烈，风险极高。"

        # 生成趋势描述
        trend_description = ""
        if volatility_trend > 1.1:
            trend_description = "波动率呈上升趋势，风险可能进一步增加。"
        elif volatility_trend < 0.9:
            trend_description = "波动率呈下降趋势，风险可能逐渐降低。"
        else:
            trend_description = "波动率相对稳定，风险水平可能维持不变。"

        # 生成交易建议
        trading_advice = ""
        if risk_level in ["极低", "低"]:
            trading_advice = "适合长期持有和价值投资。"
        elif risk_level in ["中低", "中等"]:
            trading_advice = "适合中长期投资，建议设置止损。"
        elif risk_level == "中高":
            trading_advice = "适合短期交易，需密切关注市场变化，严格控制仓位。"
        else:  # 高或极高
            trading_advice = "高风险交易，建议谨慎参与，控制仓位，设置严格止损。"

        # 生成风险评估结果
        result_text = f"""
## {self.current_token} 风险评估报告

- **当前波动率**: {current_volatility:.2f}%
- **平均波动率**: {avg_volatility:.2f}%
- **波动率趋势**: {"上升" if volatility_trend > 1.1 else "下降" if volatility_trend < 0.9 else "稳定"}

### 风险等级: {risk_level}

{risk_description}

### 趋势分析

{trend_description}

### 交易建议

{trading_advice}
"""

        # 生成风险热力图
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        risk_chart = f"{self.output_dir}/{self.current_token}_risk_{timestamp}.png"

        # 创建风险仪表盘图
        plt.figure(figsize=(10, 6))
        plt.barh(["风险等级"], [current_volatility], color="orange")
        plt.xlim(0, 20)  # 设置x轴范围
        plt.axvline(x=2.5, color="green", linestyle="--")
        plt.axvline(x=5.0, color="yellowgreen", linestyle="--")
        plt.axvline(x=7.5, color="yellow", linestyle="--")
        plt.axvline(x=10.0, color="orange", linestyle="--")
        plt.axvline(x=15.0, color="red", linestyle="--")

        # 添加风险区域标签
        plt.text(1.25, 1.1, "极低", ha="center")
        plt.text(3.75, 1.1, "低", ha="center")
        plt.text(6.25, 1.1, "中等", ha="center")
        plt.text(8.75, 1.1, "中高", ha="center")
        plt.text(12.5, 1.1, "高", ha="center")
        plt.text(17.5, 1.1, "极高", ha="center")

        plt.title(f"{self.current_token} 风险仪表盘", fontsize=15)
        plt.tight_layout()
        plt.savefig(risk_chart)
        plt.close()

        response = Response(result_text)
        response.metadata["chart"] = risk_chart

        # 导出PDF报告
        pdf_path = self.pdf_exporter.export_analysis_to_pdf(
            self.current_token,
            result_text,
            [risk_chart],
            {"analysis_type": "risk_assessment", "risk_level": risk_level}
        )
        response.metadata["pdf_report"] = pdf_path

        return response

    def remember(self, message, response):
        """
        记住对话历史

        Args:
            message (Message): 用户消息对象
            response (Response): 智能体响应对象
        """
        self.memory.append((message, response))

    def get_memory(self):
        """
        获取对话历史

        Returns:
            list: 包含(message, response)元组的列表
        """
        return self.memory

    def clear_memory(self):
        """
        清除对话历史
        """
        self.memory = []
