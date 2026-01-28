"""
主应用模块
协调各个组件，实现完整的股票分析和监控系统
"""
import logging
import schedule
import time
from datetime import datetime, timedelta
import threading
import os
from typing import Dict, List

from config.settings import WATCHLIST, TRADING_HOURS_START, TRADING_HOURS_END, POST_MARKET_ANALYSIS_TIME
from data.data_provider import data_provider
from analysis.ai_analyzer import ai_analyzer
from monitoring.risk_monitor import risk_monitor
from notification.notification_service import notification_service

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockAnalysisSystem:
    def __init__(self):
        self.watchlist = WATCHLIST
        self.running = False
        self.trading_hours_start = TRADING_HOURS_START
        self.trading_hours_end = TRADING_HOURS_END
        self.post_market_time = POST_MARKET_ANALYSIS_TIME
    
    def is_trading_hour(self) -> bool:
        """检查是否在交易时间内"""
        current_time = datetime.now().strftime("%H:%M")
        return self.trading_hours_start <= current_time <= self.trading_hours_end
    
    def real_time_monitoring(self):
        """实时监控功能"""
        logger.info("开始实时监控...")
        
        while self.running:
            if self.is_trading_hour():
                logger.info("正在进行盘中监控...")
                
                # 监控股票风险和机会
                alerts = risk_monitor.monitor_stocks(self.watchlist)
                
                # 发送预警通知
                for alert in alerts:
                    logger.info(f"检测到预警: {alert['message']}")
                    notification_service.send_alert_notification(alert)
                
                # 每5分钟检查一次
                time.sleep(300)  # 5分钟
            else:
                logger.info("非交易时间，暂停实时监控...")
                # 非交易时间休眠更长时间
                time.sleep(600)  # 10分钟
    
    def daily_analysis(self):
        """每日分析功能（盘后）"""
        logger.info("开始盘后分析...")
        
        try:
            # 获取市场概览
            market_overview = data_provider.get_market_overview()
            market_overview_str = ""
            for index_name, data in market_overview.items():
                market_overview_str += f"- {index_name}: {data['close']:.2f} ({data['change_pct']:+.2f}%)\n"
            
            # 分析关注股票
            watched_stocks_analysis = ""
            for symbol in self.watchlist[:5]:  # 只分析前5只股票
                try:
                    analysis = ai_analyzer.analyze_stock(symbol)
                    if 'error' not in analysis:
                        watched_stocks_analysis += f"\n**{symbol}**:\n{analysis['analysis'][:200]}...\n"
                    else:
                        watched_stocks_analysis += f"\n**{symbol}**: 分析失败 - {analysis['error']}\n"
                except Exception as e:
                    watched_stocks_analysis += f"\n**{symbol}**: 分析错误 - {str(e)}\n"
            
            # 获取风险提醒
            risk_alerts = ""
            recent_alerts = risk_monitor.alerts[-10:]  # 最近10个警报
            if recent_alerts:
                for alert in recent_alerts:
                    risk_alerts += f"- {alert['symbol']}: {alert['message']} ({alert['severity']})\n"
            else:
                risk_alerts = "今日无重大风险提醒\n"
            
            # AI策略建议
            ai_strategies = ""
            for symbol in self.watchlist[:3]:  # 为前3只股票生成策略
                try:
                    strategy = ai_analyzer.generate_trading_strategy(symbol, "momentum")
                    if 'error' not in strategy:
                        ai_strategies += f"\n**{symbol}策略**: {strategy['strategy'][:150]}...\n"
                    else:
                        ai_strategies += f"\n**{symbol}策略**: 生成失败 - {strategy['error']}\n"
                except Exception as e:
                    ai_strategies += f"\n**{symbol}策略**: 生成错误 - {str(e)}\n"
            
            # 组织报告数据
            report_data = {
                'market_overview': market_overview_str,
                'watched_stocks_analysis': watched_stocks_analysis,
                'risk_alerts': risk_alerts,
                'ai_strategies': ai_strategies
            }
            
            # 发送每日报告
            notification_service.send_daily_report(report_data)
            logger.info("盘后分析报告发送完成")
            
        except Exception as e:
            logger.error(f"盘后分析执行失败: {str(e)}")
    
    def single_stock_analysis(self, symbol: str):
        """单只股票分析"""
        try:
            logger.info(f"开始分析股票: {symbol}")
            analysis = ai_analyzer.analyze_stock(symbol)
            
            if 'error' not in analysis:
                notification_service.send_stock_analysis(analysis)
                logger.info(f"股票 {symbol} 分析完成并发送通知")
            else:
                logger.error(f"股票 {symbol} 分析失败: {analysis['error']}")
        except Exception as e:
            logger.error(f"分析股票 {symbol} 时出错: {str(e)}")
    
    def market_sentiment_analysis(self):
        """市场情绪分析"""
        try:
            logger.info("开始市场情绪分析...")
            sentiment = ai_analyzer.analyze_market_sentiment(self.watchlist)
            
            if 'error' not in sentiment:
                notification_service.send_market_sentiment(sentiment)
                logger.info("市场情绪分析完成并发送通知")
            else:
                logger.error(f"市场情绪分析失败: {sentiment['error']}")
        except Exception as e:
            logger.error(f"市场情绪分析时出错: {str(e)}")
    
    def setup_schedule(self):
        """设置定时任务"""
        # 每天盘后分析
        schedule.every().monday.at(self.post_market_time).do(self.daily_analysis)
        schedule.every().tuesday.at(self.post_market_time).do(self.daily_analysis)
        schedule.every().wednesday.at(self.post_market_time).do(self.daily_analysis)
        schedule.every().thursday.at(self.post_market_time).do(self.daily_analysis)
        schedule.every().friday.at(self.post_market_time).do(self.daily_analysis)
        
        # 每周一早上进行市场情绪分析
        schedule.every().monday.at("09:00").do(self.market_sentiment_analysis)
        
        # 每小时检查是否有新任务
        schedule.every().hour.do(self.check_scheduled_tasks)
        
        logger.info("定时任务设置完成")
    
    def check_scheduled_tasks(self):
        """检查并执行定时任务"""
        schedule.run_pending()
    
    def start_monitoring_thread(self):
        """启动监控线程"""
        monitor_thread = threading.Thread(target=self.real_time_monitoring, daemon=True)
        monitor_thread.start()
        return monitor_thread
    
    def run(self):
        """运行系统"""
        logger.info("启动股票分析系统...")
        
        self.running = True
        
        # 设置定时任务
        self.setup_schedule()
        
        # 启动实时监控线程
        monitor_thread = self.start_monitoring_thread()
        
        logger.info("系统已启动，开始监控...")
        
        try:
            while self.running:
                # 执行定时任务
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次定时任务
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭系统...")
            self.stop()
        except Exception as e:
            logger.error(f"系统运行出错: {str(e)}")
            self.stop()
    
    def stop(self):
        """停止系统"""
        logger.info("正在停止系统...")
        self.running = False
        logger.info("系统已停止")

# 创建全局系统实例
stock_system = StockAnalysisSystem()

if __name__ == "__main__":
    # 如果直接运行此脚本，则启动系统
    stock_system.run()