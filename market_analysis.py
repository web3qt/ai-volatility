#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
市场分析模块 - 负责多维度市场数据分析和报告生成
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM
from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain.schema.output import ChatGeneration, ChatResult
from typing import Any, Dict, List, Mapping, Optional, Union, Tuple
from dotenv import load_dotenv
import requests
import json

# 加载环境变量
load_dotenv()

# DeepSeek API配置
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

class DeepSeekChatModel(BaseChatModel):
    """DeepSeek聊天模型的LangChain集成"""
    
    client: Any = None
    model_name: str = "deepseek-chat"
    api_key: str = None
    api_url: str = DEEPSEEK_API_URL
    temperature: float = 0.7
    max_tokens: int = 1024
    
    def __init__(self, api_key: str, **kwargs):
        """初始化DeepSeek聊天模型
        
        Args:
            api_key: DeepSeek API密钥
            **kwargs: 其他参数
        """
        super().__init__(**kwargs)
        self.api_key = api_key
        
        # 设置其他参数
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def _llm_type(self) -> str:
        """返回LLM类型"""
        return "deepseek-chat"
    
    def _convert_messages_to_deepseek_format(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        """将LangChain消息转换为DeepSeek API格式
        
        Args:
            messages: LangChain消息列表
            
        Returns:
            DeepSeek格式的消息列表
        """
        deepseek_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                deepseek_messages.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                deepseek_messages.append({"role": "assistant", "content": message.content})
            elif isinstance(message, SystemMessage):
                deepseek_messages.append({"role": "system", "content": message.content})
            else:
                deepseek_messages.append({"role": "user", "content": str(message.content)})
        return deepseek_messages
    
    def _generate(
        self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs
    ) -> ChatResult:
        """生成聊天完成
        
        Args:
            messages: 消息列表
            stop: 停止序列（可选）
            **kwargs: 其他参数
            
        Returns:
            ChatResult: 包含生成结果的LangChain格式对象
        """
        # 准备请求数据
        deepseek_messages = self._convert_messages_to_deepseek_format(messages)
        
        request_data = {
            "model": self.model_name,
            "messages": deepseek_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        # 添加stop序列（如果提供）
        if stop is not None:
            request_data["stop"] = stop
        
        # 添加其他参数
        for key, value in kwargs.items():
            if key not in request_data:
                request_data[key] = value
        
        # 发送API请求
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=request_data
        )
        
        if response.status_code != 200:
            raise ValueError(f"DeepSeek API请求失败: {response.status_code} {response.text}")
        
        response_data = response.json()
        
        # 提取生成的文本
        generated_text = response_data["choices"][0]["message"]["content"]
        
        # 创建LangChain格式的返回对象
        message = AIMessage(content=generated_text)
        generation = ChatGeneration(message=message)
        
        # 创建ChatResult对象
        chat_result = ChatResult(generations=[generation])
        
        # 添加额外的元数据
        if "usage" in response_data:
            chat_result.llm_output = {"token_usage": response_data["usage"]}
        
        return chat_result
    
    async def _agenerate(
        self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs
    ) -> ChatResult:
        """异步生成聊天完成（简单实现，实际应使用aiohttp）"""
        return self._generate(messages, stop, **kwargs)

class MarketAnalyzer:
    """
    市场分析器类
    负责整合多维度数据并生成综合分析报告
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化市场分析器
        
        Args:
            api_key: DeepSeek API密钥（可选）
        """
        try:
            # 优先使用传入的API密钥，其次尝试从环境变量获取
            if api_key is None:
                api_key = os.getenv('DEEPSEEK_API_KEY')
            
            if api_key is None:
                raise ValueError("未找到DeepSeek API密钥，请设置DEEPSEEK_API_KEY环境变量或直接传入api_key参数")
            
            # 初始化DeepSeek聊天模型
            self.llm = DeepSeekChatModel(
                api_key=api_key,
                temperature=0.7,
                max_tokens=2048
            )
        except Exception as e:
            raise Exception(f"初始化DeepSeekChatModel失败: {str(e)}")

        
        # 设置分析报告模板
        self.report_template = PromptTemplate(
            input_variables=["token_symbol", "market_data", "technical_indicators", 
                            "correlation_data", "volatility_data", "macro_indicators"],
            template="""请基于以下数据对{token_symbol}进行全面的市场分析：

1. 市场数据：
{market_data}

2. 技术指标：
{technical_indicators}

3. 相关性分析：
{correlation_data}

4. 波动率数据：
{volatility_data}

5. 宏观指标：
{macro_indicators}

请从以下维度进行分析：
1. 当前市场情绪和趋势
2. 技术面分析
3. 相关资产联动性
4. 风险评估
5. 未来趋势预测
6. 投资建议

请生成一份详细的分析报告。"""
        )
        
        # 创建报告生成链
        self.report_chain = LLMChain(
            llm=self.llm,
            prompt=self.report_template
        )
        
    def analyze_technical_indicators(self, price_data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析技术指标
        
        Args:
            price_data: 价格数据DataFrame
            
        Returns:
            包含各种技术指标的字典
        """
        # 计算移动平均线
        price_data['MA5'] = price_data['price'].rolling(window=5).mean()
        price_data['MA20'] = price_data['price'].rolling(window=20).mean()
        
        # 计算RSI
        delta = price_data['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 计算MACD
        exp1 = price_data['price'].ewm(span=12, adjust=False).mean()
        exp2 = price_data['price'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        
        return {
            "moving_averages": {
                "MA5": price_data['MA5'].iloc[-1],
                "MA20": price_data['MA20'].iloc[-1]
            },
            "rsi": rsi.iloc[-1],
            "macd": {
                "macd": macd.iloc[-1],
                "signal": signal.iloc[-1]
            }
        }
    
    def analyze_correlations(self, token_price: pd.Series, 
                           comparison_assets: Dict[str, pd.Series]) -> Dict[str, float]:
        """
        分析与其他资产的相关性
        
        Args:
            token_price: 目标代币价格序列
            comparison_assets: 其他资产的价格序列字典
            
        Returns:
            相关性系数字典
        """
        correlations = {}
        for asset_name, asset_price in comparison_assets.items():
            # 确保两个序列长度相同
            min_length = min(len(token_price), len(asset_price))
            correlation = token_price[-min_length:].corr(asset_price[-min_length:])
            correlations[asset_name] = correlation
        return correlations
    
    def generate_market_analysis(self, token_symbol: str, 
                               price_data: pd.DataFrame,
                               volatility_data: pd.Series,
                               comparison_assets: Dict[str, pd.Series] = None) -> str:
        """
        生成综合市场分析报告
        
        Args:
            token_symbol: 代币符号
            price_data: 价格数据
            volatility_data: 波动率数据
            comparison_assets: 用于比较的其他资产数据（可选）
            
        Returns:
            str: 分析报告文本
        """
        # 准备技术指标数据
        technical_indicators = self.analyze_technical_indicators(price_data)
        
        # 准备相关性数据
        correlation_data = {}
        if comparison_assets:
            correlation_data = self.analyze_correlations(price_data['price'], comparison_assets)
        
        # 准备市场数据摘要
        market_data = {
            "current_price": price_data['price'].iloc[-1],
            "24h_change": (price_data['price'].iloc[-1] / price_data['price'].iloc[-24] - 1) * 100,
            "24h_volume": price_data['volume'].iloc[-24:].sum(),
            "7d_high": price_data['price'].iloc[-168:].max(),
            "7d_low": price_data['price'].iloc[-168:].min()
        }
        
        # 准备波动率数据摘要
        volatility_summary = {
            "current": volatility_data.iloc[-1],
            "7d_avg": volatility_data.iloc[-7:].mean(),
            "30d_avg": volatility_data.iloc[-30:].mean() if len(volatility_data) >= 30 else None,
            "trend": "上升" if volatility_data.iloc[-1] > volatility_data.iloc[-7:].mean() else "下降"
        }
        
        # 生成分析报告
        report = self.report_chain.run({
            "token_symbol": token_symbol,
            "market_data": json.dumps(market_data, ensure_ascii=False, indent=2),
            "technical_indicators": json.dumps(technical_indicators, ensure_ascii=False, indent=2),
            "correlation_data": json.dumps(correlation_data, ensure_ascii=False, indent=2),
            "volatility_data": json.dumps(volatility_summary, ensure_ascii=False, indent=2),
            "macro_indicators": "暂无宏观经济数据"
        })
        
        return report