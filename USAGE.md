# 老王股票分析系统使用说明

## 系统概述

这是一个基于DeepSeek AI模型的个人股票分析和策略系统，具备以下功能：
- 实时数据获取（A股、港股、美股）
- AI驱动的股票分析（使用DeepSeek模型）
- 个性化投资策略
- 风险监控与预警
- 盘后复盘总结
- 多渠道通知（企业微信、Telegram等）

## 环境准备

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置API密钥
复制 `.env.example` 文件并命名为 `.env`，然后填入相应的API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入以下信息：

```env
# DeepSeek API 配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# 数据源配置 (可选)
DATA_SOURCE=akshare

# 通知配置 (可选)
WECHAT_WORK_WEBHOOK=your_wechat_work_webhook_url
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Tushare配置 (可选)
TUSHARE_TOKEN=your_tushare_token
```

## 配置说明

### 股票监控列表
在 `config/settings.py` 中修改 `WATCHLIST` 变量，添加您想要监控的股票代码：

```python
WATCHLIST = [
    "000001.XSHG",  # 上证指数
    "399001.XSHE",  # 深证成指
    "600519.XSHG",  # 贵州茅台
    "000002.XSHE",  # 万科A
    # 添加您关注的其他股票
]
```

### 策略参数
在 `config/settings.py` 中可以调整以下策略参数：

- `RSI_OVERBOUGHT`: RSI超买阈值（默认70）
- `RSI_OVERSOLD`: RSI超卖阈值（默认30）
- `STOP_LOSS_PERCENT`: 止损百分比（默认5.0%）
- `TAKE_PROFIT_PERCENT`: 止盈百分比（默认10.0%）

## 运行系统

### 1. 直接运行
```bash
python main.py
```

### 2. 运行单个功能测试
```bash
# 测试单只股票分析
python -c "
from main import stock_system
stock_system.single_stock_analysis('600519.XSHG')
"

# 测试风险监控
python -c "
from monitoring.risk_monitor import risk_monitor
from config.settings import WATCHLIST
alerts = risk_monitor.monitor_stocks(WATCHLIST)
print(f'检测到 {len(alerts)} 个预警')
for alert in alerts:
    print(alert)
"
```

## 功能说明

### 1. 实时监控
- 监控设定的股票列表
- 检测技术指标信号（RSI、MACD、突破等）
- 价格异动和成交量异常监控
- 实时发送预警通知

### 2. AI分析
- 使用DeepSeek模型进行深度分析
- 提供技术面、基本面分析
- 给出投资建议和风险提示
- 生成个性化交易策略

### 3. 风险管理
- RSI超买超卖检测
- 价格突破信号
- 支撑阻力位分析
- 成交量异常监控

### 4. 定时报告
- 每日盘后分析报告
- 市场情绪分析
- 个股深度分析
- 策略建议更新

## 通知渠道配置

### 企业微信
1. 在企业微信群中添加机器人
2. 获取Webhook URL
3. 在 `.env` 文件中配置 `WECHAT_WORK_WEBHOOK`

### Telegram
1. 创建Telegram Bot
2. 获取Bot Token
3. 获取Chat ID
4. 在 `.env` 文件中配置 `TELEGRAM_BOT_TOKEN` 和 `TELEGRAM_CHAT_ID`

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    个人股票分析和策略系统                      │
├─────────────────────────────────────────────────────────────┤
│  数据层     │  逻辑层        │  应用层      │  通知层         │
│            │                │             │               │
│  Ashare    │  数据处理      │  AI分析      │  推送通知       │
│  (数据获取)   │  (清洗/存储)    │  (策略分析)    │  (风险提醒)     │
│            │                │             │               │
│  Tushare/   │  Pandas/      │  DeepSeek    │  企业微信/      │
│  Yahoo      │  SQLite       │  (AI模型)     │  Telegram      │
└─────────────────────────────────────────────────────────────┘
```

## 注意事项

1. 本系统仅供学习和参考，不构成投资建议
2. 使用前请确保已正确配置API密钥
3. 请注意API调用成本，合理设置监控频率
4. 系统运行期间会持续调用API，请注意用量
5. 投资有风险，入市需谨慎

## 常见问题

### API调用限制
如果遇到API调用限制，请：
1. 检查API提供商的用量限制
2. 适当降低监控频率
3. 考虑升级API套餐

### 数据获取问题
如果无法获取股票数据：
1. 检查网络连接
2. 确认股票代码格式正确
3. 检查数据源API配置

### 通知发送失败
如果通知无法发送：
1. 检查Webhook URL或Bot Token是否正确
2. 确认通知渠道配置
3. 检查网络连接