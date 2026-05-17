from models.stock import Stock, AnalysisResult
from typing import List, Dict
import os

class StockAnalyzer:
    def __init__(self):
        self.use_real_ai = bool(os.getenv("OPENAI_API_KEY"))
    
    def analyze(self, stock: Stock) -> AnalysisResult:
        valuation = self._calc_valuation_percentile(stock)
        entry_range = self._calc_entry_range(stock)
        stop_loss = self._calc_stop_loss(stock)
        opportunities = self._extract_opportunities(stock)
        risks = self._extract_risks(stock)
        recommendation = self._generate_recommendation(valuation, entry_range, stock)
        source = self._generate_recommendation_source(stock, valuation, recommendation)
        
        return AnalysisResult(
            code=stock.code,
            name=stock.name,
            valuation_percentile=valuation,
            entry_min=entry_range["min"],
            entry_max=entry_range["max"],
            stop_loss=stop_loss,
            opportunity_points=opportunities,
            core_risks=risks,
            recommendation=recommendation,
            recommendation_source=source
        )
    
    def _calc_valuation_percentile(self, stock: Stock) -> float:
        # 基于PE计算估值百分位（确定性算法，不使用随机数）
        if stock.pe and stock.pe > 0:
            # PE越低，估值百分位越低（越低估）
            # PE=5 -> 5%, PE=10 -> 15%, PE=20 -> 35%, PE=30 -> 55%, PE=50 -> 75%, PE=80 -> 90%
            if stock.pe < 5:
                return 5.0
            elif stock.pe < 10:
                return 5.0 + (stock.pe - 5) * 2.0
            elif stock.pe < 20:
                return 15.0 + (stock.pe - 10) * 2.0
            elif stock.pe < 30:
                return 35.0 + (stock.pe - 20) * 2.0
            elif stock.pe < 50:
                return 55.0 + (stock.pe - 30) * 1.0
            elif stock.pe < 80:
                return 75.0 + (stock.pe - 50) * 0.5
            else:
                return min(95.0, 90.0 + (stock.pe - 80) * 0.1)
        elif stock.pb and stock.pb > 0:
            # 基于PB计算
            if stock.pb < 0.5:
                return 5.0
            elif stock.pb < 1:
                return 5.0 + (stock.pb - 0.5) * 20.0
            elif stock.pb < 2:
                return 15.0 + (stock.pb - 1) * 15.0
            elif stock.pb < 3:
                return 30.0 + (stock.pb - 2) * 15.0
            elif stock.pb < 5:
                return 45.0 + (stock.pb - 3) * 10.0
            else:
                return min(90.0, 65.0 + (stock.pb - 5) * 5.0)
        return 50.0
    
    def _calc_entry_range(self, stock: Stock) -> Dict[str, float]:
        if not stock.price:
            return {"min": 0, "max": 0}
        
        price = stock.price
        pe = stock.pe or 20
        
        if pe < 10:
            risk_adj = 0.92
        elif pe < 20:
            risk_adj = 0.95
        elif pe < 30:
            risk_adj = 0.97
        else:
            risk_adj = 1.02
        
        if stock.concepts and len(stock.concepts) > 0:
            concept_boost = 1.05
        else:
            concept_boost = 1.0
        
        entry_max = round(price * risk_adj * concept_boost, 2)
        entry_min = round(entry_max * 0.88, 2)
        
        return {"min": entry_min, "max": entry_max}
    
    def _calc_stop_loss(self, stock: Stock) -> float:
        if not stock.price:
            return 0
        
        entry_max = self._calc_entry_range(stock)["max"]
        if entry_max > 0:
            base_price = (entry_max + stock.price) / 2
        else:
            base_price = stock.price
        
        volatility = 0.08
        if stock.industry in ["科技", "互联网", "医药"]:
            volatility = 0.12
        elif stock.industry in ["银行", "房地产", "基建"]:
            volatility = 0.06
        
        stop_loss = round(base_price * (1 - volatility), 2)
        return stop_loss
    
    def _extract_opportunities(self, stock: Stock) -> List[str]:
        opportunities = []
        
        if stock.pe and stock.pe < 15:
            opportunities.append("估值处于历史低位")
        elif stock.pe and stock.pe > 40:
            opportunities.append("估值偏高，需谨慎")
        
        if stock.concepts:
            for concept in stock.concepts[:2]:
                opportunities.append(f"涉及{concept}热点")
        
        industry_opp = {
            "科技": "技术突破，国产替代",
            "医药": "人口老龄化，行业景气",
            "消费": "内需扩大，消费升级",
            "新能源": "碳中和政策利好",
            "银行": "估值修复，低估值高股息"
        }
        if stock.industry in industry_opp:
            opportunities.append(industry_opp[stock.industry])
        
        if not opportunities:
            opportunities = ["业绩稳健", "行业地位稳固", "基本面良好"]
        
        return opportunities[:3]
    
    def _extract_risks(self, stock: Stock) -> List[str]:
        risks = []
        
        # 使用确定性规则，不使用随机数
        # 根据股票代码的hash值选择风险项，保证同一股票结果一致
        code_hash = sum(ord(c) for c in stock.code) if stock.code else 0
        
        common_risks = ["宏观经济波动", "政策变化风险", "行业竞争加剧"]
        # 用hash值确定选择哪些风险
        risks.append(common_risks[code_hash % len(common_risks)])
        risks.append(common_risks[(code_hash + 1) % len(common_risks)])
        
        industry_risks = {
            "科技": ["技术迭代风险", "人才流失风险"],
            "医药": ["带量采购降价", "研发失败风险"],
            "房地产": ["调控政策收紧", "流动性风险"],
            "银行": ["不良贷款率上升", "净息差收窄"],
            "白酒": ["消费税传言", "需求增速放缓"]
        }
        if stock.industry in industry_risks:
            ind_risks = industry_risks[stock.industry]
            risks.append(ind_risks[code_hash % len(ind_risks)])
        
        if stock.pe and stock.pe > 50:
            risks.append("高估值透支未来业绩")
        elif stock.pe and stock.pe < 5:
            risks.append("低估值可能反映经营问题")
        
        return risks[:3]
    
    def _generate_recommendation(self, valuation: float, entry_range: Dict, stock: Stock) -> str:
        if valuation < 20:
            rec = "强烈推荐"
        elif valuation < 40:
            rec = "推荐"
        elif valuation < 60:
            rec = "中性"
        elif valuation < 80:
            rec = "谨慎推荐"
        else:
            rec = "回避"
        
        if stock.price and entry_range["max"] > 0:
            if stock.price <= entry_range["max"]:
                rec = rec.replace("推荐", "建议关注")
        
        return rec
    
    def _generate_recommendation_source(self, stock: Stock, valuation: float, recommendation: str) -> str:
        sources = []
        
        if stock.pe:
            sources.append(f"PE={stock.pe}")
        if stock.pb:
            sources.append(f"PB={stock.pb}")
        
        valuation_level = "低估值" if valuation < 30 else ("高估值" if valuation > 70 else "适中")
        sources.append(f"估值{valuation_level}")
        
        if stock.price and stock.price > 0:
            sources.append(f"现价{stock.price}")
        
        combined = " | ".join(sources)
        
        return f"数据来源: 腾讯财经/同花顺 | 分析依据: {combined}"
    
    def analyze_batch(self, stocks: List[Stock]) -> List[AnalysisResult]:
        return [self.analyze(stock) for stock in stocks if stock.code]
    
    def rank_industry(self, stocks: List[Stock]) -> List[tuple]:
        ranked = []
        industry_groups = {}
        
        for stock in stocks:
            if stock.industry:
                if stock.industry not in industry_groups:
                    industry_groups[stock.industry] = []
                industry_groups[stock.industry].append(stock)
        
        for industry, ind_stocks in industry_groups.items():
            avg_pe = sum(s.pe for s in ind_stocks if s.pe) / max(len([s for s in ind_stocks if s.pe]), 1)
            score = 100 - min(avg_pe * 2, 80) if avg_pe > 0 else 50
            ranked.append((industry, score, len(ind_stocks)))
        
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked
