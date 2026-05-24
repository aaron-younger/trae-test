@app.route("/api/industry-indices", methods=["GET"])
def get_industry_indices():
    """获取行业/主题指数数据"""
    import requests
    indices = [
        {"codes": ["usNDX"], "name": "纳斯达克100"},
        {"codes": ["hkHSTECH"], "name": "恒生科技"},
        {"codes": ["sh000300"], "name": "沪深300"},
        {"codes": ["sh000905"], "name": "中证500"},
        {"codes": ["sh000852"], "name": "中证1000"},
        {"codes": ["sz399101"], "name": "中证2000"},
        {"codes": ["szH30269", "shH30269", "shH30263", "shH30271", "szH30271", "sh930740", "sz930740"], "name": "红利低波动"},
        {"codes": ["sz930713", "CSI930713", "sh930713", "sh931071", "sz931071", "shCSIAI", "sh950125", "sz950125"], "name": "CS人工智能"},
        {"codes": ["sz980017"], "name": "国证芯片"},
        {"codes": ["sz931743", "CSI931743", "sh931743", "sh970070", "sz970070"], "name": "半导体材料设备"}
    ]
    
    result = []
    for index_info in indices:
        current_price = None
        yesterday_close = None
        change_pct = None
        closes = []
        used_code = None
        data_source = None
        
        for code in index_info["codes"]:
            try:
                url = f"https://qt.gtimg.cn/q={code}"
                response = requests.get(url, timeout=5)
                data_text = response.text
                
                if "v_" in data_text:
                    data_text = data_text[data_text.index("v_"):]
                
                parts = data_text.split("=")[1].strip('"').split("~")
                
                if len(parts) > 4 and parts[3]:
                    current_price = float(parts[3]) if parts[3] else None
                    yesterday_close = float(parts[4]) if parts[4] else None
                    if current_price and yesterday_close and yesterday_close != 0:
                        change_pct = round((current_price - yesterday_close) / yesterday_close * 100, 2)
                    used_code = code
                    data_source = "realtime"
                
                closes = get_index_kline_data(code, 60)
                
                if closes and len(closes) > 0:
                    if not used_code:
                        used_code = code
                        data_source = "kline"
                
                if current_price or (closes and len(closes) > 0):
                    break
            except Exception as e:
                print(f"尝试获取{index_info['name']} ({code})失败: {e}")
                continue
        
        ma20 = calculate_ma_from_closes(closes, 20)
        
        if ma20 is None and closes and len(closes) >= 1:
            available_days = min(20, len(closes))
            ma20 = round(sum(closes[-available_days:]) / available_days, 2)
        
        if closes and len(closes) > 0 and current_price is None:
            current_price = closes[-1]
            if not used_code:
                used_code = index_info["codes"][0]
                data_source = "kline_last"
        
        above_ma20 = current_price > ma20 if (current_price is not None and ma20 is not None) else None
        
        result.append({
            "code": used_code if used_code else index_info["codes"][0],
            "name": index_info["name"],
            "price": current_price,
            "change": change_pct,
            "ma20": ma20,
            "above_ma20": above_ma20,
            "available": current_price is not None or ma20 is not None,
            "data_source": data_source
        })
    
    return jsonify({
        "success": True,
        "data": result,
        "source": "腾讯财经"
    })
