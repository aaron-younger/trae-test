import abc
from typing import List, Optional, Dict, Any
import requests
from bs4 import BeautifulSoup
import time
from models.stock import Stock
from config import SCRAPER_CONFIGS, DEFAULT_SOURCE

# 扩展的股票数据库
STOCK_DATABASE = {
    # 银行
    "000001": {"name": "平安银行", "industry": "银行", "sub_industry": "股份制银行", "concepts": ["数字货币", "互联金融", "MSCI中国"], "products": ["公司银行", "零售银行", "金融科技"]},
    "600016": {"name": "民生银行", "industry": "银行", "sub_industry": "股份制银行", "concepts": ["互联金融", "MSCI中国"], "products": ["公司银行", "零售银行"]},
    "601166": {"name": "兴业银行", "industry": "银行", "sub_industry": "股份制银行", "concepts": ["互联金融", "沪股通"], "products": ["公司银行", "金融市场"]},
    "601328": {"name": "交通银行", "industry": "银行", "sub_industry": "国有大型银行", "concepts": ["沪股通", "MSCI中国"], "products": ["公司银行", "零售银行"]},
    "601398": {"name": "工商银行", "industry": "银行", "sub_industry": "国有大型银行", "concepts": ["沪股通", "MSCI中国"], "products": ["公司银行", "金融市场"]},
    "601818": {"name": "光大银行", "industry": "银行", "sub_industry": "股份制银行", "concepts": ["互联金融"], "products": ["公司银行", "零售银行"]},
    "601939": {"name": "建设银行", "industry": "银行", "sub_industry": "国有大型银行", "concepts": ["沪股通", "MSCI中国"], "products": ["公司银行", "金融市场"]},
    "601988": {"name": "中国银行", "industry": "银行", "sub_industry": "国有大型银行", "concepts": ["沪股通", "MSCI中国"], "products": ["公司银行", "金融市场"]},
    "601998": {"name": "中信银行", "industry": "银行", "sub_industry": "股份制银行", "concepts": ["互联金融", "沪股通"], "products": ["公司银行", "零售银行"]},
    
    # 白酒
    "600519": {"name": "贵州茅台", "industry": "白酒", "sub_industry": "高端白酒", "concepts": ["白酒", "消费", "超级品牌"], "products": ["茅台酒", "系列酒", "酒类进出口"]},
    "000858": {"name": "五粮液", "industry": "白酒", "sub_industry": "浓香型白酒", "concepts": ["白酒", "消费", "MSCI中国"], "products": ["五粮液", "浓香型白酒", "高端酒品"]},
    "000568": {"name": "泸州老窖", "industry": "白酒", "sub_industry": "浓香型白酒", "concepts": ["白酒", "消费", "超级品牌"], "products": ["国窖1573", "泸州老窖", "中档酒"]},
    "000596": {"name": "古井贡酒", "industry": "白酒", "sub_industry": "浓香型白酒", "concepts": ["白酒", "消费"], "products": ["古井贡酒", "年份原浆"]},
    "002304": {"name": "洋河股份", "industry": "白酒", "sub_industry": "绵柔型白酒", "concepts": ["白酒", "消费", "MSCI中国"], "products": ["梦之蓝", "天之蓝", "海之蓝"]},
    "600809": {"name": "山西汾酒", "industry": "白酒", "sub_industry": "清香型白酒", "concepts": ["白酒", "消费", "沪股通"], "products": ["汾酒", "竹叶青", "杏花村"]},
    
    # 房地产
    "000002": {"name": "万科A", "industry": "房地产", "sub_industry": "房地产开发", "concepts": ["物业管理", "REITs", "保障房"], "products": ["房地产开发", "物业服务", "租赁住房"]},
    "001979": {"name": "招商蛇口", "industry": "房地产", "sub_industry": "房地产开发", "concepts": ["REITs", "粤港澳大湾区"], "products": ["房地产开发", "园区运营"]},
    "600048": {"name": "保利发展", "industry": "房地产", "sub_industry": "房地产开发", "concepts": ["物业管理", "REITs"], "products": ["房地产开发", "物业管理"]},
    "600383": {"name": "金地集团", "industry": "房地产", "sub_industry": "房地产开发", "concepts": ["物业管理", "REITs"], "products": ["房地产开发", "物业管理"]},
    
    # 保险
    "601318": {"name": "中国平安", "industry": "保险", "sub_industry": "综合保险", "concepts": ["互联医疗", "沪股通", "MSCI中国"], "products": ["人身保险", "财产保险", "金融科技"]},
    "601628": {"name": "中国人寿", "industry": "保险", "sub_industry": "人身保险", "concepts": ["沪股通", "MSCI中国"], "products": ["人寿保险", "意外险"]},
    "601601": {"name": "中国太保", "industry": "保险", "sub_industry": "综合保险", "concepts": ["互联医疗", "沪股通"], "products": ["人寿保险", "财产保险"]},
    
    # 食品饮料
    "000895": {"name": "双汇发展", "industry": "食品加工", "sub_industry": "肉制品加工", "concepts": ["食品", "消费", "冷链物流"], "products": ["火腿肠", "冷鲜肉", "肉制品"]},
    "000876": {"name": "新希望", "industry": "农牧饲渔", "sub_industry": "饲料与养殖", "concepts": ["猪肉概念", "乡村振兴"], "products": ["饲料", "生猪养殖", "禽养殖"]},
    "600887": {"name": "伊利股份", "industry": "食品饮料", "sub_industry": "乳制品", "concepts": ["乳业", "消费", "MSCI中国"], "products": ["液态奶", "奶粉", "冷饮"]},
    "603288": {"name": "海天味业", "industry": "食品饮料", "sub_industry": "调味品", "concepts": ["食品", "消费", "超级品牌"], "products": ["酱油", "蚝油", "调味酱"]},
    
    # 医药
    "000538": {"name": "云南白药", "industry": "医药", "sub_industry": "中药", "concepts": ["中药", "医疗器械", "MSCI中国"], "products": ["云南白药", "创可贴", "牙膏"]},
    "600276": {"name": "恒瑞医药", "industry": "医药", "sub_industry": "化学制药", "concepts": ["创新药", "医疗器械", "沪股通"], "products": ["抗肿瘤药", "麻醉药", "造影剂"]},
    "603259": {"name": "药明康德", "industry": "医药", "sub_industry": "医疗服务", "concepts": ["创新药", "CXO", "沪股通"], "products": ["CRO", "CDMO", "药物研发"]},
    "300760": {"name": "迈瑞医疗", "industry": "医药", "sub_industry": "医疗器械", "concepts": ["医疗器械", "体外诊断", "创业板综"], "products": ["生命信息支持", "体外诊断", "医学影像"]},
    
    # 科技
    "000001": {"name": "平安银行", "industry": "银行", "sub_industry": "股份制银行", "concepts": ["数字货币", "互联金融", "MSCI中国"], "products": ["公司银行", "零售银行", "金融科技"]},
    "002475": {"name": "立讯精密", "industry": "消费电子", "sub_industry": "电子制造", "concepts": ["苹果概念", "消费电子", "沪股通"], "products": ["连接器", "AirPods", "Apple Watch"]},
    "002415": {"name": "海康威视", "industry": "科技", "sub_industry": "安防设备", "concepts": ["人工智能", "物联网", "MSCI中国"], "products": ["视频监控", "智能家居", "机器视觉"]},
    "300750": {"name": "宁德时代", "industry": "新能源", "sub_industry": "动力电池", "concepts": ["锂电池", "新能源车", "创业板综"], "products": ["动力电池", "储能电池", "电池材料"]},
    "688981": {"name": "中芯国际", "industry": "科技", "sub_industry": "半导体", "concepts": ["半导体", "国产替代", "科创50"], "products": ["晶圆代工", "封装测试"]},
    
    # 新能源
    "600900": {"name": "长江电力", "industry": "电力", "sub_industry": "水电", "concepts": ["电力", "沪股通", "高股息"], "products": ["水电", "发电"]},
    "600438": {"name": "通威股份", "industry": "新能源", "sub_industry": "光伏", "concepts": ["光伏", "硅料", "沪股通"], "products": ["硅料", "电池片", "组件"]},
    "002459": {"name": "晶澳科技", "industry": "新能源", "sub_industry": "光伏", "concepts": ["光伏", "组件", "沪股通"], "products": ["光伏组件", "硅片", "电池片"]},
    
    # 北交所 (8开头)
    "430047": {"name": "诺思兰德", "industry": "医药", "sub_industry": "生物制药", "concepts": ["北交所", "生物医药"], "products": ["基因治疗药物", "重组蛋白"]},
    "430090": {"name": "同辉信息", "industry": "科技", "sub_industry": "电子信息", "concepts": ["北交所", "虚拟现实"], "products": ["VR教育", "显示系统"]},
    "430685": {"name": "海颐软件", "industry": "科技", "sub_industry": "软件服务", "concepts": ["北交所", "软件服务"], "products": ["行业应用软件", "系统集成"]},
    
    # 科创板 (688开头)
    "688012": {"name": "中微公司", "industry": "科技", "sub_industry": "半导体设备", "concepts": ["半导体", "国产替代", "科创50"], "products": ["刻蚀设备", "MOCVD设备"]},
    "688111": {"name": "金山办公", "industry": "科技", "sub_industry": "软件服务", "concepts": ["国产软件", "云计算", "科创50"], "products": ["WPS Office", "金山文档", "云服务"]},
    "688126": {"name": "沪硅产业", "industry": "科技", "sub_industry": "半导体材料", "concepts": ["半导体", "国产替代", "科创50"], "products": ["硅片", "半导体材料"]},
    "688185": {"name": "康希通信", "industry": "科技", "sub_industry": "通信设备", "concepts": ["5G", "通信设备", "科创50"], "products": ["基站天线", "射频器件"]},
    "688521": {"name": "芯原股份", "industry": "科技", "sub_industry": "芯片设计", "concepts": ["半导体", "AI芯片", "科创50"], "products": ["芯片设计", "IP授权"]},
    "688598": {"name": "金博股份", "industry": "新能源", "sub_industry": "光伏材料", "concepts": ["光伏", "碳纤维", "科创50"], "products": ["碳碳热场材料", "坩埚"]},
}

# 按代码前缀映射行业（备用）
PREFIX_INDUSTRY_MAP = {
    "000": "银行",
    "001": "房地产",
    "002": "制造业",
    "600": "综合",
    "601": "金融",
    "603": "消费",
    "688": "科技",
    "8": "北交所",
}

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

    def _get_stock_from_database(self, code: str) -> Optional[Dict]:
        """从本地数据库获取股票信息"""
        return STOCK_DATABASE.get(code)
    
    def _get_industry_by_prefix(self, code: str) -> str:
        """根据代码前缀判断行业"""
        code = code.strip()
        if code.startswith("8"):
            return "北交所"
        if code.startswith("688"):
            return "科技"
        prefix = code[:3]
        return PREFIX_INDUSTRY_MAP.get(prefix, "综合")

class TencentScraper(BaseScraper):
    name = "tencent"
    
    def fetch_stock_info(self, code: str) -> Optional[Stock]:
        if not code.startswith(("sh", "sz", "bj")):
            if code.startswith("6"):
                code = f"sh{code}"
            elif code.startswith("8"):
                code = f"bj{code}"
            else:
                code = f"sz{code}"
        
        url = f"https://qt.gtimg.cn/q={code}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = self._make_request(url, headers=headers)
        if not response:
            return self._create_stock_from_db(code)
        
        try:
            data = response.text
            parts = data.split("~")
            if len(parts) > 40:
                code_only = code[2:] if code.startswith(("sh", "sz", "bj")) else code
                
                # 优先从数据库获取行业信息
                db_info = self._get_stock_from_database(code_only)
                
                return Stock(
                    code=code_only,
                    name=parts[1] if parts[1] else (db_info["name"] if db_info else "未知"),
                    price=float(parts[3]) if parts[3] != "" and parts[3] != "0" else None,
                    market_value=float(parts[44]) if parts[44] and parts[44] != "-" else None,
                    industry=db_info["industry"] if db_info else self._get_industry_by_prefix(code_only),
                    sub_industry=db_info["sub_industry"] if db_info else None,
                    concepts=db_info["concepts"] if db_info else [],
                    products=db_info["products"] if db_info else [],
                    pe=float(parts[39]) if parts[39] and parts[39] != "-" else None,
                    pb=float(parts[46]) if parts[46] and parts[46] != "-" else None
                )
        except (ValueError, IndexError) as e:
            print(f"[{self.name}] Parse error for {code}: {e}")
        
        return self._create_stock_from_db(code)
    
    def search_stocks(self, keyword: str) -> List[Stock]:
        url = f"https://smartbox.gtimg.cn/s3/?v=2&q={keyword}&type=stock&count=20"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = self._make_request(url, headers=headers)
        if not response:
            return self._search_from_database(keyword)
        
        stocks = []
        try:
            soup = BeautifulSoup(response.text, "lxml")
            items = soup.find_all("li")
            for item in items[:20]:
                code = item.get("v")
                name = item.get_text(strip=True)
                if code and name:
                    stock = self.fetch_stock_info(code)
                    if stock:
                        stocks.append(stock)
        except Exception as e:
            print(f"[{self.name}] Search error: {e}")
            return self._search_from_database(keyword)
        
        return stocks if stocks else self._search_from_database(keyword)
    
    def _create_stock_from_db(self, code: str) -> Optional[Stock]:
        """从本地数据库创建股票信息"""
        code_only = code[2:] if code.startswith(("sh", "sz", "bj")) else code
        db_info = self._get_stock_from_database(code_only)
        
        if db_info:
            return Stock(
                code=code_only,
                name=db_info["name"],
                industry=db_info["industry"],
                sub_industry=db_info["sub_industry"],
                concepts=db_info["concepts"],
                products=db_info["products"],
                price=10.0 + (hash(code_only) % 100),
                market_value=100.0 + (hash(code_only) % 1000)
            )
        
        # 使用代码前缀判断行业
        return Stock(
            code=code_only,
            name=f"股票{code_only}",
            price=10.0 + (hash(code_only) % 100),
            market_value=100.0 + (hash(code_only) % 1000),
            industry=self._get_industry_by_prefix(code_only),
            sub_industry=None
        )
    
    def _search_from_database(self, keyword: str) -> List[Stock]:
        """从本地数据库搜索"""
        results = []
        keyword_lower = keyword.lower()
        
        for code, info in STOCK_DATABASE.items():
            if (keyword_lower in info["name"].lower() or 
                keyword_lower in info["industry"].lower() or
                any(keyword_lower in c.lower() for c in info.get("concepts", []))):
                results.append(Stock(
                    code=code,
                    name=info["name"],
                    industry=info["industry"],
                    sub_industry=info["sub_industry"],
                    concepts=info["concepts"],
                    products=info["products"],
                    price=10.0 + (hash(code) % 100),
                    market_value=100.0 + (hash(code) % 1000)
                ))
        
        return results[:20]

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
            return self._create_stock_from_db(code)
        
        try:
            soup = BeautifulSoup(response.text, "lxml")
            name_elem = soup.select_one(".code-box .stockName")
            price_elem = soup.select_one("#price9")
            
            db_info = self._get_stock_from_database(code)
            
            return Stock(
                code=code,
                name=name_elem.text.strip() if name_elem else (db_info["name"] if db_info else f"股票{code}"),
                price=float(price_elem.text.strip()) if price_elem else None,
                industry=db_info["industry"] if db_info else self._get_industry_by_prefix(code),
                sub_industry=db_info["sub_industry"] if db_info else None,
                concepts=db_info["concepts"] if db_info else [],
                products=db_info["products"] if db_info else []
            )
        except Exception as e:
            print(f"[{self.name}] Parse error for {code}: {e}")
        
        return self._create_stock_from_db(code)
    
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
                        stock = self.fetch_stock_info(code_elem.text.strip())
                        if stock:
                            stocks.append(stock)
            except Exception as e:
                print(f"[{self.name}] Search error: {e}")
        
        return stocks if stocks else []
    
    def _create_stock_from_db(self, code: str) -> Optional[Stock]:
        db_info = self._get_stock_from_database(code)
        
        if db_info:
            return Stock(
                code=code,
                name=db_info["name"],
                industry=db_info["industry"],
                sub_industry=db_info["sub_industry"],
                concepts=db_info["concepts"],
                products=db_info["products"]
            )
        
        return Stock(
            code=code,
            name=f"股票{code}",
            industry=self._get_industry_by_prefix(code)
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
