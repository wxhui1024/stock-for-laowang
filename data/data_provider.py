"""
数据获取模块
基于Ashare项目封装，支持多源数据获取
"""
import pandas as pd
import akshare as ak
import tushare as ts
from datetime import datetime, timedelta
import logging

from config.settings import DATA_SOURCE, DEEPSEEK_API_KEY

logger = logging.getLogger(__name__)

class DataProvider:
    def __init__(self):
        # 初始化tushare
        if hasattr(ts, 'set_token'):
            ts.set_token('your_tushare_token_here')  # 如果使用tushare
        
    def get_stock_data(self, symbol, period='daily', days=30):
        """
        获取股票数据
        :param symbol: 股票代码
        :param period: 时间周期 ('daily', 'weekly', 'monthly', '1min', '5min', '15min', '30min', '60min')
        :param days: 获取天数
        :return: DataFrame
        """
        try:
            if DATA_SOURCE == 'ashare':
                return self._get_ashare_data(symbol, period, days)
            elif DATA_SOURCE == 'akshare':
                return self._get_akshare_data(symbol, period, days)
            elif DATA_SOURCE == 'tushare':
                return self._get_tushare_data(symbol, period, days)
            else:
                # 默认使用akshare
                return self._get_akshare_data(symbol, period, days)
        except Exception as e:
            logger.error(f"Error getting data for {symbol}: {str(e)}")
            # 返回一个空的DataFrame作为fallback
            import pandas as pd
            return pd.DataFrame()
    
    def _get_ashare_data(self, symbol, period, days):
        """使用Ashare风格的数据获取"""
        # 这里我们会导入Ashare的核心逻辑
        # 由于Ashare是一个独立的库，我们需要模拟其功能
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # 使用akshare作为替代
        if symbol.endswith('.XSHG') or symbol.endswith('SH'):
            # 上交所股票
            code = symbol.replace('.XSHG', '').replace('SH', '')
            df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start_date, end_date=end_date, adjust="")
        elif symbol.endswith('.XSHE') or symbol.endswith('SZ'):
            # 深交所股票
            code = symbol.replace('.XSHE', '').replace('SZ', '')
            df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start_date, end_date=end_date, adjust="")
        else:
            # 默认处理
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="")
        
        # 转换列名为标准格式
        if not df.empty:
            df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume'
            }, inplace=True)
            
            # 转换日期格式
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
        return df
    
    def _get_akshare_data(self, symbol, period, days):
        """使用akshare获取数据"""
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        if symbol.endswith('.XSHG') or symbol.endswith('SH'):
            code = symbol.replace('.XSHG', '').replace('SH', '')
            df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start_date, end_date=end_date, adjust="")
        elif symbol.endswith('.XSHE') or symbol.endswith('SZ'):
            code = symbol.replace('.XSHE', '').replace('SZ', '')
            df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start_date, end_date=end_date, adjust="")
        else:
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="")
        
        if not df.empty:
            df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume'
            }, inplace=True)
            
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        
        return df
    
    def _get_tushare_data(self, symbol, period, days):
        """使用tushare获取数据"""
        pro = ts.pro_api()
        
        # 转换股票代码格式
        ts_symbol = symbol.replace('.XSHG', '.SH').replace('.XSHE', '.SZ')
        
        # 获取数据
        df = pro.daily(ts_code=ts_symbol, start_date=(
            datetime.now() - timedelta(days=days)).strftime('%Y%m%d'),
            end_date=datetime.now().strftime('%Y%m%d'))
        
        if not df.empty:
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df.set_index('trade_date', inplace=True)
            df.rename(columns={'vol': 'volume'}, inplace=True)
        
        return df

    def get_market_overview(self):
        """获取市场概览数据"""
        try:
            # 获取主要指数数据
            indices = {
                '上证指数': '000001.XSHG',
                '深证成指': '399001.XSHE',
                '创业板指': '399006.XSHE',
            }
            
            overview = {}
            for name, code in indices.items():
                data = self.get_stock_data(code, period='daily', days=1)
                if not data.empty:
                    latest = data.iloc[-1]
                    overview[name] = {
                        'close': latest['close'],
                        'change_pct': ((latest['close'] - latest['open']) / latest['open']) * 100 if latest['open'] != 0 else 0
                    }
            
            return overview
        except Exception as e:
            logger.error(f"Error getting market overview: {str(e)}")
            return {}

# 全局数据提供者实例
data_provider = DataProvider()