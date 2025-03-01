# 加密货币波动率预测智能体

## 项目介绍

这是一个基于EWMA（指数加权移动平均）模型的加密货币波动率预测智能体。该智能体能够实时分析和预测加密货币价格波动率，为投资决策提供数据支持。通过整合历史价格数据、波动率计算和风险评估，帮助用户更好地理解和预测加密货币市场波动性。

## 核心功能

- **波动率分析**：基于EWMA模型计算历史波动率，支持自定义时间窗口
- **波动率预测**：使用统计模型预测未来波动率趋势
- **多币种比较**：支持多种加密货币的波动率对比分析
- **风险评估**：提供详细的风险评估报告和交易建议
- **可视化展示**：生成直观的波动率趋势图和对比图表
- **实时数据**：自动获取最新的加密货币市场数据
- **PDF报告导出**：支持将分析结果导出为PDF格式报告
- **DeepSeek集成**：利用DeepSeek大模型提供智能市场分析

## 技术特点

- 使用EWMA模型进行波动率建模，符合RiskMetrics标准
- 支持自定义衰减因子(λ)，默认值0.94符合金融行业标准
- 提供完整的数据分析链，从数据获取到结果可视化
- 集成DeepSeek大模型API，提供智能化市场分析和预测
- 基于Python实现，具有良好的可扩展性
- 使用LangChain框架实现AI分析流程
- 支持多种可视化图表和PDF报告导出

## 安装指南

### 环境要求

- Python 3.7或更高版本
- 网络连接（用于获取市场数据和调用DeepSeek API）

### 安装步骤

1. 克隆项目代码库

```bash
git clone https://github.com/yourusername/ai-volatility.git
cd ai-volatility
```

2. 安装依赖包

```bash
pip install -r requirements.txt
```

3. 配置环境变量（可选，用于DeepSeek API集成）

创建`.env`文件并添加以下内容：

```
DEEPSEEK_API_KEY=your_api_key_here
```

## 使用方法

### 基本用法

```bash
python main.py --token BTC --days 30 --command analyze
```

### 常用命令

1. 分析特定加密货币的波动率

```bash
python main.py --token ETH --days 30 --command analyze
```

2. 预测未来波动率

```bash
python main.py --token BTC --days 30 --command predict --horizon 7
```

3. 比较多种加密货币的波动率

```bash
python main.py --token BTC --compare-tokens BTC,ETH --days 30 --command compare
```

4. 进行风险评估

```bash
python main.py --token BTC --days 30 --command risk
```

## 参数说明

- `--token`: 加密货币代码（如BTC、ETH）
- `--days`: 历史数据天数，默认30天
- `--lambda`: EWMA模型衰减因子，默认0.94
- `--horizon`: 预测时间跨度（天数），默认7天
- `--command`: 执行命令（analyze/predict/compare/risk）
- `--compare-tokens`: 要比较的代币列表，用逗号分隔（仅用于compare命令）

## 项目结构

```
├── main.py           # 主程序入口
├── requirements.txt  # 项目依赖
├── src/              # 源代码目录
│   ├── __init__.py   # 包初始化文件
│   ├── volatility_agent.py # 波动率预测智能体核心实现
│   ├── models/       # 模型目录
│   │   ├── __init__.py
│   │   └── volatility_model.py # EWMA模型实现
│   ├── services/     # 服务目录
│   │   ├── __init__.py
│   │   ├── data_fetcher.py   # 数据获取模块
│   │   ├── market_analysis.py # 市场分析模块
│   │   └── visualization.py  # 数据可视化模块
│   └── utils/        # 工具目录
│       ├── __init__.py
│       └── pdf_exporter.py   # PDF报告导出模块
├── tests/            # 测试目录
│   └── test_pdf.py   # PDF导出测试
├── data/             # 数据存储目录
├── docs/             # 文档目录
└── output/           # 输出目录（分析结果和报告）
```

## 输出示例

### 波动率分析输出

```
正在分析 BTC 的波动率...

分析结果：
- 分析周期：2023-01-01 至 2023-01-30 (30天)
- 平均波动率：2.34%
- 最大波动率：4.56% (2023-01-15)
- 最小波动率：1.23% (2023-01-05)
- 当前波动率：2.78%

波动率趋势图已保存至：output/BTC_volatility_trend.png
```

### 风险评估输出

```
风险评估报告 - BTC

- 95%置信区间下的日VaR：3.45%
- 预期最大损失(ES)：4.12%
- 波动率趋势：上升
- 风险等级：中高风险

建议：短期内保持谨慎，考虑降低仓位或设置止损。
```

## 注意事项

1. 确保网络连接正常，以便获取最新市场数据
2. 推荐使用Python 3.7或更高版本
3. 首次运行时会自动创建输出目录
4. 大数据量分析可能需要较长处理时间
5. DeepSeek API功能需要有效的API密钥

## 开发计划

- [ ] 添加更多预测模型支持
- [ ] 优化数据获取效率
- [ ] 添加Web界面支持
- [ ] 增加更多风险指标
- [ ] 支持自定义数据源
- [ ] 增强DeepSeek模型集成能力
- [ ] 添加回测功能
