from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.scraper import ScraperFactory
from core.cleaner import CleanerPipeline
from core.analyzer import StockAnalyzer
from core.database import Database
from visualization.charts import ChartGenerator
from models.stock import Stock, AnalysisResult

app = Flask(__name__)
CORS(app)

db = Database()
scraper_factory = ScraperFactory()
cleaner = CleanerPipeline()
analyzer = StockAnalyzer()
chart_gen = ChartGenerator()

@app.route("/")
def index():
    return render_template("index.html")

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
    data = request.get_json()
    code = data.get("code")
    name = data.get("name")
    
    if not code:
        return jsonify({"success": False, "error": "股票代码不能为空"}), 400
    
    scraper = scraper_factory.get_scraper("tencent")
    stock = scraper.fetch_stock_info(code)
    
    if not stock:
        stock = Stock(code=code, name=name or f"股票{code}")
    
    db.save_stock(stock)
    
    analysis = analyzer.analyze(stock)
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

@app.route("/api/stocks/<code>", methods=["DELETE"])
def delete_stock(code):
    success = db.delete_stock(code)
    return jsonify({"success": success})

@app.route("/api/stocks/scrape", methods=["POST"])
def scrape_stocks():
    data = request.get_json() or {}
    codes = data.get("codes", [])
    keyword = data.get("keyword")
    
    if not codes and not keyword:
        codes = ["000001", "000002", "600519", "000858", "601318"]
    elif keyword:
        scraper = scraper_factory.get_scraper("tencent")
        search_results = scraper.search_stocks(keyword)
        codes = [s.code for s in search_results]
    
    raw_stocks = []
    for code in codes:
        scraper = scraper_factory.get_scraper("tencent")
        stock = scraper.fetch_stock_info(code)
        if stock:
            raw_stocks.append(stock)
    
    cleaned_stocks = cleaner.process(raw_stocks)
    saved_count = db.save_stocks(cleaned_stocks)
    
    analyses = []
    for stock in cleaned_stocks:
        analysis = analyzer.analyze(stock)
        db.save_analysis(analysis)
        analyses.append(analysis)
    
    result = []
    for stock in cleaned_stocks:
        stock_dict = stock.to_dict()
        analysis = db.get_analysis(stock.code)
        if analysis:
            stock_dict["analysis"] = analysis.to_dict()
        result.append(stock_dict)
    
    return jsonify({
        "success": True,
        "message": f"成功采集并分析 {saved_count} 只股票",
        "data": result,
        "total": saved_count
    })

@app.route("/api/stocks/<code>/chart", methods=["GET"])
def get_chart(code):
    days = int(request.args.get("days", 30))
    stock = db.get_stock(code)
    
    chart_json = chart_gen.get_chart_json(code, stock.name if stock else None, days)
    
    return jsonify({
        "success": True,
        "data": json.loads(chart_json)
    })

@app.route("/api/stocks/<code>/analyze", methods=["POST"])
def analyze_stock(code):
    stock = db.get_stock(code)
    if not stock:
        return jsonify({"success": False, "error": "股票不存在"}), 404
    
    analysis = analyzer.analyze(stock)
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
    app.run(debug=True, host="0.0.0.0", port=5000)
