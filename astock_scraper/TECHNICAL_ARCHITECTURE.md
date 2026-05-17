# A股数据采集系统 - 技术架构文档

## 1. 系统架构

### 1.1 整体架构
```
┌────────────────────────────────────────────────────────────┐
│                      Presentation Layer                     │
│  ┌─────────────────┐           ┌─────────────────────────┐ │
│  │  CLI Interface  │           │    Web Dashboard        │ │
│  │  (Click/Typer)  │           │    (React + AntD)       │ │
│  └─────────────────┘           └─────────────────────────┘ │
├────────────────────────────────────────────────────────────┤
│                       API Layer                             │
│              Flask REST API (Port 5000)                    │
├────────────────────────────────────────────────────────────┤
│                    Business Logic Layer                     │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ │
│  │ Scraper   │ │ Cleaner   │ │ Analyzer  │ │ Chart     │ │
│  │ Engine    │ │ Engine    │ │ Engine    │ │ Generator │ │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘ │
├────────────────────────────────────────────────────────────┤
│                      Data Access Layer                      │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│    │ SQLite   │  │ CSV/Excel│  │ Cache    │               │
│    └──────────┘  └──────────┘  └──────────┘               │
├────────────────────────────────────────────────────────────┤
│                   External Data Sources                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ 同花顺   │  │ 腾讯财经  │  │ 东方财富  │  │ Mootdx   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└────────────────────────────────────────────────────────────┘
```

### 2. 核心模块设计

### 2.1 数据采集模块 (Scraper Engine)
```python
# 数据源策略模式
class DataSource(ABC):
    @abstractmethod
    def fetch_stock_info(self, code: str) -> StockInfo: pass
    
class THSScraper(DataSource):
    def fetch_stock_info(self, code: str) -> StockInfo:
        # 同花顺API调用
        pass

class TencentScraper(DataSource):
    def fetch_stock_info(self, code: str) -> StockInfo:
        # 腾讯财经爬虫
        pass

class ScraperFactory:
    @staticmethod
    def create_scraper(source: str) -> DataSource:
        scrapers = {
            "ths": THSScraper,
            "tencent": TencentScraper,
            "mootdx": MootdxScraper
        }
        return scrapers.get(source, TencentScraper)()
```

### 2.2 数据清洗模块 (Cleaner Engine)
```python
class DataCleaner:
    def clean(self, raw_data: List[Dict]) -> List[Dict]:
        pipeline = [
            RemoveNulls(),
            StandardizeFormat(),
            Deduplicate(),
            ValidateData()
        ]
        for step in pipeline:
            raw_data = step.process(raw_data)
        return raw_data
```

### 2.3 分析模块 (Analyzer Engine)
```python
class StockAnalyzer:
    def analyze(self, stock: StockInfo) -> AnalysisResult:
        return {
            "valuation_percentile": self.calc_percentile(stock),
            "entry_range": self.calc_entry_range(stock),
            "stop_loss": self.calc_stop_loss(stock),
            "opportunity_points": self.extract_opportunities(stock),
            "core_risks": self.extract_risks(stock)
        }
```

### 2.4 可视化模块 (Chart Generator)
```python
class ChartGenerator:
    def generate_price_trend(self, code: str) -> str:
        # 生成HTML/PNG格式的价格趋势图
        
    def generate_industry_comparison(self, stocks: List[Stock]) -> str:
        # 生成行业对比图
```

### 3. 数据流设计

### 3.1 CLI命令执行流程
```
User Input → CLI Parser → Scraper Factory → 
Data Sources → Cleaner Pipeline → Analyzer Engine → 
Result Formatter → CSV/Excel Output
```

### 3.2 Web请求处理流程
```
HTTP Request → Flask Route → Scraper/DB Layer →
Response JSON → React Component → UI Render
```

### 4. API接口设计

### 4.1 REST API
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/stocks | 获取股票列表 |
| GET | /api/stocks/{code} | 获取单只股票详情 |
| POST | /api/stocks/search | 关键词搜索 |
| POST | /api/stocks/scrape | 触发数据采集 |
| PUT | /api/stocks/{code} | 更新股票信息 |
| DELETE | /api/stocks/{code} | 删除股票 |
| GET | /api/stocks/{code}/chart | 获取趋势图 |
| GET | /api/stocks/{code}/analysis | 获取分析结果 |

### 5. 数据存储方案

### 5.1 SQLite Schema
```sql
CREATE TABLE stocks (
    id INTEGER PRIMARY KEY,
    code VARCHAR(10) UNIQUE,
    name VARCHAR(50),
    market_value REAL,
    price REAL,
    industry VARCHAR(50),
    sub_industry VARCHAR(50),
    concepts TEXT,
    products TEXT,
    pe REAL,
    pb REAL,
    update_time DATETIME
);

CREATE TABLE analysis_results (
    id INTEGER PRIMARY KEY,
    stock_code VARCHAR(10),
    valuation_percentile REAL,
    entry_min REAL,
    entry_max REAL,
    stop_loss REAL,
    opportunity_points TEXT,
    core_risks TEXT,
    recommendation VARCHAR(20),
    FOREIGN KEY(stock_code) REFERENCES stocks(code)
);
```

### 6. 依赖包清单

```
flask>=2.0.0
flask-cors>=3.0.0
pandas>=1.3.0
requests>=2.25.0
beautifulsoup4>=4.9.0
lxml>=4.6.0
plotly>=5.0.0
kaleido>=0.2.0
mootdx>=0.8.0
python-dotenv>=0.19.0
click>=8.0.0
rich>=10.0.0
SQLAlchemy>=1.4.0
openai>=1.0.0
```

### 7. 部署方案

### 7.1 开发环境
```bash
pip install -r requirements.txt
python cli/main.py scrape --keyword 科技
python -m flask --app web/app.py run
```

### 7.2 目录结构
```
astock_scraper/
├── cli/
│   └── main.py              # CLI入口
├── web/
│   ├── app.py               # Flask应用
│   ├── static/
│   └── templates/
├── core/
│   ├── scraper/             # 爬虫模块
│   ├── cleaner.py           # 清洗模块
│   ├── analyzer.py          # 分析模块
│   └── database.py          # 数据库模块
├── models/
│   └── stock.py             # 数据模型
├── visualization/
│   └── charts.py            # 图表生成
├── utils/
│   └── helpers.py           # 工具函数
├── requirements.txt
└── config.py                # 配置文件
```
