import os
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Stock:
    code: str
    name: str
    market_value: Optional[float] = None
    price: Optional[float] = None
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    concepts: List[str] = None
    products: List[str] = None
    pe: Optional[float] = None
    pb: Optional[float] = None
    update_time: Optional[str] = None
    favorite: Optional[bool] = None
    
    def __post_init__(self):
        if self.concepts is None:
            self.concepts = []
        if self.products is None:
            self.products = []
        if self.update_time is None:
            self.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self):
        return {
            "code": self.code,
            "name": self.name,
            "market_value": self.market_value,
            "price": self.price,
            "industry": self.industry,
            "sub_industry": self.sub_industry,
            "concepts": ",".join(self.concepts) if self.concepts else "",
            "products": ",".join(self.products) if self.products else "",
            "pe": self.pe,
            "pb": self.pb,
            "update_time": self.update_time,
            "favorite": self.favorite
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        concepts = data.get("concepts", "")
        products = data.get("products", "")
        if isinstance(concepts, str):
            concepts = [c.strip() for c in concepts.split(",") if c.strip()]
        if isinstance(products, str):
            products = [p.strip() for p in products.split(",") if p.strip()]
        
        favorite = data.get("favorite", False)
        # 处理数据库中存储的整数形式 (0/1)
        if isinstance(favorite, int):
            favorite = favorite == 1
        
        return cls(
            code=data.get("code", ""),
            name=data.get("name", ""),
            market_value=data.get("market_value"),
            price=data.get("price"),
            industry=data.get("industry"),
            sub_industry=data.get("sub_industry"),
            concepts=concepts,
            products=products,
            pe=data.get("pe"),
            pb=data.get("pb"),
            update_time=data.get("update_time"),
            favorite=favorite
        )

@dataclass
class AnalysisResult:
    code: str
    name: str
    valuation_percentile: Optional[float] = None
    entry_min: Optional[float] = None
    entry_max: Optional[float] = None
    stop_loss: Optional[float] = None
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None
    opportunity_points: List[str] = None
    core_risks: List[str] = None
    industry_rank: Optional[int] = None
    recommendation: Optional[str] = None
    recommendation_source: Optional[str] = None
    
    def __post_init__(self):
        if self.opportunity_points is None:
            self.opportunity_points = []
        if self.core_risks is None:
            self.core_risks = []
    
    def to_dict(self):
        return {
            "code": self.code,
            "name": self.name,
            "valuation_percentile": self.valuation_percentile,
            "entry_min": self.entry_min,
            "entry_max": self.entry_max,
            "stop_loss": self.stop_loss,
            "support_level": self.support_level,
            "resistance_level": self.resistance_level,
            "opportunity_points": ",".join(self.opportunity_points) if self.opportunity_points else "",
            "core_risks": ",".join(self.core_risks) if self.core_risks else "",
            "industry_rank": self.industry_rank,
            "recommendation": self.recommendation,
            "recommendation_source": self.recommendation_source
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        opp_points = data.get("opportunity_points", "")
        core_risks = data.get("core_risks", "")
        if isinstance(opp_points, str):
            opp_points = [p.strip() for p in opp_points.split(",") if p.strip()]
        if isinstance(core_risks, str):
            core_risks = [r.strip() for r in core_risks.split(",") if r.strip()]
        
        return cls(
            code=data.get("code", ""),
            name=data.get("name", ""),
            valuation_percentile=data.get("valuation_percentile"),
            entry_min=data.get("entry_min"),
            entry_max=data.get("entry_max"),
            stop_loss=data.get("stop_loss"),
            support_level=data.get("support_level"),
            resistance_level=data.get("resistance_level"),
            opportunity_points=opp_points,
            core_risks=core_risks,
            industry_rank=data.get("industry_rank"),
            recommendation=data.get("recommendation"),
            recommendation_source=data.get("recommendation_source")
        )
