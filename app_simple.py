#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股个股数据可视化 - 简化版
"""
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A股个股数据可视化</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        header { 
            text-align: center; 
            color: white; 
            padding: 30px 0;
        }
        h1 { font-size: 2.5rem; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
        .subtitle { opacity: 0.9; }
        .controls { 
            background: white; 
            padding: 20px; 
            border-radius: 12px; 
            margin-bottom: 20px;
            display: flex; gap: 20px; align-items: center; flex-wrap: wrap;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        }
        select, button { 
            padding: 10px 15px; 
            border: 1px solid #e5e7eb; 
            border-radius: 6px; 
            font-size: 1rem;
            cursor: pointer;
        }
        button { 
            background: #3b82f6; 
            color: white; 
            border: none; 
            transition: all 0.3s ease;
        }
        button:hover { background: #2563eb; transform: translateY(-2px); }
        .stats { 
            display: grid; 
            grid-template-columns: repeat(4, 1fr); 
            gap: 15px; 
            margin-bottom: 20px;
        }
        .stat-card { 
            background: white; 
            padding: 20px; 
            border-radius: 12px; 
            text-align: center;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        }
        .stat-label { color: #6b7280; font-size: 0.9rem; margin-bottom: 8px; }
        .stat-value { font-size: 1.5rem; font-weight: 700; }
        .positive { color: #10b981; }
        .negative { color: #ef4444; }
        .charts { 
            display: grid; 
            gap: 20px;
        }
        .chart-card { 
            background: white; 
            padding: 20px; 
            border-radius: 12px;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        }
        .chart-card h3 { margin-bottom: 15px; color: #1f2937; }
        .chart { width: 100%; height: 350px; }
        .two-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 768px) {
            .stats { grid-template-columns: repeat(2, 1fr); }
            .two-cols { grid-template-columns: 1fr; }
            h1 { font-size: 1.8rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📈 A股个股数据可视化</h1>
            <p class="subtitle">专业的股票数据分析工具</p>
        </header>
        
        <div class="controls">
            <label>选择股票:</label>
            <select id="stockSelect">
                <option value="600519.SH">600519.SH 贵州茅台</option>
                <option value="000001.SZ">000001.SZ 平安银行</option>
                <option value="000858.SZ">000858.SZ 五粮液</option>
                <option value="002594.SZ">002594.SZ 比亚迪</option>
            </select>
            <label>时间周期:</label>
            <select id="periodSelect">
                <option value="30">30天</option>
                <option value="90">90天</option>
                <option value="180">180天</option>
                <option value="365" selected>1年</option>
            </select>
            <button onclick="loadData()">刷新数据</button>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">总收益率</div>
                <div class="stat-value" id="totalReturn">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">日均收益率</div>
                <div class="stat-value" id="avgReturn">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">波动率</div>
                <div class="stat-value" id="volatility">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">夏普比率</div>
                <div class="stat-value" id="sharpe">-</div>
            </div>
        </div>
        
        <div class="charts">
            <div class="chart-card">
                <h3>📊 价格走势与均线</h3>
                <div id="priceChart" class="chart"></div>
            </div>
            
            <div class="two-cols">
                <div class="chart-card">
                    <h3>📉 RSI指标</h3>
                    <div id="rsiChart" class="chart"></div>
                </div>
                <div class="chart-card">
                    <h3>📊 MACD指标</h3>
                    <div id="macdChart" class="chart"></div>
                </div>
            </div>
            
            <div class="chart-card">
                <h3>📈 布林带</h3>
                <div id="bollingerChart" class="chart"></div>
            </div>
        </div>
    </div>
    
    <script>
        let priceChart, rsiChart, macdChart, bollingerChart;
        const data = {{ data | tojson }};
        
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
            renderData(data);
        });
        
        function initCharts() {
            priceChart = echarts.init(document.getElementById('priceChart'));
            rsiChart = echarts.init(document.getElementById('rsiChart'));
            macdChart = echarts.init(document.getElementById('macdChart'));
            bollingerChart = echarts.init(document.getElementById('bollingerChart'));
            
            window.addEventListener('resize', function() {
                priceChart.resize();
                rsiChart.resize();
                macdChart.resize();
                bollingerChart.resize();
            });
        }
        
        function loadData() {
            alert('本演示使用模拟数据，真实数据请运行main.py');
        }
        
        function renderData(data) {
            const stats = data.stats;
            const records = data.data;
            const dates = records.map(r => r.date);
            
            document.getElementById('totalReturn').textContent = stats.total_return.toFixed(2) + '%';
            document.getElementById('totalReturn').className = 'stat-value ' + (stats.total_return >= 0 ? 'positive' : 'negative');
            document.getElementById('avgReturn').textContent = stats.avg_daily_return.toFixed(3) + '%';
            document.getElementById('avgReturn').className = 'stat-value ' + (stats.avg_daily_return >= 0 ? 'positive' : 'negative');
            document.getElementById('volatility').textContent = stats.std_dev.toFixed(2) + '%';
            document.getElementById('sharpe').textContent = stats.sharpe_ratio.toFixed(2);
            
            renderPriceChart(dates, records);
            renderRSIChart(dates, records);
            renderMACDChart(dates, records);
            renderBollingerChart(dates, records);
        }
        
        function renderPriceChart(dates, records) {
            priceChart.setOption({
                tooltip: { trigger: 'axis' },
                legend: { data: ['收盘价', 'MA5', 'MA10', 'MA20'] },
                grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
                xAxis: { type: 'category', data: dates, boundaryGap: false },
                yAxis: { type: 'value' },
                series: [
                    { name: '收盘价', type: 'line', data: records.map(r => r.close), smooth: true, lineStyle: { width: 2, color: '#3b82f6' } },
                    { name: 'MA5', type: 'line', data: records.map(r => r.ma5), smooth: true, lineStyle: { width: 1.5, color: '#10b981' }, showSymbol: false },
                    { name: 'MA10', type: 'line', data: records.map(r => r.ma10), smooth: true, lineStyle: { width: 1.5, color: '#f59e0b' }, showSymbol: false },
                    { name: 'MA20', type: 'line', data: records.map(r => r.ma20), smooth: true, lineStyle: { width: 1.5, color: '#ef4444' }, showSymbol: false }
                ]
            });
        }
        
        function renderRSIChart(dates, records) {
            rsiChart.setOption({
                tooltip: { trigger: 'axis' },
                grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
                xAxis: { type: 'category', data: dates, boundaryGap: false },
                yAxis: { type: 'value', min: 0, max: 100 },
                series: [{
                    name: 'RSI', type: 'line', data: records.map(r => r.rsi), smooth: true, lineStyle: { width: 2 },
                    markLine: { data: [
                        { yAxis: 70, lineStyle: { color: '#ef4444', type: 'dashed' } },
                        { yAxis: 30, lineStyle: { color: '#10b981', type: 'dashed' } }
                    ]}
                }]
            });
        }
        
        function renderMACDChart(dates, records) {
            macdChart.setOption({
                tooltip: { trigger: 'axis' },
                legend: { data: ['MACD', 'Signal', 'Histogram'] },
                grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
                xAxis: { type: 'category', data: dates, boundaryGap: false },
                yAxis: { type: 'value' },
                series: [
                    { name: 'MACD', type: 'line', data: records.map(r => r.macd), smooth: true, lineStyle: { width: 2, color: '#3b82f6' } },
                    { name: 'Signal', type: 'line', data: records.map(r => r.signal), smooth: true, lineStyle: { width: 2, color: '#f59e0b' } },
                    { name: 'Histogram', type: 'bar', data: records.map(r => r.histogram), itemStyle: { color: function(p) { return p.value >= 0 ? '#10b981' : '#ef4444'; } } }
                ]
            });
        }
        
        function renderBollingerChart(dates, records) {
            bollingerChart.setOption({
                tooltip: { trigger: 'axis' },
                legend: { data: ['收盘价', '上轨', '中轨', '下轨'] },
                grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
                xAxis: { type: 'category', data: dates, boundaryGap: false },
                yAxis: { type: 'value' },
                series: [
                    { name: '收盘价', type: 'line', data: records.map(r => r.close), smooth: true, lineStyle: { width: 2, color: '#3b82f6' } },
                    { name: '上轨', type: 'line', data: records.map(r => r.bb_upper), smooth: true, lineStyle: { width: 1, color: '#ef4444', type: 'dashed' }, showSymbol: false },
                    { name: '中轨', type: 'line', data: records.map(r => r.bb_middle), smooth: true, lineStyle: { width: 1, color: '#f59e0b', type: 'dashed' }, showSymbol: false },
                    { name: '下轨', type: 'line', data: records.map(r => r.bb_lower), smooth: true, lineStyle: { width: 1, color: '#10b981', type: 'dashed' }, showSymbol: false }
                ]
            });
        }
    </script>
</body>
</html>
'''

def generate_mock_data():
    """生成模拟数据"""
    days = 100
    base_price = 1000.0
    dates = []
    data = []
    
    current_price = base_price
    for i in range(days):
        date = (datetime.now() - timedelta(days=days - i)).strftime('%Y-%m-%d')
        dates.append(date)
        
        change = np.random.normal(0.001, 0.02)
        current_price = current_price * (1 + change)
        
        data.append({
            'date': date,
            'open': current_price * (1 + np.random.normal(0, 0.01)),
            'high': current_price * (1 + np.random.normal(0, 0.02)),
            'low': current_price * (1 - np.random.normal(0, 0.02)),
            'close': current_price
        })
    
    # 计算技术指标
    df = pd.DataFrame(data)
    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma10'] = df['close'].rolling(window=10).mean()
    df['ma20'] = df['close'].rolling(window=20).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    df['ema_fast'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = df['ema_fast'] - df['ema_slow']
    df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['histogram'] = df['macd'] - df['signal']
    
    # 布林带
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    df['bb_std'] = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
    df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
    
    # 统计数据
    daily_returns = df['close'].pct_change().dropna()
    stats = {
        'total_return': float((df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100),
        'avg_daily_return': float(daily_returns.mean() * 100),
        'std_dev': float(daily_returns.std() * 100),
        'sharpe_ratio': float((daily_returns.mean() / daily_returns.std()) * np.sqrt(252)) if daily_returns.std() != 0 else 0,
        'days': days
    }
    
    return {
        'data': df.to_dict('records'),
        'stats': stats
    }

@app.route('/')
def index():
    mock_data = generate_mock_data()
    return render_template_string(HTML_TEMPLATE, data=mock_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
