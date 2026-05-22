# A股个股数据自动化采集与分析工具

一个用于采集和分析A股股票数据的Python工具，支持多种数据源和技术指标计算。

## 功能特点

- **多数据源支持**: 集成 Tushare 和 AkShare 数据源
- **数据采集**: 支持日线数据、分钟数据、财务报告、分红信息
- **技术指标计算**: 
  - 移动平均线 (MA5, MA10, MA20, MA60)
  - 相对强弱指数 (RSI)
  - MACD 指标
  - 布林带
  - 日收益率和累计收益率
- **数据可视化**: 支持蜡烛图、价格均线图、RSI图
- **关注列表管理**: 管理常用股票列表
- **数据导出**: 支持导出为CSV文件

## 安装依赖

```bash
pip install pandas numpy tushare akshare matplotlib mplfinance
```

## 使用方法

### 基本用法

```bash
# 获取单只股票数据
python main.py -s 600519.SH

# 获取指定天数的数据
python main.py -s 600519.SH -d 180

# 获取数据并导出到CSV
python main.py -s 600519.SH -o

# 获取财务数据
python main.py -s 600519.SH -f

# 获取分红信息
python main.py -s 600519.SH -div

# 绘制图表
python main.py -s 600519.SH -p
```

### 关注列表管理

```bash
# 查看关注列表
python main.py -w

# 添加股票到关注列表
python main.py -a 000001.SZ

# 从关注列表移除股票
python main.py -r 000001.SZ
```

### 设置 Tushare Token

```bash
python main.py -t your_tushare_token
```

### 列出已保存的数据文件

```bash
python main.py -l
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| -s, --symbol | 股票代码，如 000001.SZ |
| -d, --days | 获取数据天数，默认365天 |
| -w, --watchlist | 查看关注列表 |
| -a, --add | 添加股票到关注列表 |
| -r, --remove | 从关注列表移除股票 |
| -t, --token | 设置Tushare token |
| -f, --financial | 获取财务数据 |
| -div, --dividend | 获取分红信息 |
| -o, --output | 输出数据到CSV |
| -p, --plot | 绘制图表 |
| -l, --list | 列出已保存的数据文件 |

## 支持的股票代码格式

- 深圳市场: 000001.SZ
- 上海市场: 600519.SH

## 项目结构

```
├── main.py          # 主程序入口
├── config.json      # 配置文件
├── data/            # 数据存储目录
│   └── *.csv        # 导出的CSV数据文件
└── README.md        # 项目说明文档
```

## 注意事项

1. 使用 Tushare 数据源需要注册账号并获取 token
2. AkShare 数据源无需注册，但数据获取频率有限制
3. 建议使用 Tushare 获取更稳定和完整的数据
4. 首次使用前建议设置 Tushare token 以获得更好的数据服务

## 许可证

MIT License
