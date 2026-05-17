import click
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.panel import Panel
from pathlib import Path
import sys
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.scraper import ScraperFactory
from core.cleaner import CleanerPipeline
from core.analyzer import StockAnalyzer
from core.database import Database
from visualization.charts import ChartGenerator
from models.stock import Stock, AnalysisResult
import pandas as pd

console = Console()

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """A股个股数据采集分析工具"""
    pass

@cli.command()
@click.option("--code", "-c", help="股票代码")
@click.option("--codes", "-C", help="股票代码列表，逗号分隔")
@click.option("--keyword", "-k", help="搜索关键词")
@click.option("--source", "-s", default="tencent", type=click.Choice(["ths", "tencent", "all"]), help="数据源")
@click.option("--save/--no-save", default=True, help="保存到数据库")
@click.option("--analyze/--no-analyze", default=True, help="是否分析")
@click.option("--export", "-e", type=click.Path(), help="导出文件路径")
def scrape(code, codes, keyword, source, save, analyze, export):
    """采集股票数据"""
    console.print(Panel.fit("[bold cyan]A股数据采集工具[/bold cyan]", border_style="cyan"))
    
    db = Database()
    scraper_factory = ScraperFactory()
    cleaner = CleanerPipeline()
    analyzer = StockAnalyzer()
    
    stocks_to_fetch = []
    
    if code:
        stocks_to_fetch.append(code)
    elif codes:
        stocks_to_fetch = [c.strip() for c in codes.split(",")]
    elif keyword:
        console.print(f"[yellow]搜索关键词: {keyword}[/yellow]")
        scraper = scraper_factory.get_scraper("tencent")
        search_results = scraper.search_stocks(keyword)
        if search_results:
            stocks_to_fetch = [s.code for s in search_results]
            console.print(f"[green]找到 {len(stocks_to_fetch)} 只相关股票[/green]")
        else:
            console.print("[red]未找到相关股票[/red]")
            return
    else:
        stocks_to_fetch = ["000001", "000002", "600519", "000858", "601318"]
    
    console.print(f"[cyan]开始采集 {len(stocks_to_fetch)} 只股票...[/cyan]")
    
    raw_stocks = []
    for code in track(stocks_to_fetch, description="采集进度"):
        scraper = scraper_factory.get_scraper(source)
        stock = scraper.fetch_stock_info(code)
        if stock:
            raw_stocks.append(stock)
    
    console.print(f"[green]✓ 成功采集 {len(raw_stocks)} 只股票[/green]")
    
    console.print("[cyan]清洗数据...[/cyan]")
    cleaned_stocks = cleaner.process(raw_stocks)
    console.print(f"[green]✓ 清洗后剩余 {len(cleaned_stocks)} 只股票[/green]")
    
    if save:
        saved_count = db.save_stocks(cleaned_stocks)
        console.print(f"[green]✓ 已保存 {saved_count} 只股票到数据库[/green]")
    
    analyses = []
    if analyze:
        console.print("[cyan]分析数据...[/cyan]")
        analyses = analyzer.analyze_batch(cleaned_stocks)
        for a in analyses:
            db.save_analysis(a)
        console.print(f"[green]✓ 完成 {len(analyses)} 个分析[/green]")
    
    if export:
        df = db.to_dataframe(cleaned_stocks)
        if analyses:
            analysis_df = pd.DataFrame([a.to_dict() for a in analyses])
            df = df.merge(analysis_df[["code", "valuation_percentile", "entry_min", "entry_max", 
                                        "stop_loss", "recommendation"]], on="code", how="left")
        df.to_csv(export, index=False, encoding="utf-8-sig")
        console.print(f"[green]✓ 已导出到 {export}[/green]")
    
    display_stocks(cleaned_stocks, analyses)

@cli.command()
@click.option("--industry", "-i", help="按行业筛选")
@click.option("--sort", "-s", default="industry", type=click.Choice(["code", "name", "price", "industry"]), help="排序字段")
@click.option("--limit", "-l", type=int, default=50, help="显示数量")
def list(industry, sort, limit):
    """列出股票列表"""
    db = Database()
    stocks = db.get_all_stocks(industry=industry)
    
    if sort == "code":
        stocks.sort(key=lambda x: x.code)
    elif sort == "name":
        stocks.sort(key=lambda x: x.name)
    elif sort == "price":
        stocks.sort(key=lambda x: x.price or 0, reverse=True)
    elif sort == "industry":
        stocks.sort(key=lambda x: (x.industry or "", x.sub_industry or ""))
    
    stocks = stocks[:limit]
    
    display_stocks(stocks)

@cli.command()
@click.argument("keyword")
def search(keyword):
    """搜索股票"""
    db = Database()
    results = db.search_stocks(keyword)
    
    if not results:
        console.print(f"[yellow]未找到包含 '{keyword}' 的股票[/yellow]")
        return
    
    console.print(f"[green]找到 {len(results)} 只股票:[/green]")
    display_stocks(results)

@cli.command()
@click.argument("code")
@click.option("--chart/--no-chart", default=True, help="生成图表")
def analyze(code, chart):
    """分析单只股票"""
    db = Database()
    stock = db.get_stock(code)
    
    if not stock:
        console.print(f"[red]未找到股票 {code}[/red]")
        return
    
    analyzer = StockAnalyzer()
    analysis = analyzer.analyze(stock)
    db.save_analysis(analysis)
    
    console.print(Panel.fit(
        f"[bold]{stock.name}[/bold] ({stock.code})\n\n"
        f"现价: [yellow]{stock.price}[/yellow]\n"
        f"行业: {stock.industry} > {stock.sub_industry}\n"
        f"概念: {', '.join(stock.concepts[:3]) if stock.concepts else '无'}\n\n"
        f"[bold cyan]分析结果[/bold cyan]\n"
        f"估值百分位: [cyan]{analysis.valuation_percentile:.1f}%[/cyan]\n"
        f"推荐评级: [green]{analysis.recommendation}[/green]\n"
        f"入场区间: {analysis.entry_min:.2f} - {analysis.entry_max:.2f}\n"
        f"止损位: [red]{analysis.stop_loss:.2f}[/red]\n\n"
        f"[bold green]机会要点[/bold green]\n"
        + "\n".join([f"• {p}" for p in analysis.opportunity_points]) + "\n\n"
        f"[bold red]核心风险[/bold red]\n"
        + "\n".join([f"• {r}" for r in analysis.core_risks]),
        border_style="cyan"
    ))
    
    if chart:
        chart_gen = ChartGenerator()
        chart_path = chart_gen.generate_price_trend(stock.code, stock.name)
        console.print(f"[green]✓ 图表已生成: {chart_path}[/green]")

@cli.command()
@click.option("--code", "-c", help="股票代码")
@click.option("--industry", "-i", help="行业")
@click.option("--export", "-e", type=click.Path(), help="导出文件路径")
def export(code, industry, export):
    """导出股票数据"""
    db = Database()
    
    if code:
        stock = db.get_stock(code)
        stocks = [stock] if stock else []
    elif industry:
        stocks = db.get_all_stocks(industry=industry)
    else:
        stocks = db.get_all_stocks()
    
    if not stocks:
        console.print("[yellow]没有可导出的数据[/yellow]")
        return
    
    analyses = [db.get_analysis(s.code) for s in stocks]
    analyses = [a for a in analyses if a]
    
    df = db.to_dataframe(stocks)
    
    if analyses:
        analysis_df = pd.DataFrame([a.to_dict() for a in analyses])
        analysis_cols = ["valuation_percentile", "entry_min", "entry_max", 
                         "stop_loss", "recommendation"]
        merge_cols = ["code"] + [c for c in analysis_cols if c in analysis_df.columns]
        df = df.merge(analysis_df[merge_cols], on="code", how="left")
    
    if export:
        df.to_csv(export, index=False, encoding="utf-8-sig")
        console.print(f"[green]✓ 已导出到 {export}[/green]")
    else:
        console.print(df.to_string())

@cli.command()
def industries():
    """显示行业统计"""
    db = Database()
    stocks = db.get_all_stocks()
    
    industries = {}
    for s in stocks:
        if s.industry:
            if s.industry not in industries:
                industries[s.industry] = {"count": 0, "sub_industries": set(), "total_value": 0}
            industries[s.industry]["count"] += 1
            if s.sub_industry:
                industries[s.industry]["sub_industries"].add(s.sub_industry)
            if s.market_value:
                industries[s.industry]["total_value"] += s.market_value
    
    table = Table(title="行业统计")
    table.add_column("行业", style="cyan")
    table.add_column("股票数量", justify="right")
    table.add_column("细分行业", style="yellow")
    table.add_column("总市值(亿)", justify="right")
    
    sorted_industries = sorted(industries.items(), key=lambda x: x[1]["total_value"], reverse=True)
    
    for name, data in sorted_industries:
        value_str = f"{data['total_value']/1e8:.2f}" if data['total_value'] else "N/A"
        table.add_row(
            name,
            str(data["count"]),
            str(len(data["sub_industries"])),
            value_str
        )
    
    console.print(table)

def display_stocks(stocks: list, analyses: list = None):
    if not stocks:
        console.print("[yellow]没有数据[/yellow]")
        return
    
    table = Table(title=f"股票列表 ({len(stocks)}只)")
    table.add_column("代码", style="cyan")
    table.add_column("名称", style="yellow")
    table.add_column("现价", justify="right")
    table.add_column("市值(亿)", justify="right")
    table.add_column("行业", style="magenta")
    table.add_column("推荐", style="green")
    
    analysis_map = {a.code: a for a in (analyses or [])}
    
    for stock in stocks:
        price_str = f"{stock.price:.2f}" if stock.price else "N/A"
        value_str = f"{stock.market_value/1e8:.2f}" if stock.market_value else "N/A"
        
        analysis = analysis_map.get(stock.code)
        rec = analysis.recommendation if analysis else "N/A"
        
        table.add_row(
            stock.code,
            stock.name,
            price_str,
            value_str,
            stock.industry or "N/A",
            rec
        )
    
    console.print(table)

if __name__ == "__main__":
    cli()
