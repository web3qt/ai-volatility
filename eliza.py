#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Eliza框架 - 简单的智能体框架实现
"""

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
        self.timestamp = None  # 可以在需要时添加时间戳
        self.metadata = {}     # 可以存储额外的元数据

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
        self.timestamp = None  # 可以在需要时添加时间戳
        self.metadata = {}     # 可以存储额外的元数据

class Agent:
    """
    基础智能体类
    提供智能体的基本功能和接口
    """
    
    def __init__(self):
        """
        初始化智能体
        """
        self.context = {}  # 用于存储对话上下文
        self.memory = []   # 用于存储历史消息
    
    def process(self, message):
        """
        处理用户消息（需要被子类重写）
        
        Args:
            message (Message): 用户消息对象
            
        Returns:
            Response: 智能体响应对象
        """
        return Response("这是一个基础智能体，请在子类中实现process方法。")
    
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
    
    def set_context(self, key, value):
        """
        设置上下文变量
        
        Args:
            key (str): 变量名
            value: 变量值
        """
        self.context[key] = value
    
    def get_context(self, key, default=None):
        """
        获取上下文变量
        
        Args:
            key (str): 变量名
            default: 默认值
            
        Returns:
            变量值，如果不存在则返回默认值
        """
        return self.context.get(key, default)
    
    def clear_context(self):
        """
        清除所有上下文变量
        """
        self.context = {}