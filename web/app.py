"""
Web界面模块
提供可视化的股票监控和管理界面
"""
import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import threading
import time

from config.settings import WATCHLIST
from main import stock_system
from data.data_provider import data_provider
from analysis.ai_analyzer import ai_analyzer

app = Flask(__name__)
CORS(app)

# 全局变量存储当前监控的股票列表
current_watchlist = WATCHLIST.copy()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html', watchlist=current_watchlist)

@app.route('/dashboard')
def dashboard():
    """数据看板"""
    return render_template('dashboard.html')

@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    """获取监控列表"""
    return jsonify(current_watchlist)

@app.route('/api/watchlist', methods=['POST'])
def add_to_watchlist():
    """添加股票到监控列表"""
    data = request.get_json()
    symbol = data.get('symbol')
    name = data.get('name', '')
    
    if symbol and symbol not in current_watchlist:
        current_watchlist.append(symbol)
        return jsonify({'success': True, 'message': f'{symbol} 已添加到监控列表'})
    
    return jsonify({'success': False, 'message': '股票已在监控列表中或无效代码'})

@app.route('/api/watchlist/<symbol>', methods=['DELETE'])
def remove_from_watchlist(symbol):
    """从监控列表删除股票"""
    if symbol in current_watchlist:
        current_watchlist.remove(symbol)
        return jsonify({'success': True, 'message': f'{symbol} 已从监控列表移除'})
    
    return jsonify({'success': False, 'message': '股票不在监控列表中'})

@app.route('/api/stock/<symbol>/data')
def get_stock_data(symbol):
    """获取股票数据"""
    try:
        # 获取最近30天的数据
        stock_data = data_provider.get_stock_data(symbol, period='daily', days=30)
        if not stock_data.empty:
            # 转换为JSON格式
            data = {
                'dates': stock_data.index.strftime('%Y-%m-%d').tolist(),
                'close': stock_data['close'].tolist(),
                'open': stock_data['open'].tolist(),
                'high': stock_data['high'].tolist(),
                'low': stock_data['low'].tolist(),
                'volume': stock_data['volume'].tolist() if 'volume' in stock_data.columns else []
            }
            return jsonify(data)
        else:
            return jsonify({'error': '未能获取数据'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/<symbol>/analyze')
def analyze_stock(symbol):
    """AI分析股票"""
    try:
        analysis = ai_analyzer.analyze_stock(symbol)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts')
def get_alerts():
    """获取最新警报"""
    # 返回最近的警报
    recent_alerts = getattr(stock_system.risk_monitor, 'alerts', [])[-10:]
    return jsonify(recent_alerts)

def run_web_app():
    """运行Web应用"""
    app.run(debug=True, host='0.0.0.0', port=5001)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)