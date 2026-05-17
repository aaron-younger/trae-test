import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Optional
import json
from pathlib import Path
from datetime import datetime, timedelta
import random
from models.stock import Stock, AnalysisResult

class ChartGenerator:
    def __init__(self, output_dir: str = "data/charts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_price_trend(self, code: str, name: str = None, days: int = 30) -> str:
        dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days, 0, -1)]
        base_price = 10 + (hash(code) % 100)
        prices = self._generate_mock_prices(base_price, days)
        
        volumes = [random.randint(1000000, 10000000) for _ in range(days)]
        
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.7, 0.3],
            subplot_titles=(f"{name or code} 价格趋势", "成交量")
        )
        
        fig.add_trace(
            go.Candlestick(
                x=dates,
                open=prices["open"],
                high=prices["high"],
                low=prices["low"],
                close=prices["close"],
                name="K线",
                increasing_line_color="#FF6B6B",
                decreasing_line_color="#4ECDC4"
            ),
            row=1, col=1
        )
        
        ma5 = self._calc_ma(prices["close"], 5)
        ma10 = self._calc_ma(prices["close"], 10)
        ma20 = self._calc_ma(prices["close"], 20)
        
        fig.add_trace(
            go.Scatter(x=dates, y=ma5, name="MA5", line=dict(color="#FFD93D", width=1.5)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=dates, y=ma10, name="MA10", line=dict(color="#6BCB77", width=1.5)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=dates, y=ma20, name="MA20", line=dict(color="#4D96FF", width=1.5)),
            row=1, col=1
        )
        
        colors = ["#FF6B6B" if prices["close"][i] >= prices["open"][i] else "#4ECDC4" for i in range(days)]
        fig.add_trace(
            go.Bar(x=dates, y=volumes, marker_color=colors, name="成交量"),
            row=2, col=1
        )
        
        fig.update_layout(
            template="plotly_dark",
            title=dict(text=f"{name or code} ({code})", font=dict(size=20)),
            xaxis_rangeslider_visible=False,
            height=600,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified"
        )
        
        output_path = self.output_dir / f"{code}_trend.html"
        fig.write_html(str(output_path))
        return str(output_path)
    
    def generate_industry_comparison(self, stocks: List[Stock], analysis_results: List[AnalysisResult] = None) -> str:
        industries = {}
        for stock in stocks:
            if stock.industry:
                if stock.industry not in industries:
                    industries[stock.industry] = {"count": 0, "total_value": 0, "avg_price": 0}
                industries[stock.industry]["count"] += 1
                if stock.market_value:
                    industries[stock.industry]["total_value"] += stock.market_value
                if stock.price:
                    industries[stock.industry]["avg_price"] += stock.price
        
        for ind in industries:
            if industries[ind]["count"] > 0:
                industries[ind]["avg_price"] /= industries[ind]["count"]
        
        sorted_industries = sorted(industries.items(), key=lambda x: x[1]["total_value"], reverse=True)
        labels = [x[0] for x in sorted_industries]
        values = [x[1]["total_value"] / 1e8 for x in sorted_industries]
        
        fig = go.Figure(data=[
            go.Bar(
                x=labels,
                y=values,
                marker_color=["#FF6B6B", "#4ECDC4", "#FFD93D", "#6BCB77", "#4D96FF", "#9B59B6", "#E74C3C"][:len(labels)],
                text=[f"{v:.0f}亿" for v in values],
                textposition="auto"
            )
        ])
        
        fig.update_layout(
            template="plotly_dark",
            title="行业市值对比",
            xaxis_title="行业",
            yaxis_title="总市值(亿元)",
            height=500,
            showlegend=False
        )
        
        output_path = self.output_dir / "industry_comparison.html"
        fig.write_html(str(output_path))
        return str(output_path)
    
    def generate_analysis_radar(self, analysis: AnalysisResult) -> str:
        categories = ["估值百分位", "成长性", "盈利质量", "股价强度", "行业地位"]
        values = [
            100 - (analysis.valuation_percentile or 50),
            random.uniform(40, 90),
            random.uniform(50, 95),
            random.uniform(30, 85),
            random.uniform(45, 90)
        ]
        values.append(values[0])
        categories.append(categories[0])
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            fillcolor="rgba(255, 107, 107, 0.3)",
            line=dict(color="#FF6B6B", width=2)
        ))
        
        fig.update_layout(
            template="plotly_dark",
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title=f"{analysis.name} 分析雷达图",
            height=500,
            showlegend=False
        )
        
        output_path = self.output_dir / f"{analysis.code}_radar.html"
        fig.write_html(str(output_path))
        return str(output_path)
    
    def generate_recommendation_chart(self, stocks: List[Stock], analyses: List[AnalysisResult]) -> str:
        recommendations = {"强烈推荐": 0, "推荐": 0, "建议关注": 0, "中性": 0, "谨慎推荐": 0, "回避": 0}
        
        for a in analyses:
            if a.recommendation:
                rec = a.recommendation
                for key in recommendations:
                    if key in rec:
                        recommendations[key] += 1
                        break
        
        labels = list(recommendations.keys())
        values = list(recommendations.values())
        colors = ["#FF6B6B", "#FFD93D", "#6BCB77", "#95A5A6", "#E74C3C", "#9B59B6"]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            textinfo="label+percent",
            textposition="inside"
        )])
        
        fig.update_layout(
            template="plotly_dark",
            title="个股推荐分布",
            height=400,
            showlegend=True
        )
        
        output_path = self.output_dir / "recommendations.html"
        fig.write_html(str(output_path))
        return str(output_path)
    
    def _generate_mock_prices(self, base_price: float, days: int) -> Dict[str, List[float]]:
        prices = {"open": [], "high": [], "low": [], "close": []}
        
        # 生成倒推，从当前价格开始，让最后一天（最新）是当前价格，然后向前生成
        current = base_price
        
        # 先反向生成（从当前往过去推）
        backward_prices = []
        for _ in range(days):
            change = random.uniform(-0.02, 0.03)
            open_price = current
            close_price = current * (1 + change)
            
            high_price = max(open_price, close_price) * random.uniform(1.0, 1.02)
            low_price = min(open_price, close_price) * random.uniform(0.98, 1.0)
            
            backward_prices.append({
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "close": round(close_price, 2),
                "low": round(low_price, 2),
            })
            
            current = close_price
        
        # 反转得到从旧到新
        backward_prices.reverse()
        
        # 填充到数组，确保最后一个价格是base_price
        for i, p in enumerate(backward_prices):
            prices["open"].append(p["open"])
            prices["high"].append(p["high"])
            prices["low"].append(p["low"])
            if i == len(backward_prices) - 1:
                # 最后一天（最新一天）价格设为base_price
                prices["close"].append(round(base_price, 2))
            else:
                prices["close"].append(p["close"])
        
        return prices
    
    def _calc_ma(self, prices: List[float], period: int) -> List[float]:
        ma = []
        for i in range(len(prices)):
            if i < period - 1:
                ma.append(None)
            else:
                ma_value = sum(prices[i - period + 1:i + 1]) / period
                ma.append(round(ma_value, 2))
        return ma
    
    def get_chart_json(self, code: str, name: str = None, days: int = 30, base_price: float = None) -> str:
        if base_price is None:
            base_price = 10 + (hash(code) % 100)
        
        dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days, 0, -1)]
        prices = self._generate_mock_prices(base_price, days)
        ma5 = self._calc_ma(prices["close"], 5)
        ma10 = self._calc_ma(prices["close"], 10)
        
        return json.dumps({
            "code": code,
            "name": name or code,
            "currentPrice": base_price,
            "dates": dates,
            "prices": {
                "open": prices["open"],
                "high": prices["high"],
                "low": prices["low"],
                "close": prices["close"]
            },
            "ma": {
                "ma5": ma5,
                "ma10": ma10
            }
        })
