import sys
import os
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import argparse
import json

try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False

try:
    import akshare as ak
    AK_SHARE_AVAILABLE = True
except ImportError:
    AK_SHARE_AVAILABLE = False

class StockDataCollector:
    def __init__(self):
        self.data_dir = 'data'
        self.config_file = 'config.json'
        self._create_data_dir()
        self.config = self._load_config()
        self._init_api()
    
    def _convert_symbol(self, symbol):
        if symbol.endswith('.SH'):
            return 'sh' + symbol.replace('.SH', '')
        elif symbol.endswith('.SZ'):
            return 'sz' + symbol.replace('.SZ', '')
        return symbol
    
    def _create_data_dir(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'tushare_token': '',
            'last_update': '',
            'watchlist': ['000001.SZ', '600519.SH', '000858.SZ']
        }
    
    def _save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def _init_api(self):
        if TUSHARE_AVAILABLE and self.config.get('tushare_token'):
            ts.set_token(self.config['tushare_token'])
            self.pro = ts.pro_api()
    
    def set_tushare_token(self, token):
        self.config['tushare_token'] = token
        self._save_config()
        self._init_api()
    
    def add_to_watchlist(self, symbol):
        if symbol not in self.config['watchlist']:
            self.config['watchlist'].append(symbol)
            self._save_config()
    
    def remove_from_watchlist(self, symbol):
        if symbol in self.config['watchlist']:
            self.config['watchlist'].remove(symbol)
            self._save_config()
    
    def get_watchlist(self):
        return self.config['watchlist']
    
    def get_stock_basic_info(self, symbol):
        try:
            if TUSHARE_AVAILABLE and hasattr(self, 'pro'):
                df = self.pro.stock_basic(ts_code=symbol)
                if not df.empty:
                    return df.iloc[0].to_dict()
            if AK_SHARE_AVAILABLE:
                df = ak.stock_zh_a_spot()
                df = df[df['代码'] == symbol.replace('.SZ', '').replace('.SH', '')]
                if not df.empty:
                    return df.iloc[0].to_dict()
        except Exception as e:
            print(f"获取股票基本信息失败: {e}")
        return None
    
    def get_daily_data(self, symbol, start_date=None, end_date=None):
        end_date = end_date or datetime.now().strftime('%Y%m%d')
        start_date = start_date or (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        
        try:
            if TUSHARE_AVAILABLE and hasattr(self, 'pro'):
                df = self.pro.daily(ts_code=symbol, start_date=start_date, end_date=end_date)
                if not df.empty:
                    df = df.sort_values('trade_date')
                    return df
            if AK_SHARE_AVAILABLE:
                ak_symbol = self._convert_symbol(symbol)
                df = ak.stock_zh_a_daily(symbol=ak_symbol, start_date=start_date, end_date=end_date, adjust='hfq')
                if not df.empty:
                    return df
        except Exception as e:
            print(f"获取日线数据失败: {e}")
        return None
    
    def get_minute_data(self, symbol, freq='1min', count=60):
        try:
            if AK_SHARE_AVAILABLE:
                df = ak.stock_zh_a_minute(symbol=symbol, period=freq)
                if not df.empty:
                    return df.tail(count)
        except Exception as e:
            print(f"获取分钟数据失败: {e}")
        return None
    
    def get_financial_report(self, symbol):
        try:
            if TUSHARE_AVAILABLE and hasattr(self, 'pro'):
                df = self.pro.fina_indicator(ts_code=symbol)
                if not df.empty:
                    return df.iloc[0].to_dict()
        except Exception as e:
            print(f"获取财务报告失败: {e}")
        return None
    
    def get_dividend_info(self, symbol):
        try:
            if TUSHARE_AVAILABLE and hasattr(self, 'pro'):
                df = self.pro.dividend(ts_code=symbol)
                if not df.empty:
                    return df.head(10).to_dict('records')
        except Exception as e:
            print(f"获取分红信息失败: {e}")
        return None
    
    def save_to_csv(self, df, filename):
        filepath = os.path.join(self.data_dir, filename)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"数据已保存到: {filepath}")
        return filepath
    
    def load_from_csv(self, filename):
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            return pd.read_csv(filepath, encoding='utf-8-sig')
        return None


class StockAnalyzer:
    @staticmethod
    def calculate_moving_average(df, window):
        if 'close' in df.columns:
            df[f'ma{window}'] = df['close'].rolling(window=window).mean()
        elif '收盘' in df.columns:
            df[f'ma{window}'] = df['收盘'].rolling(window=window).mean()
        return df
    
    @staticmethod
    def calculate_rsi(df, window=14):
        if 'close' in df.columns:
            delta = df['close'].diff()
        elif '收盘' in df.columns:
            delta = df['收盘'].diff()
        else:
            return df
        
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df
    
    @staticmethod
    def calculate_macd(df, fast=12, slow=26, signal=9):
        if 'close' in df.columns:
            df['ema_fast'] = df['close'].ewm(span=fast, adjust=False).mean()
            df['ema_slow'] = df['close'].ewm(span=slow, adjust=False).mean()
        elif '收盘' in df.columns:
            df['ema_fast'] = df['收盘'].ewm(span=fast, adjust=False).mean()
            df['ema_slow'] = df['收盘'].ewm(span=slow, adjust=False).mean()
        else:
            return df
        
        df['macd'] = df['ema_fast'] - df['ema_slow']
        df['signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        df['histogram'] = df['macd'] - df['signal']
        return df
    
    @staticmethod
    def calculate_bollinger_bands(df, window=20, num_std=2):
        if 'close' in df.columns:
            df['bb_middle'] = df['close'].rolling(window=window).mean()
            df['bb_std'] = df['close'].rolling(window=window).std()
        elif '收盘' in df.columns:
            df['bb_middle'] = df['收盘'].rolling(window=window).mean()
            df['bb_std'] = df['收盘'].rolling(window=window).std()
        else:
            return df
        
        df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * num_std)
        df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * num_std)
        return df
    
    @staticmethod
    def calculate_daily_return(df):
        if 'close' in df.columns:
            df['daily_return'] = df['close'].pct_change()
        elif '收盘' in df.columns:
            df['daily_return'] = df['收盘'].pct_change()
        return df
    
    @staticmethod
    def calculate_cumulative_return(df):
        if 'daily_return' in df.columns:
            df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
        return df
    
    @staticmethod
    def get_summary_stats(df):
        if 'daily_return' in df.columns:
            stats = {
                'total_return': df['daily_return'].sum() * 100,
                'avg_daily_return': df['daily_return'].mean() * 100,
                'std_dev': df['daily_return'].std() * 100,
                'max_return': df['daily_return'].max() * 100,
                'min_return': df['daily_return'].min() * 100,
                'sharpe_ratio': (df['daily_return'].mean() / df['daily_return'].std()) * np.sqrt(252) if df['daily_return'].std() != 0 else 0,
                'days': len(df)
            }
            return stats
        return None


class StockDataVisualizer:
    @staticmethod
    def plot_candlestick(df, symbol):
        try:
            import mplfinance as mpf
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df.set_index('trade_date', inplace=True)
            mpf.plot(df, type='candle', volume=True, title=f'{symbol} 蜡烛图', mav=(5, 10, 20))
        except ImportError:
            print("请安装 mplfinance 库以绘制蜡烛图: pip install mplfinance")
        except Exception as e:
            print(f"绘制蜡烛图失败: {e}")
    
    @staticmethod
    def plot_price_with_ma(df, symbol):
        try:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(12, 6))
            plt.plot(df['close'], label='收盘价')
            if 'ma5' in df.columns:
                plt.plot(df['ma5'], label='MA5')
            if 'ma10' in df.columns:
                plt.plot(df['ma10'], label='MA10')
            if 'ma20' in df.columns:
                plt.plot(df['ma20'], label='MA20')
            plt.title(f'{symbol} 价格与均线')
            plt.legend()
            plt.grid(True)
            plt.show()
        except ImportError:
            print("请安装 matplotlib 库以绘制图表: pip install matplotlib")
        except Exception as e:
            print(f"绘制价格图失败: {e}")
    
    @staticmethod
    def plot_rsi(df, symbol):
        try:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(12, 4))
            plt.plot(df['rsi'], label='RSI')
            plt.axhline(70, color='red', linestyle='--')
            plt.axhline(30, color='green', linestyle='--')
            plt.title(f'{symbol} RSI指标')
            plt.legend()
            plt.grid(True)
            plt.show()
        except ImportError:
            print("请安装 matplotlib 库以绘制图表: pip install matplotlib")
        except Exception as e:
            print(f"绘制RSI图失败: {e}")


def print_summary(symbol, basic_info, stats):
    print("\n" + "="*60)
    print(f"股票代码: {symbol}")
    if basic_info:
        print(f"股票名称: {basic_info.get('name', basic_info.get('名称', '未知'))}")
        print(f"行业: {basic_info.get('industry', basic_info.get('行业', '未知'))}")
        print(f"上市日期: {basic_info.get('list_date', basic_info.get('上市日期', '未知'))}")
    if stats:
        print("\n统计摘要:")
        print(f"交易天数: {stats['days']}")
        print(f"总收益率: {stats['total_return']:.2f}%")
        print(f"日均收益率: {stats['avg_daily_return']:.2f}%")
        print(f"标准差: {stats['std_dev']:.2f}%")
        print(f"最大单日收益: {stats['max_return']:.2f}%")
        print(f"最大单日亏损: {stats['min_return']:.2f}%")
        print(f"夏普比率: {stats['sharpe_ratio']:.2f}")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(description='A股个股数据自动化采集与分析工具')
    parser.add_argument('-s', '--symbol', type=str, help='股票代码，如 000001.SZ')
    parser.add_argument('-d', '--days', type=int, default=365, help='获取数据天数')
    parser.add_argument('-w', '--watchlist', action='store_true', help='查看关注列表')
    parser.add_argument('-a', '--add', type=str, help='添加股票到关注列表')
    parser.add_argument('-r', '--remove', type=str, help='从关注列表移除股票')
    parser.add_argument('-t', '--token', type=str, help='设置Tushare token')
    parser.add_argument('-f', '--financial', action='store_true', help='获取财务数据')
    parser.add_argument('-div', '--dividend', action='store_true', help='获取分红信息')
    parser.add_argument('-o', '--output', action='store_true', help='输出数据到CSV')
    parser.add_argument('-p', '--plot', action='store_true', help='绘制图表')
    parser.add_argument('-l', '--list', action='store_true', help='列出已保存的数据文件')
    
    args = parser.parse_args()
    
    collector = StockDataCollector()
    
    if args.token:
        collector.set_tushare_token(args.token)
        print("Tushare token已设置")
        return
    
    if args.list:
        files = [f for f in os.listdir('data') if f.endswith('.csv')]
        print("已保存的数据文件:")
        for f in files:
            print(f"  - {f}")
        return
    
    if args.watchlist:
        watchlist = collector.get_watchlist()
        print("关注列表:")
        for symbol in watchlist:
            basic = collector.get_stock_basic_info(symbol)
            name = basic.get('name', basic.get('名称', '未知')) if basic else '未知'
            print(f"  - {symbol} ({name})")
        return
    
    if args.add:
        collector.add_to_watchlist(args.add)
        print(f"已添加 {args.add} 到关注列表")
        return
    
    if args.remove:
        collector.remove_from_watchlist(args.remove)
        print(f"已从关注列表移除 {args.remove}")
        return
    
    if not args.symbol:
        print("请指定股票代码，使用 -s 参数")
        return
    
    print(f"正在获取 {args.symbol} 的数据...")
    
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=args.days)).strftime('%Y%m%d')
    
    df = collector.get_daily_data(args.symbol, start_date, end_date)
    
    if df is None or df.empty:
        print("未能获取数据")
        return
    
    basic_info = collector.get_stock_basic_info(args.symbol)
    
    analyzer = StockAnalyzer()
    df = analyzer.calculate_moving_average(df, 5)
    df = analyzer.calculate_moving_average(df, 10)
    df = analyzer.calculate_moving_average(df, 20)
    df = analyzer.calculate_moving_average(df, 60)
    df = analyzer.calculate_rsi(df)
    df = analyzer.calculate_macd(df)
    df = analyzer.calculate_bollinger_bands(df)
    df = analyzer.calculate_daily_return(df)
    df = analyzer.calculate_cumulative_return(df)
    
    stats = analyzer.get_summary_stats(df)
    print_summary(args.symbol, basic_info, stats)
    
    if args.financial:
        financial = collector.get_financial_report(args.symbol)
        if financial:
            print("\n财务指标:")
            for key, value in financial.items():
                print(f"  {key}: {value}")
    
    if args.dividend:
        dividend = collector.get_dividend_info(args.symbol)
        if dividend:
            print("\n分红信息:")
            for item in dividend:
                print(f"  {item.get('end_date', '')}: 每10股派现 {item.get('cash_div', 0)}元")
    
    if args.output:
        filename = f"{args.symbol}_{start_date}_{end_date}.csv"
        collector.save_to_csv(df, filename)
    
    if args.plot:
        visualizer = StockDataVisualizer()
        visualizer.plot_price_with_ma(df, args.symbol)
        visualizer.plot_rsi(df, args.symbol)


if __name__ == '__main__':
    main()
