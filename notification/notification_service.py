"""
通知模块
负责发送风险提醒和分析报告
"""
import requests
import json
import logging
from typing import Dict, List
from datetime import datetime

from config.settings import NOTIFICATION_CHANNELS
from analysis.ai_analyzer import ai_analyzer

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.enabled_channels = []
        if NOTIFICATION_CHANNELS.get("wechat_work"):
            self.enabled_channels.append("wechat_work")
        if NOTIFICATION_CHANNELS.get("telegram", {}).get("bot_token"):
            self.enabled_channels.append("telegram")
    
    def send_wechat_work_message(self, title: str, content: str):
        """发送企业微信消息"""
        webhook_url = NOTIFICATION_CHANNELS.get("wechat_work")
        if not webhook_url:
            logger.warning("企业微信Webhook URL未配置")
            return False
        
        try:
            # 企业微信消息格式
            message = {
                "msgtype": "markdown",
                "markdown": {
                    "content": f"### {title}\n\n{content}"
                }
            }
            
            response = requests.post(webhook_url, json=message, timeout=10)
            response.raise_for_status()
            logger.info(f"企业微信消息发送成功: {title}")
            return True
        except Exception as e:
            logger.error(f"企业微信消息发送失败: {str(e)}")
            return False
    
    def send_telegram_message(self, content: str):
        """发送Telegram消息"""
        telegram_config = NOTIFICATION_CHANNELS.get("telegram", {})
        bot_token = telegram_config.get("bot_token")
        chat_id = telegram_config.get("chat_id")
        
        if not bot_token or not chat_id:
            logger.warning("Telegram Bot Token或Chat ID未配置")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            message = {
                "chat_id": chat_id,
                "text": content,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=message, timeout=10)
            response.raise_for_status()
            logger.info(f"Telegram消息发送成功")
            return True
        except Exception as e:
            logger.error(f"Telegram消息发送失败: {str(e)}")
            return False
    
    def send_alert_notification(self, alert: Dict):
        """发送预警通知"""
        title = f"🚨 {alert['type']} - {alert['symbol']}"
        content = f"**{alert['message']}**\n\n严重性: {alert['severity']}\n时间: {alert['timestamp']}"
        
        success_count = 0
        for channel in self.enabled_channels:
            if channel == "wechat_work":
                if self.send_wechat_work_message(title, content):
                    success_count += 1
            elif channel == "telegram":
                if self.send_telegram_message(content):
                    success_count += 1
        
        return success_count > 0
    
    def send_daily_report(self, report_data: Dict):
        """发送每日报告"""
        title = f"📊 {datetime.now().strftime('%Y-%m-%d')} 盘后分析报告"
        
        content = f"""
### 📊 {datetime.now().strftime('%Y-%m-%d')} 盘后分析报告

#### 市场概览
{report_data.get('market_overview', '暂无数据')}

#### 重点关注股票
{report_data.get('watched_stocks_analysis', '暂无分析')}

#### 风险提醒
{report_data.get('risk_alerts', '今日无重大风险提醒')}

#### AI策略建议
{report_data.get('ai_strategies', '暂无策略建议')}

---
报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        success_count = 0
        for channel in self.enabled_channels:
            if channel == "wechat_work":
                if self.send_wechat_work_message(title, content):
                    success_count += 1
            elif channel == "telegram":
                if self.send_telegram_message(content):
                    success_count += 1
        
        return success_count > 0
    
    def send_stock_analysis(self, analysis_result: Dict):
        """发送股票分析结果"""
        symbol = analysis_result.get('symbol', 'Unknown')
        current_price = analysis_result.get('current_price', 'N/A')
        recommendation = analysis_result.get('recommendation', 'N/A')
        
        title = f"🔍 {symbol} AI分析报告"
        content = f"""
### 📈 {symbol} AI分析报告

**当前价格**: ¥{current_price}
**AI建议**: {recommendation}

#### 分析详情:
{analysis_result.get('analysis', '暂无分析内容')}

---
分析时间: {analysis_result.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
        """.strip()
        
        success_count = 0
        for channel in self.enabled_channels:
            if channel == "wechat_work":
                if self.send_wechat_work_message(title, content):
                    success_count += 1
            elif channel == "telegram":
                if self.send_telegram_message(content):
                    success_count += 1
        
        return success_count > 0
    
    def send_market_sentiment(self, sentiment_data: Dict):
        """发送市场情绪分析"""
        title = "📉 市场情绪分析"
        content = f"""
### 📊 市场情绪分析

{sentiment_data.get('analysis', '暂无分析内容')}

---
分析时间: {sentiment_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
        """.strip()
        
        success_count = 0
        for channel in self.enabled_channels:
            if channel == "wechat_work":
                if self.send_wechat_work_message(title, content):
                    success_count += 1
            elif channel == "telegram":
                if self.send_telegram_message(content):
                    success_count += 1
        
        return success_count > 0

# 全局通知服务实例
notification_service = NotificationService()