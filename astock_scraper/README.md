# A股个股数据采集分析系统

## 项目简介

这是一个功能完整的A股个股数据自动化采集与分析工具，支持从多个金融平台批量抓取股票数据，并结合智能分析提供估值百分位、入场区间、止损位等投资参考信息。

## 功能特性

- **多数据源采集**: 支持同花顺、腾讯财经等平台
- **关键词搜索**: 按行业、概念、名称搜索股票
- **智能分析**: 估值百分位、入场区间、止损位、机会要点、核心风险
- **数据可视化**: 价格趋势图、行业对比图、雷达图
- **双入口**: CLI命令行工具 + Web演示页面

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动Web服务

```bash
python -m web.app
# 或使用启动脚本
bash run.sh
```

访问 http://localhost:5000 查看Web界面。

### 3. 使用CLI工具

```bash
# 采集指定股票
python cli/main.py scrape -C "000001,000002,600519"

# 按关键词搜索采集
python cli/main.py scrape --keyword 科技

# 查看股票列表
python cli/main.py list --sort price

# 分析单只股票
python cli/main.py analyze 000001 --chart

# 查看行业统计
python cli/main.py industries

# 导出数据到CSV
python cli/main.py export --industry 银行 -e output.csv
```

## 核心模块

| 模块 | 路径 | 说明 |
|------|------|------|
| 爬虫 | `core/scraper.py` | 数据采集核心，支持多数据源 |
| 清洗 | `core/cleaner.py` | 数据清洗与去重 |
| 分析 | `core/analyzer.py` | 智能分析引擎 |
| 数据库 | `core/database.py` | SQLite数据存储 |
| 可视化 | `visualization/charts.py` | 图表生成 |

## API接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/stocks` | GET | 获取股票列表 |
| `/api/stocks/<code>` | GET | 获取单只股票 |
| `/api/stocks` | POST | 添加股票 |
| `/api/stocks/<code>` | PUT | 更新股票 |
| `/api/stocks/<code>` | DELETE | 删除股票 |
| `/api/stocks/scrape` | POST | 触发数据采集 |
| `/api/stocks/<code>/chart` | GET | 获取趋势图数据 |
| `/api/industries` | GET | 获取行业统计 |

## Web界面功能

- 股票表格展示（支持排序、筛选、分页）
- 添加/编辑/删除股票
- 实时数据采集
- 价格趋势图表
- 分析结果展示
- CSV导出功能

## 数据字段

| 字段 | 说明 |
|------|------|
| code | 股票代码 |
| name | 股票名称 |
| price | 现价 |
| market_value | 流通市值 |
| industry | 所属行业 |
| sub_industry | 细分行业 |
| concepts | 所属概念（最多3个） |
| products | 核心产品（最多3个） |
| pe | 市盈率 |
| pb | 市净率 |

## 分析结果字段

| 字段 | 说明 |
|------|------|
| valuation_percentile | 估值百分位 |
| entry_min | 入场区间下限 |
| entry_max | 入场区间上限 |
| stop_loss | 止损位 |
| opportunity_points | 机会要点 |
| core_risks | 核心风险 |
| recommendation | 推荐评级 |

## 目录结构

```
astock_scraper/
├── cli/
│   └── main.py           # CLI入口
├── web/
│   ├── app.py            # Flask应用
│   └── templates/
│       └── index.html    # Web页面
├── core/
│   ├── scraper.py        # 爬虫模块
│   ├── cleaner.py        # 清洗模块
│   ├── analyzer.py       # 分析模块
│   └── database.py       # 数据库模块
├── models/
│   └── stock.py          # 数据模型
├── visualization/
│   └── charts.py         # 图表生成
├── data/                 # 数据存储
├── requirements.txt
├── config.py
└── run.sh/run.bat        # 启动脚本
```

## 配置说明

环境变量:

```bash
export DATABASE_URL="sqlite:///data/stocks.db"
export OPENAI_API_KEY="your-api-key"  # 可选，用于真实AI分析
```

## 注意事项

1. 数据仅供学习参考，不构成投资建议
2. 请遵守各数据源的使用条款
3. 建议设置合理的采集间隔，避免对目标服务器造成压力
4. 定期备份数据库文件

## License

MIT License
