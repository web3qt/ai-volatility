# Cryptocurrency Volatility Prediction Agent

## Project Introduction

This is a cryptocurrency volatility prediction agent based on the EWMA (Exponentially Weighted Moving Average) model. The agent can analyze and predict cryptocurrency price volatility in real-time, providing data support for investment decisions. By integrating historical price data, volatility calculations, and risk assessments, it helps users better understand and predict cryptocurrency market volatility.

## Core Features

- **Volatility Analysis**: Calculate historical volatility based on the EWMA model, supporting customizable time windows
- **Volatility Prediction**: Use statistical models to predict future volatility trends
- **Multi-Currency Comparison**: Support comparative volatility analysis of multiple cryptocurrencies
- **Risk Assessment**: Provide detailed risk assessment reports and trading recommendations
- **Visualization**: Generate intuitive volatility trend charts and comparison graphs
- **Real-time Data**: Automatically fetch the latest cryptocurrency market data
- **PDF Report Export**: Support exporting analysis results as PDF format reports
- **DeepSeek Integration**: Utilize the DeepSeek large model to provide intelligent market analysis

## Technical Features

- Use EWMA model for volatility modeling, compliant with RiskMetrics standards
- Support customizable decay factor (λ), with a default value of 0.94 conforming to financial industry standards
- Provide a complete data analysis chain, from data acquisition to result visualization
- Integrate DeepSeek large model API, providing intelligent market analysis and prediction
- Implemented in Python, with good scalability
- Use LangChain framework to implement AI analysis processes
- Support various visualization charts and PDF report export

## Installation Guide

### Requirements

- Python 3.7 or higher

### Installation Steps

1. Clone the repository

```bash
git clone https://github.com/yourusername/ai-volatility.git
cd ai-volatility
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Configure environment variables (optional, for DeepSeek API integration)

Create a `.env` file and add the following content:

```
DEEPSEEK_API_KEY=your_api_key_here
```

## Usage

### Basic Usage

```bash
python main.py --token BTC --days 30 --command analyze
```

### Common Commands

1. Analyze the volatility of a specific cryptocurrency

```bash
python main.py --token ETH --days 30 --command analyze
```

2. Predict future volatility

```bash
python main.py --token BTC --days 30 --command predict --horizon 7
```

3. Compare volatility of multiple cryptocurrencies

```bash
python main.py --token BTC --compare-tokens BTC,ETH --days 30 --command compare
```

4. Conduct risk assessment

```bash
python main.py --token BTC --days 30 --command risk
```

## Parameter Description

- `--token`: Cryptocurrency code (e.g., BTC, ETH)
- `--days`: Number of days of historical data, default is 30 days
- `--lambda`: EWMA model decay factor, default is 0.94
- `--horizon`: Prediction time span (days), default is 7 days
- `--command`: Execution command (analyze/predict/compare/risk)
- `--compare-tokens`: List of tokens to compare, separated by commas (only for compare command)

## Project Structure

```
├── main.py           # Main program entry
├── requirements.txt  # Project dependencies
├── src/              # Source code directory
│   ├── __init__.py   # Package initialization file
│   ├── volatility_agent.py # Core implementation of volatility prediction agent
│   ├── models/       # Models directory
│   │   ├── __init__.py
│   │   └── volatility_model.py # EWMA model implementation
│   ├── services/     # Services directory
│   │   ├── __init__.py
│   │   ├── data_fetcher.py   # Data fetching module
│   │   ├── market_analysis.py # Market analysis module
│   │   └── visualization.py  # Data visualization module
│   └── utils/        # Utilities directory
│       ├── __init__.py
│       └── pdf_exporter.py   # PDF report export module
├── tests/            # Tests directory
│   └── test_pdf.py   # PDF export test
├── data/             # Data storage directory
├── docs/             # Documentation directory
└── output/           # Output directory (analysis results and reports)
```

## Output Examples

### Volatility Analysis Output

```
Analyzing BTC volatility...

Analysis Results:
- Analysis Period: 2023-01-01 to 2023-01-30 (30 days)
- Average Volatility: 2.34%
- Maximum Volatility: 4.56% (2023-01-15)
- Minimum Volatility: 1.23% (2023-01-05)
- Current Volatility: 2.78%

Volatility trend chart has been saved to: output/BTC_volatility_trend.png
```

### Risk Assessment Output

```
Risk Assessment Report - BTC

- Daily VaR at 95% confidence interval: 3.45%
- Expected Shortfall (ES): 4.12%
- Volatility Trend: Increasing
- Risk Level: Medium-High Risk

Recommendation: Maintain caution in the short term, consider reducing position or setting stop-loss.
```

## Notes

1. Ensure network connection is normal to fetch the latest market data
2. Python 3.7 or higher is recommended
3. Output directories will be created automatically on first run
4. Large data volume analysis may require longer processing time
5. DeepSeek API functionality requires a valid API key

## Development Plan

- [ ] Add support for more prediction models
- [ ] Optimize data acquisition efficiency
- [ ] Add Web interface support
- [ ] Increase more risk indicators
- [ ] Support custom data sources
- [ ] Enhance DeepSeek model integration capabilities
- [ ] Add backtesting functionality
