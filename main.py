#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
加密货币波动率预测智能体 - 主程序入口
"""

import argparse
import sys
from volatility_agent import Message, VolatilityAgent


def parse_arguments():
    """
    解析命令行参数
    
    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(description="加密货币波动率预测智能体")
    parser.add_argument("--token", type=str, default="BTC", help="指定要分析的加密货币代码（如BTC, ETH等）")
    parser.add_argument("--days", type=int, default=30, help="历史数据的天数")
    parser.add_argument("--lambda", dest="lambda_param", type=float, default=0.94, 
                        help="EWMA模型的衰减因子（默认为0.94，符合RiskMetrics标准）")
    parser.add_argument("--command", type=str, default="analyze", 
                        choices=["analyze", "predict", "compare", "risk", "help"],
                        help="要执行的命令（analyze, predict, compare, risk, help）")
    parser.add_argument("--horizon", type=int, default=7, help="预测未来的天数（仅用于predict命令）")
    parser.add_argument("--compare-tokens", type=str, help="要比较的代币列表，用逗号分隔（仅用于compare命令）")
    
    return parser.parse_args()


def main():
    """
    主函数
    """
    # 解析命令行参数
    args = parse_arguments()
    
    # 初始化波动率预测智能体
    agent = VolatilityAgent(lambda_param=args.lambda_param)
    
    # 根据命令执行相应操作
    if args.command == "help":
        response = agent.process(Message("help"))
        print(response.content)
    
    elif args.command == "analyze":
        command = f"analyze {args.token} {args.days}"
        response = agent.process(Message(command))
        print(response.content)
    
    elif args.command == "predict":
        command = f"predict {args.token} {args.days} {args.horizon}"
        response = agent.process(Message(command))
        print(response.content)
    
    elif args.command == "compare":
        if args.compare_tokens:
            tokens = args.compare_tokens
        else:
            tokens = args.token  # 如果没有指定比较代币，则使用主代币
        
        command = f"compare {tokens} {args.days}"
        response = agent.process(Message(command))
        print(response.content)
    
    elif args.command == "risk":
        # 先分析代币以获取数据
        analyze_command = f"analyze {args.token} {args.days}"
        agent.process(Message(analyze_command))
        
        # 然后评估风险
        risk_command = f"risk {args.token}"
        response = agent.process(Message(risk_command))
        print(response.content)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序运行出错: {str(e)}")
        sys.exit(1)