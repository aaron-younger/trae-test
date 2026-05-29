from typing import List, Dict, Any
from models.stock import Stock
import re

class DataCleaner:
    def clean(self, raw_data: List[Stock]) -> List[Stock]:
        cleaned = []
        seen_codes = set()
        
        for stock in raw_data:
            if not stock:
                continue
            
            stock.code = self._clean_code(stock.code)
            if not stock.code:
                continue
            
            if stock.code in seen_codes:
                continue
            seen_codes.add(stock.code)
            
            stock.name = self._clean_text(stock.name)
            stock.industry = self._clean_text(stock.industry) or "未分类"
            stock.sub_industry = self._clean_text(stock.sub_industry) or "未分类"
            
            if stock.price is not None and (stock.price <= 0 or stock.price > 100000):
                stock.price = None
            
            if stock.market_value is not None and (stock.market_value <= 0 or stock.market_value > 1e15):
                stock.market_value = None
            
            if stock.concepts and len(stock.concepts) > 3:
                stock.concepts = stock.concepts[:3]
            if stock.products and len(stock.products) > 3:
                stock.products = stock.products[:3]
            
            cleaned.append(stock)
        
        return cleaned
    
    def _clean_code(self, code: str) -> str:
        if not code:
            return ""
        code = re.sub(r'[^0-9]', '', str(code))
        if len(code) == 6:
            return code
        return code[:6] if len(code) >= 6 else code
    
    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'\s+', '', str(text))
        text = text.strip('"\'')
        return text

class DataDeduplicator:
    def deduplicate(self, stocks: List[Stock]) -> List[Stock]:
        seen = {}
        unique_stocks = []
        
        for stock in stocks:
            if stock.code in seen:
                existing = seen[stock.code]
                if self._should_update(existing, stock):
                    seen[stock.code] = self._merge_stocks(existing, stock)
            else:
                seen[stock.code] = stock
                unique_stocks.append(stock)
        
        return unique_stocks
    
    def _should_update(self, existing: Stock, new: Stock) -> bool:
        if existing.update_time and new.update_time:
            return new.update_time > existing.update_time
        return new.price is not None and existing.price is None
    
    def _merge_stocks(self, existing: Stock, new: Stock) -> Stock:
        if new.name and new.name != f"股票{new.code}":
            existing.name = new.name
        if new.price is not None:
            existing.price = new.price
        if new.market_value is not None:
            existing.market_value = new.market_value
        if new.industry and new.industry != "未分类":
            existing.industry = new.industry
        if new.concepts:
            existing.concepts = new.concepts
        if new.products:
            existing.products = new.products
        
        existing.update_time = new.update_time or existing.update_time
        # 保留原有的 favorite 状态
        # existing.favorite 保持不变，不被 new.favorite 覆盖
        return existing

class CleanerPipeline:
    def __init__(self):
        self.steps = [DataCleaner(), DataDeduplicator()]
    
    def process(self, raw_data: List[Stock]) -> List[Stock]:
        for step in self.steps:
            raw_data = step.clean(raw_data) if hasattr(step, 'clean') else step.deduplicate(raw_data)
        return raw_data
