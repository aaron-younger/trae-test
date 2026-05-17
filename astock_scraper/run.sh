#!/bin/bash

echo "======================================"
echo "   A股数据采集分析系统启动器"
echo "======================================"
echo ""

show_menu() {
    echo "请选择操作:"
    echo "1) 启动 Web 服务 (Flask)"
    echo "2) 运行数据采集 (CLI)"
    echo "3) 查看行业统计"
    echo "4) 列出已采集股票"
    echo "5) 退出"
    echo ""
}

start_web() {
    echo "正在启动 Web 服务..."
    echo "服务地址: http://localhost:5000"
    echo "按 Ctrl+C 停止服务"
    echo ""
    cd "$(dirname "$0")"
    python -m web.app
}

run_scrape() {
    echo "正在运行数据采集..."
    echo "采集样本股票: 000001, 000002, 600519, 000858, 601318"
    echo ""
    cd "$(dirname "$0")"
    python cli/main.py scrape -C "000001,000002,600519,000858,601318" --save --analyze
}

show_industries() {
    echo "行业统计:"
    echo ""
    cd "$(dirname "$0")"
    python cli/main.py industries
}

list_stocks() {
    echo "股票列表:"
    echo ""
    cd "$(dirname "$0")"
    python cli/main.py list --limit 20
}

while true; do
    show_menu
    read -p "请输入选项 [1-5]: " choice
    echo ""
    
    case $choice in
        1) start_web ;;
        2) run_scrape ;;
        3) show_industries ;;
        4) list_stocks ;;
        5) echo "再见!"; exit 0 ;;
        *) echo "无效选项，请重新选择" ;;
    esac
    echo ""
done
