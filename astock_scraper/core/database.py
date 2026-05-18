import sqlite3
from typing import List, Optional
from pathlib import Path
from datetime import datetime
from models.stock import Stock, AnalysisResult
import pandas as pd

class Database:
    def __init__(self, db_path: str = "data/stocks.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    name TEXT,
                    market_value REAL,
                    price REAL,
                    industry TEXT,
                    sub_industry TEXT,
                    concepts TEXT,
                    products TEXT,
                    pe REAL,
                    pb REAL,
                    update_time TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT UNIQUE,
                    name TEXT,
                    valuation_percentile REAL,
                    entry_min REAL,
                    entry_max REAL,
                    stop_loss REAL,
                    support_level REAL,
                    resistance_level REAL,
                    opportunity_points TEXT,
                    core_risks TEXT,
                    industry_rank INTEGER,
                    recommendation TEXT,
                    recommendation_source TEXT,
                    update_time TEXT,
                    FOREIGN KEY(stock_code) REFERENCES stocks(code)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT,
                    date TEXT,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume REAL,
                    FOREIGN KEY(stock_code) REFERENCES stocks(code)
                )
            """)
            
            try:
                conn.execute("ALTER TABLE analysis_results ADD COLUMN recommendation_source TEXT")
            except sqlite3.OperationalError:
                pass
    
    def save_stock(self, stock: Stock) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO stocks 
                    (code, name, market_value, price, industry, sub_industry, 
                     concepts, products, pe, pb, update_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    stock.code, stock.name, stock.market_value, stock.price,
                    stock.industry, stock.sub_industry, 
                    ",".join(stock.concepts) if stock.concepts else "",
                    ",".join(stock.products) if stock.products else "",
                    stock.pe, stock.pb, stock.update_time or datetime.now().isoformat()
                ))
            return True
        except Exception as e:
            print(f"保存股票失败: {e}")
            return False
    
    def save_stocks(self, stocks: List[Stock]) -> int:
        count = 0
        for stock in stocks:
            if self.save_stock(stock):
                count += 1
        return count
    
    def get_stock(self, code: str) -> Optional[Stock]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM stocks WHERE code = ?", (code,))
            row = cursor.fetchone()
            if row:
                return Stock.from_dict(dict(row))
        return None
    
    def get_all_stocks(self, industry: str = None, sub_industry: str = None) -> List[Stock]:
        query = "SELECT * FROM stocks WHERE 1=1"
        params = []
        if industry:
            query += " AND industry = ?"
            params.append(industry)
        if sub_industry:
            query += " AND sub_industry = ?"
            params.append(sub_industry)
        query += " ORDER BY industry, sub_industry, code"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [Stock.from_dict(dict(row)) for row in cursor.fetchall()]
    
    def delete_stock(self, code: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM stocks WHERE code = ?", (code,))
                conn.execute("DELETE FROM analysis_results WHERE stock_code = ?", (code,))
            return True
        except Exception as e:
            print(f"删除股票失败: {e}")
            return False
    
    def save_analysis(self, analysis: AnalysisResult) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO analysis_results
                    (stock_code, name, valuation_percentile, entry_min, entry_max,
                     stop_loss, support_level, resistance_level,
                     opportunity_points, core_risks, industry_rank,
                     recommendation, recommendation_source, update_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis.code, analysis.name, analysis.valuation_percentile,
                    analysis.entry_min, analysis.entry_max, analysis.stop_loss,
                    getattr(analysis, 'support_level', None),
                    getattr(analysis, 'resistance_level', None),
                    ",".join(analysis.opportunity_points) if analysis.opportunity_points else "",
                    ",".join(analysis.core_risks) if analysis.core_risks else "",
                    analysis.industry_rank, analysis.recommendation,
                    getattr(analysis, 'recommendation_source', None),
                    datetime.now().isoformat()
                ))
            return True
        except Exception as e:
            print(f"保存分析结果失败: {e}")
            return False
    
    def get_analysis(self, code: str) -> Optional[AnalysisResult]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM analysis_results WHERE stock_code = ?", (code,))
            row = cursor.fetchone()
            if row:
                return AnalysisResult.from_dict(dict(row))
        return None
    
    def save_price_history(self, code: str, prices: List[dict]) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                for p in prices:
                    conn.execute("""
                        INSERT OR REPLACE INTO price_history
                        (stock_code, date, open, high, low, close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (code, p.get("date"), p.get("open"), p.get("high"),
                          p.get("low"), p.get("close"), p.get("volume")))
            return True
        except Exception as e:
            print(f"保存价格历史失败: {e}")
            return False
    
    def get_price_history(self, code: str, days: int = 30) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM price_history 
                WHERE stock_code = ?
                ORDER BY date DESC
                LIMIT ?
            """, (code, days))
            return [dict(row) for row in cursor.fetchall()]
    
    def to_dataframe(self, stocks: List[Stock] = None) -> pd.DataFrame:
        if stocks is None:
            stocks = self.get_all_stocks()
        return pd.DataFrame([s.to_dict() for s in stocks])
    
    def search_stocks(self, keyword: str) -> List[Stock]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM stocks 
                WHERE name LIKE ? OR code LIKE ? OR industry LIKE ? OR concepts LIKE ?
                ORDER BY code
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            return [Stock.from_dict(dict(row)) for row in cursor.fetchall()]
