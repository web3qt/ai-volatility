# 加密货币波动率预测智能体

这个项目使用Eliza框架开发了一个基于EWMA(指数加权移动平均)模型的加密货币波动率预测智能体。该智能体能够分析指定token的历史价格数据，计算并预测其波动率，为交易决策提供数据支持。

## 功能特点

- 基于EWMA模型的波动率计算
- 支持多种加密货币的数据获取和分析
- 可视化波动率趋势
- 提供风险评估和交易建议

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python main.py --token BTC --days 30 --lambda 0.94
```

参数说明：

- `--token`: 指定要分析的加密货币代码（如BTC, ETH等）
- `--days`: 历史数据的天数
- `--lambda`: EWMA模型的衰减因子（默认为0.94，符合RiskMetrics标准）

## 项目结构

- `main.py`: 主程序入口
- `data_fetcher.py`: 负责获取加密货币的历史价格数据
- `volatility_model.py`: 实现EWMA模型的波动率计算
- `eliza_agent.py`: 基于Eliza框架的智能体实现
- `visualization.py`: 数据可视化模块
- `utils.py`: 工具函数集合

## 运行命令

- 分析比特币30天的波动率：

```bash
python main.py --token BTC --days 30 --command analyze
 ```

- 预测以太坊未来14天的波动率：

```bash
python main.py --token ETH --days 60 --horizon 14 --command predict
 ```

- 比较BTC、ETH和SOL的波动率：

```bash
python main.py --compare-tokens BTC,ETH,SOL --days 30 --command compare
 ```

- 评估比特币的风险水平：

```bash
python main.py --token BTC --command risk
 ```
