// A股个股数据可视化 - 前端脚本
let currentData = null;
let priceChart, rsiChart, macdChart, bollingerChart, volumeChart;
const stockNames = {
    "600519.SH": "贵州茅台",
    "000001.SZ": "平安银行",
    "000858.SZ": "五粮液",
    "601318.SH": "中国平安",
    "600036.SH": "招商银行",
    "002594.SZ": "比亚迪",
    "601012.SH": "隆基绿能",
    "600900.SH": "长江电力",
    "601899.SH": "紫金矿业",
    "601888.SH": "中国中免"
};

document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    loadWatchlist();
    loadHotStocks();
    loadStockData();
});

// 下载CSV数据功能
function downloadData() {
    if (!currentData) {
        alert('请先加载数据');
        return;
    }
    
    const { data, symbol } = currentData;
    if (!data || data.length === 0) {
        alert('没有数据可下载');
        return;
    }
    
    // 构建CSV内容
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => 
            headers.map(header => {
                const value = row[header];
                return value === null || value === undefined ? '' : JSON.stringify(value);
            }).join(',')
        )
    ].join('\n');
    
    // 创建下载链接
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    const dateStr = new Date().toISOString().split('T')[0];
    link.setAttribute('href', url);
    link.setAttribute('download', `${symbol}_${dateStr}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function initCharts() {
    priceChart = echarts.init(document.getElementById('priceChart'));
    rsiChart = echarts.init(document.getElementById('rsiChart'));
    macdChart = echarts.init(document.getElementById('macdChart'));
    bollingerChart = echarts.init(document.getElementById('bollingerChart'));
    volumeChart = echarts.init(document.getElementById('volumeChart'));
    
    window.addEventListener('resize', function() {
        priceChart.resize();
        rsiChart.resize();
        macdChart.resize();
        bollingerChart.resize();
        volumeChart.resize();
    });
}

async function loadWatchlist() {
    try {
        const response = await fetch('/api/watchlist');
        const data = await response.json();
        if (data.success) {
            renderWatchlist(data.watchlist);
            updateStockSelect(data.watchlist);
        }
    } catch (error) {
        console.error('加载关注列表失败:', error);
    }
}

function renderWatchlist(watchlist) {
    const container = document.getElementById('watchlist');
    if (!watchlist || watchlist.length === 0) {
        container.innerHTML = '<div class="loading">暂无关注股票</div>';
        return;
    }
    
    container.innerHTML = watchlist.map(symbol => `
        <div class="watchlist-item" onclick="selectStock('${symbol}')">
            <span class="stock-code">${symbol}</span>
            <button class="remove-btn" onclick="event.stopPropagation(); removeFromWatchlist('${symbol}')">×</button>
        </div>
    `).join('');
}

function updateStockSelect(watchlist) {
    const select = document.getElementById('stockSelect');
    select.innerHTML = watchlist.map(symbol => 
        `<option value="${symbol}">${symbol} ${stockNames[symbol] || ''}</option>`
    ).join('');
}

async function loadHotStocks() {
    try {
        const response = await fetch('/api/stock/list');
        const data = await response.json();
        if (data.success) {
            renderHotStocks(data.stocks);
        }
    } catch (error) {
        console.error('加载热门股票失败:', error);
    }
}

function renderHotStocks(stocks) {
    const container = document.getElementById('hotStocks');
    container.innerHTML = stocks.map(stock => `
        <div class="stock-item" onclick="selectStock('${stock.code}')">
            <span class="stock-code">${stock.code}</span>
            <span>${stock.name}</span>
        </div>
    `).join('');
}

function selectStock(symbol) {
    document.getElementById('stockSelect').value = symbol;
    loadStockData();
}

async function addToWatchlist() {
    const input = document.getElementById('newStockInput');
    const symbol = input.value.trim();
    if (!symbol) return;
    
    try {
        const response = await fetch('/api/watchlist', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol })
        });
        const data = await response.json();
        if (data.success) {
            loadWatchlist();
            input.value = '';
        }
    } catch (error) {
        console.error('添加失败:', error);
    }
}

async function removeFromWatchlist(symbol) {
    try {
        const response = await fetch('/api/watchlist', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol })
        });
        const data = await response.json();
        if (data.success) {
            loadWatchlist();
        }
    } catch (error) {
        console.error('删除失败:', error);
    }
}

async function loadStockData() {
    const symbol = document.getElementById('stockSelect').value;
    const days = document.getElementById('periodSelect').value;
    const downloadBtn = document.getElementById('downloadBtn');
    
    try {
        // 显示加载状态
        downloadBtn.disabled = true;
        downloadBtn.textContent = '加载中...';
        
        const response = await fetch(`/api/stock/daily?symbol=${symbol}&days=${days}`);
        const data = await response.json();
        if (data.success) {
            currentData = data;
            updateStats(data.stats);
            renderCharts(data);
            // 启用下载按钮
            downloadBtn.disabled = false;
            downloadBtn.textContent = '下载数据';
        } else {
            alert('加载数据失败: ' + (data.error || '未知错误'));
            downloadBtn.textContent = '下载数据';
        }
    } catch (error) {
        console.error('加载数据失败:', error);
        alert('加载数据失败，请稍后重试');
        downloadBtn.textContent = '下载数据';
    }
}

function updateStats(stats) {
    if (!stats) return;
    
    const totalReturn = document.getElementById('totalReturn');
    totalReturn.textContent = stats.total_return.toFixed(2) + '%';
    totalReturn.className = 'card-value ' + (stats.total_return >= 0 ? 'positive' : 'negative');
    
    const avgReturn = document.getElementById('avgReturn');
    avgReturn.textContent = stats.avg_daily_return.toFixed(3) + '%';
    avgReturn.className = 'card-value ' + (stats.avg_daily_return >= 0 ? 'positive' : 'negative');
    
    document.getElementById('volatility').textContent = stats.std_dev.toFixed(2) + '%';
    document.getElementById('sharpe').textContent = stats.sharpe_ratio.toFixed(2);
}

function renderCharts(data) {
    const records = data.data;
    const dates = records.map(r => r.date);
    
    // 确定使用哪个字段
    const closeField = records[0].close !== undefined ? 'close' : '收盘';
    
    // 价格走势图
    renderPriceChart(dates, records, closeField);
    
    // RSI指标
    renderRSIChart(dates, records);
    
    // MACD指标
    renderMACDChart(dates, records);
    
    // 布林带
    renderBollingerChart(dates, records, closeField);
    
    // 成交量
    renderVolumeChart(dates, records, closeField);
}

function renderVolumeChart(dates, records, closeField) {
    // 确定成交量字段
    let volField = 'volume';
    if (records[0]['volume'] === undefined && records[0]['成交量'] !== undefined) {
        volField = '成交量';
    }
    
    // 计算柱状图颜色（涨跌）
    const volumeColors = records.map((record, index) => {
        if (index === 0) return '#3b82f6';
        const prevClose = records[index-1][closeField];
        const currClose = record[closeField];
        return currClose >= prevClose ? '#10b981' : '#ef4444';
    });
    
    const option = {
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: dates, boundaryGap: false },
        yAxis: { type: 'value', splitLine: { show: true } },
        series: [
            {
                name: '成交量',
                type: 'bar',
                data: records.map(r => r[volField]),
                itemStyle: {
                    color: function(params) {
                        return volumeColors[params.dataIndex];
                    }
                }
            }
        ]
    };
    volumeChart.setOption(option);
}

function renderPriceChart(dates, records, closeField) {
    const option = {
        tooltip: { trigger: 'axis' },
        legend: { data: ['收盘价', 'MA5', 'MA10', 'MA20'] },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: dates, boundaryGap: false },
        yAxis: { type: 'value' },
        series: [
            {
                name: '收盘价',
                type: 'line',
                data: records.map(r => r[closeField]),
                smooth: true,
                lineStyle: { width: 2, color: '#3b82f6' },
                itemStyle: { color: '#3b82f6' }
            },
            {
                name: 'MA5',
                type: 'line',
                data: records.map(r => r.ma5),
                smooth: true,
                lineStyle: { width: 1.5, color: '#10b981' },
                showSymbol: false
            },
            {
                name: 'MA10',
                type: 'line',
                data: records.map(r => r.ma10),
                smooth: true,
                lineStyle: { width: 1.5, color: '#f59e0b' },
                showSymbol: false
            },
            {
                name: 'MA20',
                type: 'line',
                data: records.map(r => r.ma20),
                smooth: true,
                lineStyle: { width: 1.5, color: '#ef4444' },
                showSymbol: false
            }
        ]
    };
    priceChart.setOption(option);
}

function renderRSIChart(dates, records) {
    const option = {
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: dates, boundaryGap: false },
        yAxis: { type: 'value', min: 0, max: 100, splitLine: { show: true } },
        visualMap: {
            show: false,
            pieces: [
                { lt: 30, color: '#10b981' },
                { gt: 70, color: '#ef4444' },
                { color: '#3b82f6' }
            ]
        },
        series: [
            {
                name: 'RSI',
                type: 'line',
                data: records.map(r => r.rsi),
                smooth: true,
                lineStyle: { width: 2 },
                markLine: {
                    data: [
                        { yAxis: 70, lineStyle: { color: '#ef4444', type: 'dashed' } },
                        { yAxis: 30, lineStyle: { color: '#10b981', type: 'dashed' } }
                    ],
                    label: { formatter: '{c}' }
                }
            }
        ]
    };
    rsiChart.setOption(option);
}

function renderMACDChart(dates, records) {
    const option = {
        tooltip: { trigger: 'axis' },
        legend: { data: ['MACD', 'Signal', 'Histogram'] },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: dates, boundaryGap: false },
        yAxis: { type: 'value' },
        series: [
            {
                name: 'MACD',
                type: 'line',
                data: records.map(r => r.macd),
                smooth: true,
                lineStyle: { width: 2, color: '#3b82f6' }
            },
            {
                name: 'Signal',
                type: 'line',
                data: records.map(r => r.signal),
                smooth: true,
                lineStyle: { width: 2, color: '#f59e0b' }
            },
            {
                name: 'Histogram',
                type: 'bar',
                data: records.map(r => r.histogram),
                itemStyle: {
                    color: function(params) {
                        return params.value >= 0 ? '#10b981' : '#ef4444';
                    }
                }
            }
        ]
    };
    macdChart.setOption(option);
}

function renderBollingerChart(dates, records, closeField) {
    const option = {
        tooltip: { trigger: 'axis' },
        legend: { data: ['收盘价', '上轨', '中轨', '下轨'] },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: dates, boundaryGap: false },
        yAxis: { type: 'value' },
        series: [
            {
                name: '收盘价',
                type: 'line',
                data: records.map(r => r[closeField]),
                smooth: true,
                lineStyle: { width: 2, color: '#3b82f6' }
            },
            {
                name: '上轨',
                type: 'line',
                data: records.map(r => r.bb_upper),
                smooth: true,
                lineStyle: { width: 1, color: '#ef4444', type: 'dashed' },
                showSymbol: false
            },
            {
                name: '中轨',
                type: 'line',
                data: records.map(r => r.bb_middle),
                smooth: true,
                lineStyle: { width: 1, color: '#f59e0b', type: 'dashed' },
                showSymbol: false
            },
            {
                name: '下轨',
                type: 'line',
                data: records.map(r => r.bb_lower),
                smooth: true,
                lineStyle: { width: 1, color: '#10b981', type: 'dashed' },
                showSymbol: false
            }
        ]
    };
    bollingerChart.setOption(option);
}
