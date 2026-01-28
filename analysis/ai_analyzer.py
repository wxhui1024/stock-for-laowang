"""
AI分析模块
使用DeepSeek API进行股票分析和策略建议
"""
import openai
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from config.settings import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from data.data_provider import data_provider

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        if not DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY is not set in environment variables")
        
        # 配置OpenAI客户端使用DeepSeek API
        self.client = openai.OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )
        self.model = DEEPSEEK_MODEL

    def analyze_stock(self, symbol: str, additional_context: str = "") -> Dict:
        """
        使用AI分析单个股票
        :param symbol: 股票代码
        :param additional_context: 额外上下文信息
        :return: AI分析结果
        """
        try:
            # 获取股票数据
            stock_data = data_provider.get_stock_data(symbol, period='daily', days=30)
            if stock_data.empty:
                return {"error": f"No data available for {symbol}"}
            
            # 准备数据给AI分析
            recent_data = stock_data.tail(10).to_dict('records')
            latest_price = recent_data[-1]['close']
            
            # 构建分析提示
            prompt = f"""
            请对股票 {symbol} 进行详细分析，基于以下数据：
            
            最近10个交易日数据：
            {json.dumps(recent_data, indent=2, default=str)}
            
            当前价格: {latest_price}
            
            请提供以下分析：
            1. 技术面分析（趋势、支撑位、阻力位等）
            2. 短期走势预测（未来1-5个交易日）
            3. 投资建议（买入/持有/卖出）
            4. 风险提示
            5. 目标价位和止损位
            
            请使用简洁明确的语言，避免模糊表达。
            """
            
            if additional_context:
                prompt += f"\n额外上下文: {additional_context}"
            
            # 调用DeepSeek API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的股票分析师，提供准确、客观的分析和建议。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            analysis_result = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "analysis": response.choices[0].message.content,
                "current_price": latest_price,
                "recommendation": self._extract_recommendation(response.choices[0].message.content)
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {str(e)}")
            return {"error": f"Analysis failed for {symbol}: {str(e)}"}

    def _extract_recommendation(self, analysis_text: str) -> str:
        """
        从AI分析文本中提取投资建议
        """
        analysis_lower = analysis_text.lower()
        
        if "买入" in analysis_text or "buy" in analysis_lower:
            return "BUY"
        elif "卖出" in analysis_text or "sell" in analysis_lower:
            return "SELL"
        else:
            return "HOLD"

    def analyze_market_sentiment(self, symbols: List[str]) -> Dict:
        """
        分析市场情绪和整体趋势
        :param symbols: 股票代码列表
        :return: 市场情绪分析结果
        """
        try:
            # 获取各股票数据
            market_data = {}
            for symbol in symbols:
                stock_data = data_provider.get_stock_data(symbol, period='daily', days=5)
                if not stock_data.empty:
                    latest = stock_data.iloc[-1]
                    prev = stock_data.iloc[-2] if len(stock_data) > 1 else latest
                    change_pct = ((latest['close'] - prev['close']) / prev['close']) * 100 if prev['close'] != 0 else 0
                    market_data[symbol] = {
                        "current_price": latest['close'],
                        "change_pct": change_pct,
                        "volume": latest['volume']
                    }
            
            prompt = f"""
            基于以下市场数据，请分析整体市场情绪和趋势：
            
            股票表现数据：
            {json.dumps(market_data, indent=2, default=str)}
            
            请提供：
            1. 整体市场情绪（乐观/悲观/中性）
            2. 主要趋势判断
            3. 风险因素
            4. 投资策略建议
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位资深的市场分析师，提供专业的市场情绪和趋势分析。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return {
                "timestamp": datetime.now().isoformat(),
                "analysis": response.choices[0].message.content,
                "market_data_summary": market_data
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market sentiment: {str(e)}")
            return {"error": f"Market sentiment analysis failed: {str(e)}"}

    def generate_trading_strategy(self, symbol: str, strategy_type: str = "momentum") -> Dict:
        """
        生成特定类型的交易策略
        :param symbol: 股票代码
        :param strategy_type: 策略类型（momentum, mean_reversion, breakout等）
        :return: 交易策略
        """
        try:
            stock_data = data_provider.get_stock_data(symbol, period='daily', days=60)
            if stock_data.empty:
                return {"error": f"No data available for {symbol}"}
            
            prompt = f"""
            为股票 {symbol} 设计一个{strategy_type}类型的交易策略，基于以下数据：
            
            最近60个交易日数据：
            {json.dumps(stock_data.tail(10).to_dict('records'), indent=2, default=str)}
            
            请提供：
            1. 策略逻辑和入场条件
            2. 出场条件和止损设置
            3. 风险管理措施
            4. 预期收益率和最大回撤
            5. 具体操作建议
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的量化交易策略师，设计实用有效的交易策略。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=1200
            )
            
            return {
                "symbol": symbol,
                "strategy_type": strategy_type,
                "timestamp": datetime.now().isoformat(),
                "strategy": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Error generating strategy for {symbol}: {str(e)}")
            return {"error": f"Strategy generation failed for {symbol}: {str(e)}"}

# 全局AI分析器实例
ai_analyzer = AIAnalyzer()