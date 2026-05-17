#!/bin/bash

@echo off
chcp 65001 > nul
echo ======================================
echo    A股数据采集分析系统启动器
echo ======================================
echo.

:menu
echo 请选择操作:
echo 1) 启动 Web 服务 (Flask)
echo 2) 运行数据采集 (CLI)
echo 3) 查看行业统计
echo 4) 列出已采集股票
echo 5) 退出
echo.
set /p choice=请输入选项 [1-5]:

if "%choice%"=="1" goto start_web
if "%choice%"=="2" goto run_scrape
if "%choice%"=="3" goto show_industries
if "%choice%"=="4" goto list_stocks
if "%choice%"=="5" goto end
echo 无效选项，请重新选择
echo.
goto menu

:start_web
echo 正在启动 Web 服务...
echo 服务地址: http://localhost:5000
echo 按 Ctrl+C 停止服务
echo.
python -m web.app
goto :eof

:run_scrape
echo 正在运行数据采集...
echo 采集样本股票: 000001, 000002, 600519, 000858, 601318
echo.
python cli/main.py scrape -C "000001,000002,600519,000858,601318" --save --analyze
echo.
pause
goto menu

:show_industries
echo 行业统计:
echo.
python cli/main.py industries
echo.
pause
goto menu

:list_stocks
echo 股票列表:
echo.
python cli/main.py list --limit 20
echo.
pause
goto menu

:end
echo 再见!
