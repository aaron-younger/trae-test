from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

# 延迟导入 - 按需加载
def get_db():
    from core.database import Database
    return Database()

def get_scraper_factory():
    from core.scraper import ScraperFactory
    return ScraperFactory()

def get_cleaner():
    from core.cleaner import CleanerPipeline
    return CleanerPipeline()

def get_analyzer():
    from core.analyzer import StockAnalyzer
    return StockAnalyzer()

def get_chart_gen():
    from visualization.charts import ChartGenerator
    return ChartGenerator()

app = Flask(__name__)
CORS(app)

# 预加载数据库
db = get_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/health", methods=["GET"])
def health_check():
    try:
        stocks = db.get_all_stocks()
        return jsonify({
            "success": True,
            "status": "healthy",
            "stocks_count": len(stocks),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503

@app.route("/api/stocks", methods=["GET"])
def get_stocks():
    industry = request.args.get("industry")
    sub_industry = request.args.get("sub_industry")
    sort_by = request.args.get("sort", "industry")
    
    stocks = db.get_all_stocks(industry=industry, sub_industry=sub_industry)
    
    if sort_by == "code":
        stocks.sort(key=lambda x: x.code)
    elif sort_by == "name":
        stocks.sort(key=lambda x: x.name)
    elif sort_by == "price":
        stocks.sort(key=lambda x: x.price or 0, reverse=True)
    
    result = []
    for stock in stocks:
        stock_dict = stock.to_dict()
        analysis = db.get_analysis(stock.code)
        if analysis:
            stock_dict["analysis"] = analysis.to_dict()
        result.append(stock_dict)
    
    return jsonify({"success": True, "data": result, "total": len(result)})

@app.route("/api/stocks/<code>", methods=["GET"])
def get_stock(code):
    stock = db.get_stock(code)
    if not stock:
        return jsonify({"success": False, "error": "股票不存在"}), 404
    
    result = stock.to_dict()
    analysis = db.get_analysis(code)
    if analysis:
        result["analysis"] = analysis.to_dict()
    
    return jsonify({"success": True, "data": result})

@app.route("/api/stocks/search", methods=["POST"])
def search_stocks():
    data = request.get_json()
    keyword = data.get("keyword", "")
    
    results = db.search_stocks(keyword)
    
    return jsonify({
        "success": True,
        "data": [s.to_dict() for s in results],
        "total": len(results)
    })

@app.route("/api/stocks", methods=["POST"])
def add_stock():
    from models.stock import Stock
    data = request.get_json()
    code = data.get("code")
    name = data.get("name")
    
    if not code:
        return jsonify({"success": False, "error": "股票代码不能为空"}), 400
    
    scraper = get_scraper_factory().get_scraper("tencent")
    stock = scraper.fetch_stock_info(code)
    
    if not stock:
        stock = Stock(code=code, name=name or f"股票{code}")
    
    db.save_stock(stock)
    
    analysis = get_analyzer().analyze(stock)
    db.save_analysis(analysis)
    
    return jsonify({
        "success": True,
        "data": {**stock.to_dict(), "analysis": analysis.to_dict()}
    })

@app.route("/api/stocks/<code>", methods=["PUT"])
def update_stock(code):
    data = request.get_json()
    stock = db.get_stock(code)
    
    if not stock:
        return jsonify({"success": False, "error": "股票不存在"}), 404
    
    if "name" in data:
        stock.name = data["name"]
    if "price" in data:
        stock.price = data["price"]
    if "industry" in data:
        stock.industry = data["industry"]
    
    stock.update_time = datetime.now().isoformat()
    db.save_stock(stock)
    
    return jsonify({"success": True, "data": stock.to_dict()})

@app.route("/api/stocks/<code>/favorite", methods=["PUT"])
def update_favorite(code):
    data = request.get_json()
    stock = db.get_stock(code)
    
    if not stock:
        return jsonify({"success": False, "error": "股票不存在"}), 404
    
    stock.favorite = data.get("favorite", False)
    stock.update_time = datetime.now().isoformat()
    db.save_stock(stock)
    
    return jsonify({"success": True, "data": stock.to_dict()})

@app.route("/api/stocks/<code>", methods=["DELETE"])
def delete_stock(code):
    success = db.delete_stock(code)
    return jsonify({"success": success})

@app.route("/api/stocks/batch_delete", methods=["DELETE"])
def batch_delete_stocks():
    data = request.get_json()
    codes = data.get("codes", [])
    
    if not codes or not isinstance(codes, list):
        return jsonify({"success": False, "error": "请提供要删除的股票代码列表"}), 400
    
    deleted_count = 0
    for code in codes:
        if db.delete_stock(code):
            deleted_count += 1
    
    return jsonify({
        "success": True,
        "deleted": deleted_count,
        "total_requested": len(codes)
    })

@app.route("/api/stocks/scrape", methods=["POST"])
def scrape_stocks():
    data = request.get_json() or {}
    codes = data.get("codes", [])
    keyword = data.get("keyword")
    
    if not codes and not keyword:
        all_stocks = db.get_all_stocks()
        codes = [s.code for s in all_stocks]
    elif keyword:
        scraper = get_scraper_factory().get_scraper("tencent")
        search_results = scraper.search_stocks(keyword)
        codes = [s.code for s in search_results]
    
    raw_stocks = []
    errors = []
    for i, code in enumerate(codes):
        try:
            print(f"正在采集第 {i+1}/{len(codes)} 只股票: {code}")
            scraper = get_scraper_factory().get_scraper("tencent")
            stock = scraper.fetch_stock_info(code)
            if stock:
                raw_stocks.append(stock)
        except Exception as e:
            print(f"采集 {code} 失败: {e}")
            errors.append(f"{code}: {str(e)[:50]}")
            # 遇到小错误继续处理下一只
            continue
    
    cleaned_stocks = get_cleaner().process(raw_stocks)
    saved_count = db.save_stocks(cleaned_stocks)
    
    analyses = []
    for stock in cleaned_stocks:
        try:
            analysis = get_analyzer().analyze(stock)
            db.save_analysis(analysis)
            analyses.append(analysis)
        except Exception as e:
            print(f"分析 {stock.code} 失败: {e}")
            # 跳过分析失败的
    
    result = []
    for stock in cleaned_stocks:
        stock_dict = stock.to_dict()
        analysis = db.get_analysis(stock.code)
        if analysis:
            stock_dict["analysis"] = analysis.to_dict()
        result.append(stock_dict)
    
    message = f"成功采集并分析 {saved_count} 只股票"
    if errors:
        message += f" ({len(errors)} 只失败)"
    
    return jsonify({
        "success": True,
        "message": message,
        "data": result,
        "total": saved_count,
        "errors": errors[:10] if len(errors) > 10 else errors
    })

@app.route("/api/stocks/<code>/chart", methods=["GET"])
def get_chart(code):
    try:
        days = int(request.args.get("days", 30))
        stock = db.get_stock(code)
        
        base_price = stock.price if stock and stock.price else 10.0
        chart_data = get_real_kline_data(code, days, base_price)
        
        return jsonify({
            "success": True,
            "data": chart_data
        })
    except Exception as e:
        print(f"获取图表数据失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def get_real_kline_data(code: str, days: int = 30, base_price: float = None) -> dict:
    """从腾讯财经获取真实日K线数据"""
    import requests
    
    if not code.startswith(("sh", "sz", "bj")):
        if code.startswith("6") or code.startswith("688"):
            code = f"sh{code}"
        elif code.startswith("8"):
            code = f"bj{code}"
        else:
            code = f"sz{code}"
    
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq&param={code},day,,,{days},qfq"
    
    try:
        response = requests.get(url, timeout=10)
        data_text = response.text
        
        if "kline_dayqfq" in data_text:
            data_text = data_text[data_text.index("=") + 1:]
        
        data = json.loads(data_text)
        
        qfqday = data.get("data", {}).get(code, {}).get("qfqday", [])
        
        if not qfqday:
            qfqday = data.get("data", {}).get(code, {}).get("day", [])
        
        if qfqday and len(qfqday) > 0:
            stock = db.get_stock(code[2:] if code.startswith(("sh", "sz", "bj")) else code)
            
            dates = []
            opens = []
            highs = []
            lows = []
            closes = []
            volumes = []
            
            for candle in qfqday[-days:]:
                if len(candle) >= 6:
                    dates.append(candle[0])
                    opens.append(float(candle[1]))
                    closes.append(float(candle[2]))
                    highs.append(float(candle[3]))
                    lows.append(float(candle[4]))
                    vol_str = candle[5] if candle[5] else "0"
                    volumes.append(int(float(vol_str)))
            
            current_price = closes[-1] if closes else base_price
            
            ma5 = calculate_ma(closes, 5)
            ma10 = calculate_ma(closes, 10)
            ma20 = calculate_ma(closes, 20)
            
            return {
                "code": code[2:] if code.startswith(("sh", "sz", "bj")) else code,
                "name": stock.name if stock else code,
                "currentPrice": current_price,
                "dates": dates,
                "prices": {
                    "open": opens,
                    "high": highs,
                    "low": lows,
                    "close": closes
                },
                "volumes": volumes,
                "ma": {
                    "ma5": ma5,
                    "ma10": ma10,
                    "ma20": ma20
                }
            }
    except Exception as e:
        print(f"获取K线数据失败: {e}")
    
    stock = db.get_stock(code[2:] if code.startswith(("sh", "sz", "bj")) else code)
    return {
        "code": code[2:] if code.startswith(("sh", "sz", "bj")) else code,
        "name": stock.name if stock else code,
        "currentPrice": base_price,
        "dates": [],
        "prices": {"open": [], "high": [], "low": [], "close": []},
        "volumes": [],
        "ma": {"ma5": [], "ma10": [], "ma20": []}
    }

def calculate_ma(prices: list, period: int) -> list:
    """计算移动平均线"""
    ma = []
    for i in range(len(prices)):
        if i < period - 1:
            ma.append(None)
        else:
            ma_value = sum(prices[i - period + 1:i + 1]) / period
            ma.append(round(ma_value, 2))
    return ma

@app.route("/api/stocks/<code>/analyze", methods=["POST"])
def analyze_stock(code):
    stock = db.get_stock(code)
    if not stock:
        return jsonify({"success": False, "error": "股票不存在"}), 404
    
    analysis = get_analyzer().analyze(stock)
    db.save_analysis(analysis)
    
    return jsonify({
        "success": True,
        "data": analysis.to_dict()
    })

@app.route("/api/industries", methods=["GET"])
def get_industries():
    stocks = db.get_all_stocks()
    
    industries = {}
    for s in stocks:
        if s.industry:
            if s.industry not in industries:
                industries[s.industry] = {
                    "name": s.industry,
                    "count": 0,
                    "sub_industries": set(),
                    "total_value": 0
                }
            industries[s.industry]["count"] += 1
            if s.sub_industry:
                industries[s.industry]["sub_industries"].add(s.sub_industry)
            if s.market_value:
                industries[s.industry]["total_value"] += s.market_value
    
    result = []
    for ind_data in industries.values():
        result.append({
            "name": ind_data["name"],
            "count": ind_data["count"],
            "sub_industries": list(ind_data["sub_industries"]),
            "total_value": ind_data["total_value"]
        })
    
    result.sort(key=lambda x: x["total_value"], reverse=True)
    
    return jsonify({"success": True, "data": result})

@app.route("/api/hot_industries", methods=["GET"])
def get_hot_industries():
    import requests
    
    sources = [
        ("腾讯财经", "https://qt.gtimg.cn/r=0.1234567890123456"),
        ("新浪财经", "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?num=20&sort=changepercent&asc=0&node=industry"),
    ]
    
    for source_name, url in sources:
        try:
            response = requests.get(url, timeout=8)
            
            if source_name == "腾讯财经":
                data = response.text
                hot_industries = []
                lines = data.split(';')
                for line in lines[:50]:
                    if '=' in line:
                        parts = line.split('=', 1)
                        if len(parts) >= 2:
                            code = parts[0].strip()
                            if code.startswith('v_szgn') or code.startswith('v_shgn'):
                                try:
                                    info_str = parts[1].strip()
                                    if info_str.startswith('"') and info_str.endswith('"'):
                                        info_str = info_str[1:-1]
                                    info = info_str.split('~')
                                    if len(info) > 10:
                                        hot_industries.append({
                                            "name": info[1],
                                            "change": float(info[3]) if info[3] and info[3] != '-' else 0,
                                            "up_count": int(info[4]) if info[4] else 0,
                                            "down_count": int(info[5]) if info[5] else 0,
                                            "leader": info[10] if len(info) > 10 and info[10] else ""
                                        })
                                except:
                                    pass
                
                hot_industries.sort(key=lambda x: abs(x["change"]), reverse=True)
                top_three = hot_industries[:3]
                
                if len(top_three) > 0:
                    return jsonify({
                        "success": True,
                        "data": top_three,
                        "source": source_name
                    })
            
            elif source_name == "新浪财经":
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    hot_industries = []
                    for item in data[:10]:
                        try:
                            hot_industries.append({
                                "name": item.get("name", ""),
                                "change": float(item.get("changepercent", "0")),
                                "up_count": 0,
                                "down_count": 0,
                                "leader": item.get("symbol", "")
                            })
                        except:
                            pass
                    
                    hot_industries.sort(key=lambda x: abs(x["change"]), reverse=True)
                    top_three = hot_industries[:3]
                    
                    if len(top_three) > 0:
                        return jsonify({
                            "success": True,
                            "data": top_three,
                            "source": source_name
                        })
        
        except Exception as e:
            print(f"从 {source_name} 获取热点行业失败: {e}")
            continue
    
    return jsonify({
        "success": True,
        "data": [],
        "source": "暂无数据"
    })

@app.route("/api/market-indices", methods=["GET"])
def get_market_indices():
    """获取大盘指数数据（上证、深证、创业板、科创板）"""
    import requests
    indices = [
        {"code": "sh000001", "name": "上证指数"},
        {"code": "sz399001", "name": "深证成指"},
        {"code": "sh000688", "name": "科创50"},
        {"code": "sz399006", "name": "创业板指"}
    ]
    
    result = []
    for index_info in indices:
        try:
            url = f"https://qt.gtimg.cn/q={index_info['code']}"
            response = requests.get(url, timeout=5)
            data_text = response.text
            
            if "v_" in data_text:
                data_text = data_text[data_text.index("v_"):]
            
            parts = data_text.split("=")[1].strip('"').split("~")
            
            if len(parts) > 3:
                current_price = float(parts[3]) if parts[3] else None
                yesterday_close = float(parts[4]) if (len(parts) > 4 and parts[4]) else None
                change_pct = ((current_price - yesterday_close) / yesterday_close * 100) if (current_price and yesterday_close and yesterday_close != 0) else 0
                
                # 如果无法获取真实MA20，使用模拟数据
                # 实际项目中可以通过历史数据计算
                ma20 = current_price * 0.98 if current_price else None
                
                above_ma20 = current_price > ma20 if (current_price is not None and ma20 is not None) else False
                
                result.append({
                    "code": index_info["code"],
                    "name": index_info["name"],
                    "price": current_price,
                    "change": change_pct,
                    "ma20": ma20,
                    "above_ma20": above_ma20
                })
        except Exception as e:
            print(f"获取{index_info['name']}数据失败: {e}")
            result.append({
                "code": index_info["code"],
                "name": index_info["name"],
                "price": None,
                "change": 0,
                "ma20": None,
                "above_ma20": False
            })
    
    return jsonify({
        "success": True,
        "data": result,
        "source": "腾讯财经"
    })

@app.route("/api/export", methods=["POST"])
def export_data():
    data = request.get_json() or {}
    codes = data.get("codes", [])
    industry = data.get("industry")
    
    if codes:
        stocks = [db.get_stock(c) for c in codes]
        stocks = [s for s in stocks if s]
    elif industry:
        stocks = db.get_all_stocks(industry=industry)
    else:
        stocks = db.get_all_stocks()
    
    result = []
    for stock in stocks:
        stock_dict = stock.to_dict()
        analysis = db.get_analysis(stock.code)
        if analysis:
            stock_dict["analysis"] = analysis.to_dict()
        result.append(stock_dict)
    
    return jsonify({
        "success": True,
        "data": result,
        "total": len(result)
    })

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
