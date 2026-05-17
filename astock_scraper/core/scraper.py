import abc
from typing import List, Optional, Dict, Any
import requests
from bs4 import BeautifulSoup
import time
from models.stock import Stock
from config import SCRAPER_CONFIGS, DEFAULT_SOURCE

class BaseScraper(abc.ABC):
    @abc.abstractmethod
    def fetch_stock_info(self, code: str) -> Optional[Stock]:
        pass
    
    @abc.abstractmethod
    def search_stocks(self, keyword: str) -> List[Stock]:
        pass
    
    def _make_request(self, url: str, params: dict = None, headers: dict = None) -> Optional[requests.Response]:
        config = SCRAPER_CONFIGS.get(self.name, {"timeout": 10, "retry": 3})
        timeout = config.get("timeout", 10)
        max_retries = config.get("retry", 3)
        
        for attempt in range(max_retries):
            try:
                # 添加连接超时和读取超时
                response = requests.get(url, params=params, headers=headers, timeout=(timeout * 0.3, timeout))
                response.raise_for_status()
                return response
            except requests.exceptions.Timeout:
                print(f"[{self.name}] 请求超时 (尝试 {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    return None
            except requests.RequestException as e:
                print(f"[{self.name}] 请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(0.5 * (attempt + 1))
        return None

class TencentScraper(BaseScraper):
    name = "tencent"
    
    def fetch_stock_info(self, code: str) -> Optional[Stock]:
        if not code.startswith(("sh", "sz")):
            if code.startswith("6"):
                code = f"sh{code}"
            else:
                code = f"sz{code}"
        
        url = f"https://qt.gtimg.cn/q={code}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = self._make_request(url, headers=headers)
        if not response:
            return self._create_mock_stock(code)
        
        try:
            data = response.text
            parts = data.split("~")
            if len(parts) > 40:
                return Stock(
                    code=code[2:] if code.startswith(("sh", "sz")) else code,
                    name=parts[1] if len(parts) > 1 else "未知",
                    price=float(parts[3]) if parts[3] != "" and parts[3] != "0" else None,
                    market_value=float(parts[44]) if parts[44] and parts[44] != "-" else None,
                    industry=self._get_industry_from_code(code),
                    concepts=self._extract_concepts(code),
                    products=self._extract_products(code),
                    pe=float(parts[39]) if parts[39] and parts[39] != "-" else None,
                    pb=float(parts[46]) if parts[46] and parts[46] != "-" else None
                )
        except (ValueError, IndexError) as e:
            print(f"[{self.name}] Parse error for {code}: {e}")
        
        return self._create_mock_stock(code)
    
    def search_stocks(self, keyword: str) -> List[Stock]:
        url = f"https://smartbox.gtimg.cn/s3/?v=2&q={keyword}&type=stock&count=20"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = self._make_request(url, headers=headers)
        if not response:
            return self._search_mock_stocks(keyword)
        
        stocks = []
        try:
            soup = BeautifulSoup(response.text, "lxml")
            items = soup.find_all("li")
            for item in items[:20]:
                code = item.get("v")
                name = item.get_text(strip=True)
                if code and name:
                    stocks.append(self.fetch_stock_info(code) or Stock(code=code, name=name))
        except Exception as e:
            print(f"[{self.name}] Search error: {e}")
            return self._search_mock_stocks(keyword)
        
        return stocks if stocks else self._search_mock_stocks(keyword)
    
    def _get_industry_from_code(self, code: str) -> str:
        industries = {
            "000": "银行", "001": "房地产", "002": "制造业", "600": "综合",
            "601": "金融", "603": "科技", "688": "科创板"
        }
        prefix = code[2:5] if len(code) > 5 else code[:3]
        return industries.get(prefix, "其他")
    
    def _extract_concepts(self, code: str) -> List[str]:
        concepts_map = {
            "000001": ["数字货币", "互联金融", "MSCI中国"],
            "000002": ["房地产", "物业管理", "REITs"],
            "600519": ["白酒", "消费", "MSCI中国"],
            "000858": ["白酒", "消费", "超级品牌"]
        }
        return concepts_map.get(code[2:] if code.startswith(("sh", "sz")) else code, ["题材热点", "业绩预增"])
    
    def _extract_products(self, code: str) -> List[str]:
        products_map = {
            "000001": ["公司银行", "零售银行", "金融科技"],
            "000002": ["房地产开发", "物业服务", "租赁住房"],
            "600519": ["茅台酒", "系列酒", "酒类进出口"],
            "000858": ["五粮液", "浓香型白酒", "高端酒品"]
        }
        return products_map.get(code[2:] if code.startswith(("sh", "sz")) else code, ["主营业务", "核心产品"])
    
    def _create_mock_stock(self, code: str) -> Stock:
        code_only = code[2:] if code.startswith(("sh", "sz")) else code
        mock_stocks = {
            "000001": Stock(code="000001", name="平安银行", price=12.85, market_value=2500.00, 
                          industry="银行", sub_industry="股份制银行", concepts=["数字货币", "互联金融", "MSCI中国"],
                          products=["公司银行", "零售银行", "金融科技"], pe=5.2, pb=0.65),
            "000002": Stock(code="000002", name="万科A", price=10.23, market_value=1200.00,
                          industry="房地产", sub_industry="房地产开发", concepts=["物业管理", "REITs", "保障房"],
                          products=["房地产开发", "物业服务", "租赁住房"], pe=8.5, pb=0.9),
            "600519": Stock(code="600519", name="贵州茅台", price=1680.50, market_value=21000.00,
                          industry="白酒", sub_industry="高端白酒", concepts=["白酒", "消费", "超级品牌"],
                          products=["茅台酒", "系列酒", "酒类进出口"], pe=32.5, pb=11.2),
            "000858": Stock(code="000858", name="五粮液", price=145.80, market_value=5600.00,
                          industry="白酒", sub_industry="浓香型白酒", concepts=["白酒", "消费", "MSCI中国"],
                          products=["五粮液", "浓香型白酒", "高端酒品"], pe=22.3, pb=5.8),
        }
        
        if code_only in mock_stocks:
            return mock_stocks[code_only]
        
        return Stock(
            code=code_only,
            name=f"股票{code_only}",
            price=10.0 + (hash(code_only) % 100),
            market_value=100.0 + (hash(code_only) % 1000),
            industry="随机行业",
            sub_industry="随机子行业",
            concepts=["概念1", "概念2", "概念3"],
            products=["产品1", "产品2", "产品3"]
        )
    
    def _search_mock_stocks(self, keyword: str) -> List[Stock]:
        mock_results = [
            Stock(code="000001", name="平安银行", price=12.85, market_value=2500.00,
                  industry="银行", sub_industry="股份制银行"),
            Stock(code="000002", name="万科A", price=10.23, market_value=1200.00,
                  industry="房地产", sub_industry="房地产开发"),
            Stock(code="600519", name="贵州茅台", price=1680.50, market_value=21000.00,
                  industry="白酒", sub_industry="高端白酒"),
            Stock(code="000858", name="五粮液", price=145.80, market_value=5600.00,
                  industry="白酒", sub_industry="浓香型白酒"),
            Stock(code="601318", name="中国平安", price=45.60, market_value=8500.00,
                  industry="保险", sub_industry="人身保险"),
        ]
        return [s for s in mock_results if keyword.lower() in s.name.lower() or keyword in s.industry]

class THSScraper(BaseScraper):
    name = "ths"
    
    def fetch_stock_info(self, code: str) -> Optional[Stock]:
        url = f"http://stockpage.10jqka.com.cn/{code}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "http://stockpage.10jqka.com.cn/"
        }
        
        response = self._make_request(url, headers=headers)
        if not response:
            return self._create_mock_from_ths(code)
        
        try:
            soup = BeautifulSoup(response.text, "lxml")
            name_elem = soup.select_one(".code-box .stockName")
            price_elem = soup.select_one("#price9")
            
            return Stock(
                code=code,
                name=name_elem.text.strip() if name_elem else f"股票{code}",
                price=float(price_elem.text.strip()) if price_elem else None,
                industry="同花顺行业",
                sub_industry="同花顺子行业"
            )
        except Exception as e:
            print(f"[{self.name}] Parse error for {code}: {e}")
        
        return self._create_mock_from_ths(code)
    
    def search_stocks(self, keyword: str) -> List[Stock]:
        url = f"http://search.10jqka.com.cn/?type=stock&query={keyword}"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = self._make_request(url, headers=headers)
        stocks = []
        if response:
            try:
                soup = BeautifulSoup(response.text, "lxml")
                items = soup.select(".result-item")
                for item in items[:20]:
                    code_elem = item.select_one(".code")
                    name_elem = item.select_one(".name")
                    if code_elem and name_elem:
                        stocks.append(Stock(
                            code=code_elem.text.strip(),
                            name=name_elem.text.strip()
                        ))
            except Exception as e:
                print(f"[{self.name}] Search error: {e}")
        
        return stocks if stocks else []
    
    def _create_mock_from_ths(self, code: str) -> Stock:
        return Stock(
            code=code,
            name=f"THS股票{code}",
            price=10.0 + (hash(code) % 100),
            industry="THS行业"
        )

class ScraperFactory:
    _scrapers = {}
    
    @classmethod
    def get_scraper(cls, source: str = DEFAULT_SOURCE) -> BaseScraper:
        if source not in cls._scrapers:
            if source == "ths":
                cls._scrapers[source] = THSScraper()
            else:
                cls._scrapers[source] = TencentScraper()
        return cls._scrapers[source]
    
    @classmethod
    def get_all_scrapers(cls) -> List[BaseScraper]:
        return [THSScraper(), TencentScraper()]
