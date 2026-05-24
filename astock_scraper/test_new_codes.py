#!/usr/bin/env python3
import sys
sys.path.insert(0, '/workspace/astock_scraper')

import json
from web.app import get_index_kline_data, calculate_ma_from_closes

print("=== 详细测试新代码 ===")

# 测试代码和可能的前缀
test_cases = [
    ("930740", "红利低波动备选"),
    ("970070", "半导体材料设备备选"),
    ("950125", "CS人工智能备选"),
]

prefixes = ["sh", "sz", "", "szCSI", "shCSI"]

for base_code, desc in test_cases:
    print(f"\n--- {desc} ({base_code}) ---")
    for prefix in prefixes:
        code = prefix + base_code
        try:
            print(f"测试 {code}...")
            closes = get_index_kline_data(code, 60)
            if closes and len(closes) > 0:
                ma20 = calculate_ma_from_closes(closes, 20) if len(closes) >= 20 else None
                print(f"✓ 找到数据: {len(closes)} 天")
                print(f"  最新价: {closes[-1]}")
                if ma20:
                    print(f"  MA20: {ma20}")
                    print(f"  在MA20上方: {closes[-1] > ma20}")
                # 尝试获取实时价格
                import requests
                url = f"https://qt.gtimg.cn/q={code}"
                resp = requests.get(url, timeout=5)
                data_text = resp.text
                if "v_" in data_text:
                    data_text = data_text[data_text.index("v_"):]
                if "=" in data_text:
                    parts = data_text.split("=")[1].strip('"').split("~")
                    if len(parts) > 3 and parts[3]:
                        price = float(parts[3])
                        name = parts[1] if len(parts) > 1 else "N/A"
                        print(f"  实时价格: {price}")
                        print(f"  名称: {name}")
                break
        except Exception as e:
            print(f"✗ {code}: {str(e)}")
