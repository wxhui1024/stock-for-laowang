import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")  # 或者 "deepseek-reasoner"

# 数据源配置
DATA_SOURCE = os.getenv("DATA_SOURCE", "ashare")  # ashare, tushare, akshare

# 监控股票列表
WATCHLIST = [
    "000001.XSHG",  # 上证指数
    "399001.XSHE",  # 深证成指
    "002050.XSHE",  # 三花智控
    "603087.XSHG",  # 甘李药业
    "600089.XSHG",  # 特变电工
    "600845.XSHG",  # 宝信软件
    "600592.XSHG",  # 龙溪股份
]

# 策略参数
RSI_OVERBOUGHT = 70  # RSI超买线
RSI_OVERSOLD = 30    # RSI超卖线
STOP_LOSS_PERCENT = 5.0  # 止损百分比
TAKE_PROFIT_PERCENT = 10.0  # 止盈百分比

# 通知配置
NOTIFICATION_CHANNELS = {
    "wechat_work": os.getenv("WECHAT_WORK_WEBHOOK"),
    "telegram": {
        "bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
        "chat_id": os.getenv("TELEGRAM_CHAT_ID")
    }
}

# 定时任务配置
TRADING_HOURS_START = "09:30"
TRADING_HOURS_END = "15:00"
POST_MARKET_ANALYSIS_TIME = "17:00"  # 盘后分析时间