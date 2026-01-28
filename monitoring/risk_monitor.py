"""
风险监控模块
实时监控股票风险和机会，发送预警
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import time
from typing import Dict, List

from data.data_provider import data_provider
from analysis.ai_analyzer import ai_analyzer
from config.settings import RSI_OVERBOUGHT, RSI_OVERSOLD, STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT

logger = logging.getLogger(__name__)

class RiskMonitor:
    def __init__(self):
        self.alerts = []
        self.last_check_times = {}
    
    def calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: pd.Series) -> tuple:
        """计算MACD指标"""
        exp1 = prices.ewm(span=12).mean()
        exp2 = prices.ewm(span=26).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9).mean()
        histogram = macd - signal
        return macd, signal, histogram
    
    def detect_breakout(self, prices: pd.Series, lookback: int = 20) -> bool:
        """检测突破信号"""
        recent_high = prices.tail(lookback).max()
        current_price = prices.iloc[-1]
        previous_price = prices.iloc[-2] if len(prices) > 1 else current_price
        
        # 检查是否向上突破
        if current_price > recent_high * 0.995 and previous_price <= recent_high * 0.995:
            return True
        return False
    
    def detect_support_resistance(self, prices: pd.Series, lookback: int = 30) -> dict:
        """检测支撑位和阻力位"""
        recent_prices = prices.tail(lookback)
        resistance = recent_prices.max()
        support = recent_prices.min()
        
        current_price = prices.iloc[-1]
        
        return {
            "resistance": resistance,
            "support": support,
            "is_near_resistance": abs(current_price - resistance) / resistance < 0.02,  # 2%以内
            "is_near_support": abs(current_price - support) / support < 0.02
        }
    
    def check_technical_signals(self, symbol: str) -> List[Dict]:
        """检查技术指标信号"""
        alerts = []
        
        try:
            # 获取数据
            stock_data = data_provider.get_stock_data(symbol, period='daily', days=60)
            if stock_data.empty or len(stock_data) < 30:
                return alerts
            
            prices = stock_data['close']
            
            # 计算技术指标
            rsi = self.calculate_rsi(prices)
            current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else None
            
            # RSI信号
            if current_rsi is not None:
                if current_rsi > RSI_OVERBOUGHT:
                    alerts.append({
                        "type": "OVERBOUGHT",
                        "symbol": symbol,
                        "message": f"RSI超买信号: {current_rsi:.2f}",
                        "severity": "medium",
                        "timestamp": datetime.now().isoformat()
                    })
                elif current_rsi < RSI_OVERSOLD:
                    alerts.append({
                        "type": "OVERSOLD",
                        "symbol": symbol,
                        "message": f"RSI超卖信号: {current_rsi:.2f}",
                        "severity": "medium",
                        "timestamp": datetime.now().isoformat()
                    })
            
            # 突破信号
            if self.detect_breakout(prices):
                alerts.append({
                    "type": "BREAKOUT",
                    "symbol": symbol,
                    "message": f"价格突破信号: {prices.iloc[-1]:.2f}",
                    "severity": "high",
                    "timestamp": datetime.now().isoformat()
                })
            
            # 支撑阻力位
            sr_levels = self.detect_support_resistance(prices)
            if sr_levels["is_near_resistance"]:
                alerts.append({
                    "type": "NEAR_RESISTANCE",
                    "symbol": symbol,
                    "message": f"价格接近阻力位: {sr_levels['resistance']:.2f}",
                    "severity": "low",
                    "timestamp": datetime.now().isoformat()
                })
            elif sr_levels["is_near_support"]:
                alerts.append({
                    "type": "NEAR_SUPPORT",
                    "symbol": symbol,
                    "message": f"价格接近支撑位: {sr_levels['support']:.2f}",
                    "severity": "low",
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Error checking technical signals for {symbol}: {str(e)}")
        
        return alerts
    
    def check_price_alerts(self, symbol: str, current_price: float, threshold_percent: float = 2.0) -> List[Dict]:
        """检查价格预警"""
        alerts = []
        
        try:
            # 获取历史数据计算均价
            stock_data = data_provider.get_stock_data(symbol, period='daily', days=30)
            if not stock_data.empty:
                avg_price = stock_data['close'].tail(10).mean()
                
                # 计算涨跌幅
                change_percent = ((current_price - avg_price) / avg_price) * 100
                
                if abs(change_percent) >= threshold_percent:
                    alert_type = "SHARP_INCREASE" if change_percent > 0 else "SHARP_DECREASE"
                    severity = "high" if abs(change_percent) >= 5.0 else "medium"
                    
                    alerts.append({
                        "type": alert_type,
                        "symbol": symbol,
                        "message": f"价格异动: {change_percent:+.2f}% (当前价: {current_price:.2f})",
                        "severity": severity,
                        "timestamp": datetime.now().isoformat()
                    })
        except Exception as e:
            logger.error(f"Error checking price alerts for {symbol}: {str(e)}")
        
        return alerts
    
    def check_volume_anomalies(self, symbol: str) -> List[Dict]:
        """检查成交量异常"""
        alerts = []
        
        try:
            stock_data = data_provider.get_stock_data(symbol, period='daily', days=30)
            if stock_data.empty or len(stock_data) < 10:
                return alerts
            
            volumes = stock_data['volume']
            avg_volume = volumes.rolling(window=10).mean().iloc[-1]
            current_volume = volumes.iloc[-1]
            
            if avg_volume > 0:
                volume_ratio = current_volume / avg_volume
                if volume_ratio >= 2.0:  # 成交量是平均值的2倍以上
                    alerts.append({
                        "type": "HIGH_VOLUME",
                        "symbol": symbol,
                        "message": f"成交量异常: {volume_ratio:.2f}x 平均值",
                        "severity": "medium",
                        "timestamp": datetime.now().isoformat()
                    })
        except Exception as e:
            logger.error(f"Error checking volume anomalies for {symbol}: {str(e)}")
        
        return alerts
    
    def monitor_stocks(self, symbols: List[str]) -> List[Dict]:
        """监控股票列表的风险和机会"""
        all_alerts = []
        
        for symbol in symbols:
            try:
                # 获取当前价格
                stock_data = data_provider.get_stock_data(symbol, period='daily', days=1)
                if stock_data.empty:
                    continue
                
                current_price = stock_data.iloc[-1]['close']
                
                # 检查各种信号
                technical_alerts = self.check_technical_signals(symbol)
                price_alerts = self.check_price_alerts(symbol, current_price)
                volume_alerts = self.check_volume_anomalies(symbol)
                
                # 合并所有警报
                symbol_alerts = technical_alerts + price_alerts + volume_alerts
                
                for alert in symbol_alerts:
                    # 检查是否为重复警报（避免频繁推送）
                    is_duplicate = False
                    for existing in self.alerts[-10:]:  # 检查最近10个警报
                        if (existing['symbol'] == alert['symbol'] and 
                            existing['type'] == alert['type'] and
                            abs((datetime.fromisoformat(existing['timestamp']) - 
                                 datetime.fromisoformat(alert['timestamp'])).total_seconds()) < 300):  # 5分钟内
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        all_alerts.append(alert)
                        self.alerts.append(alert)
                        
            except Exception as e:
                logger.error(f"Error monitoring {symbol}: {str(e)}")
        
        return all_alerts

# 全球风险监控实例
risk_monitor = RiskMonitor()