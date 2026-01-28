#!/bin/bash
# stock-for-laowang 启动脚本

echo "老王股票分析系统启动脚本"
echo "========================"

if [ "$1" == "--web" ]; then
    echo "启动Web界面模式..."
    python3 main.py --web
elif [ "$1" == "--monitor" ]; then
    echo "启动监控模式..."
    python3 main.py
else
    echo "用法:"
    echo "  ./start.sh --web      启动Web界面 (默认端口5001)"
    echo "  ./start.sh --monitor  启动监控模式"
    echo ""
    echo "Web界面访问地址: http://localhost:5001"
    echo ""
    read -p "按任意键启动Web界面模式 (或 Ctrl+C 取消)..."
    python3 main.py --web
fi