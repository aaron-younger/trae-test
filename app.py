#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股个股数据可视化Web应用 - 后端服务器
"""

import os
import json
import datetime
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np

try:
    import akshare as ak
except ImportError:
    print("警告: akshare未安装，部分功能可能不可用")

app = Flask(__name__)
CORS(app)

DATA_DIR = "data"
CONFIG_FILE = "config.json"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def load_config():
    """加载配置"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tushare_token": "", "last_update": "", "watchlist": ["600519.SH", "000001.SZ"]}


def save_config(config):
    """保存配置"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def convert_symbol(symbol):
    """转换股票代码格式"""
    if symbol.endswith(".SH"):
        return "sh" + symbol.replace(".SH", "")
    elif symbol.endswith(".SZ"):
        return "sz" + symbol.replace(".SZ", "")
    return symbol


def calculate_indicators(df):
    """计算技术指标"""
    if df is None or df.empty:
        return df
    
    df = df.copy()
    
    if "close" in df.columns:
        # 移动平均线
        df["ma5"] = df["close"].rolling(window=5).mean()
        df["ma10"] = df["close"].rolling(window=10).mean()
        df["ma20"] = df["close"].rolling(window=20).mean()
        df["ma60"] = df["close"].rolling(window=60).mean()
        
        # RSI
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))
        
        # MACD
        df["ema_fast"] = df["close"].ewm(span=12, adjust=False).mean()
        df["ema_slow"] = df["close"].ewm(span=26, adjust=False).mean()
        df["macd"] = df["ema_fast"] - df["ema_slow"]
        df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()
        df["histogram"] = df["macd"] - df["signal"]
        
        # 布林带
        df["bb_middle"] = df["close"].rolling(window=20).mean()
        df["bb_std"] = df["close"].rolling(window=20).std()
        df["bb_upper"] = df["bb_middle"] + (df["bb_std"] * 2)
        df["bb_lower"] = df["bb_middle"] - (df["bb_std"] * 2)
        
        # 收益率
        df["daily_return"] = df["close"].pct_change()
        df["cumulative_return"] = (1 + df["daily_return"]).cumprod() - 1
    
    elif "收盘" in df.columns:
        # 移动平均线
        df["ma5"] = df["收盘"].rolling(window=5).mean()
        df["ma10"] = df["收盘"].rolling(window=10).mean()
        df["ma20"] = df["收盘"].rolling(window=20).mean()
        df["ma60"] = df["收盘"].rolling(window=60).mean()
        
        # RSI
        delta = df["收盘"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["rsi"] = 100 - (100 / (1 + rs))
        
        # MACD
        df["ema_fast"] = df["收盘"].ewm(span=12, adjust=False).mean()
        df["ema_slow"] = df["收盘"].ewm(span=26, adjust=False).mean()
        df["macd"] = df["ema_fast"] - df["ema_slow"]
        df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()
        df["histogram"] = df["macd"] - df["signal"]
        
        # 布林带
        df["bb_middle"] = df["收盘"].rolling(window=20).mean()
        df["bb_std"] = df["收盘"].rolling(window=20).std()
        df["bb_upper"] = df["bb_middle"] + (df["bb_std"] * 2)
        df["bb_lower"] = df["bb_middle"] - (df["bb_std"] * 2)
        
        # 收益率
        df["daily_return"] = df["收盘"].pct_change()
        df["cumulative_return"] = (1 + df["daily_return"]).cumprod() - 1
    
    return df


def get_summary_stats(df):
    """获取统计摘要"""
    if df is None or df.empty or "daily_return" not in df.columns:
        return None
    
    daily_returns = df["daily_return"].dropna()
    if len(daily_returns) == 0:
        return None
    
    stats = {
        "total_return": float(daily_returns.sum() * 100),
        "avg_daily_return": float(daily_returns.mean() * 100),
        "std_dev": float(daily_returns.std() * 100),
        "max_return": float(daily_returns.max() * 100),
        "min_return": float(daily_returns.min() * 100),
        "sharpe_ratio": float((daily_returns.mean() / daily_returns.std()) * np.sqrt(252)) if daily_returns.std() != 0 else 0,
        "days": len(df)
    }
    return stats


@app.route("/")
def index():
    """首页"""
    config = load_config()
    return render_template("index.html", watchlist=config["watchlist"])


@app.route("/api/stock/daily", methods=["GET"])
def get_daily_data():
    """获取日线数据API"""
    symbol = request.args.get("symbol", "600519.SH")
    days = int(request.args.get("days", 365))
    
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
    
    try:
        ak_symbol = convert_symbol(symbol)
        df = ak.stock_zh_a_daily(symbol=ak_symbol, start_date=start_date, end_date=end_date, adjust="hfq")
        
        if df is not None and not df.empty:
            df = calculate_indicators(df)
            stats = get_summary_stats(df)
            
            if "date" in df.columns:
                df["date"] = df["date"].astype(str)
            
            return jsonify({
                "success": True,
                "symbol": symbol,
                "data": df.replace({np.nan: None}).to_dict(orient="records"),
                "stats": stats
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
    return jsonify({"success": False, "error": "未能获取数据"}), 400


@app.route("/api/watchlist", methods=["GET", "POST", "DELETE"])
def watchlist():
    """关注列表API"""
    config = load_config()
    
    if request.method == "GET":
        return jsonify({"success": True, "watchlist": config["watchlist"]})
    
    elif request.method == "POST":
        data = request.json
        symbol = data.get("symbol")
        if symbol and symbol not in config["watchlist"]:
            config["watchlist"].append(symbol)
            save_config(config)
        return jsonify({"success": True, "watchlist": config["watchlist"]})
    
    elif request.method == "DELETE":
        data = request.json
        symbol = data.get("symbol")
        if symbol in config["watchlist"]:
            config["watchlist"].remove(symbol)
            save_config(config)
        return jsonify({"success": True, "watchlist": config["watchlist"]})


@app.route("/api/stock/list", methods=["GET"])
def get_stock_list():
    """获取股票列表（热门股票）"""
    hot_stocks = [
        {"code": "600519.SH", "name": "贵州茅台"},
        {"code": "000001.SZ", "name": "平安银行"},
        {"code": "000858.SZ", "name": "五粮液"},
        {"code": "601318.SH", "name": "中国平安"},
        {"code": "600036.SH", "name": "招商银行"},
        {"code": "002594.SZ", "name": "比亚迪"},
        {"code": "601012.SH", "name": "隆基绿能"},
        {"code": "600900.SH", "name": "长江电力"},
        {"code": "601899.SH", "name": "紫金矿业"},
        {"code": "601888.SH", "name": "中国中免"}
    ]
    return jsonify({"success": True, "stocks": hot_stocks})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
