#!/usr/bin/env python3
"""
测试修复后的stock-for-laowang项目功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试基本导入功能"""
    print("测试基本导入功能...")
    try:
        from web.app import app
        print("✓ Web应用模块导入成功")
    except Exception as e:
        print(f"✗ Web应用模块导入失败: {e}")
        return False
    
    try:
        from data.data_provider import data_provider
        print("✓ 数据提供者模块导入成功")
    except Exception as e:
        print(f"✗ 数据提供者模块导入失败: {e}")
        return False
    
    try:
        from analysis.ai_analyzer import ai_analyzer
        print("✓ AI分析器模块导入成功")
    except Exception as e:
        print(f"✗ AI分析器模块导入失败: {e}")
        return False
    
    try:
        from main import stock_system
        print("✓ 主系统模块导入成功")
    except Exception as e:
        print(f"✗ 主系统模块导入失败: {e}")
        return False
    
    return True

def test_data_provider():
    """测试数据提供者功能"""
    print("\n测试数据提供者功能...")
    try:
        from data.data_provider import data_provider
        
        # 测试获取简单数据（使用上证指数）
        sample_symbol = "000001.XSHG"
        data = data_provider.get_stock_data(sample_symbol, period='daily', days=5)
        
        if not data.empty:
            print(f"✓ 成功获取 {sample_symbol} 的数据，共 {len(data)} 条记录")
            print(f"  数据列: {list(data.columns)}")
            if 'close' in data.columns:
                print(f"  最新收盘价: {data['close'].iloc[-1]:.2f}")
            return True
        else:
            print(f"✗ 未能获取 {sample_symbol} 的数据")
            return False
            
    except Exception as e:
        print(f"✗ 数据提供者功能测试失败: {e}")
        return False

def test_api_endpoints():
    """测试API端点功能"""
    print("\n测试API端点功能...")
    try:
        from web.app import get_stock_data
        import json
        
        # 创建一个简单的测试请求
        def mock_request(symbol="000001.XSHG"):
            from data.data_provider import data_provider
            stock_data = data_provider.get_stock_data(symbol, period='daily', days=5)
            if not stock_data.empty:
                data = {
                    'dates': stock_data.index.strftime('%Y-%m-%d').tolist(),
                    'close': stock_data['close'].round(2).tolist(),
                    'open': stock_data['open'].round(2).tolist(),
                    'high': stock_data['high'].round(2).tolist(),
                    'low': stock_data['low'].round(2).tolist(),
                    'volume': stock_data['volume'].tolist() if 'volume' in stock_data.columns and stock_data['volume'].notna().any() else []
                }
                return data
            else:
                return {'error': '未能获取数据'}
        
        result = mock_request()
        if 'error' not in result:
            print("✓ API端点功能正常")
            print(f"  返回数据长度: {len(result['dates'])}")
            return True
        else:
            print(f"✗ API端点功能异常: {result['error']}")
            return False
            
    except Exception as e:
        print(f"✗ API端点功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试stock-for-laowang项目修复...")
    print("="*50)
    
    # 检查API密钥是否配置
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key or api_key == "your_deepseek_api_key_here":
        print("⚠️  警告: DEEPSEEK_API_KEY 未正确配置，AI分析功能将不可用")
        print("   请在 .env 文件中设置有效的API密钥")
    else:
        print("✓ DEEPSEEK_API_KEY 已配置")
    
    # 运行各项测试
    tests = [
        test_imports,
        test_data_provider,
        test_api_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
        else:
            print(f"  (测试 {test_func.__name__} 失败)")
    
    print("\n" + "="*50)
    print(f"测试完成: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！项目功能修复成功。")
        print("\n启动命令:")
        print("  cd /Users/wangxuhui/clawd/stock-for-laowang")
        print("  ./start.sh --web")
        print("\n访问地址: http://localhost:5001")
    else:
        print(f"⚠️  {total-passed} 项测试失败，需要进一步修复。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)