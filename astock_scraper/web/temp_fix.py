        ma20 = calculate_ma_from_closes(closes, 20)
        
        # 只有当有足够的历史K线数据（至少20天）时才计算MA20
        # 否则标记为None，表示数据不足无法准确判断趋势
        if ma20 is None and closes and len(closes) >= 20:
            ma20 = round(sum(closes[-20:]) / 20, 2)
        
        if closes and len(closes) > 0 and current_price is None:
            current_price = closes[-1]
            if not used_code:
                used_code = index_info["codes"][0]
                data_source = "kline_last"
        
        # 只有当有足够的K线数据（至少20天）且MA20有效时才能判断是否在MA20上方
        above_ma20 = current_price > ma20 if (current_price is not None and ma20 is not None and len(closes) >= 20) else None
        
        # 判断是否可用：需要有实时价格或有足够历史数据的MA20
        available = (current_price is not None and len(closes) >= 20) or (ma20 is not None and len(closes) >= 20)
        
        result.append({
            "code": used_code if used_code else index_info["codes"][0],
            "name": index_info["name"],
            "price": current_price,
            "change": change_pct,
            "ma20": ma20,
            "above_ma20": above_ma20,
            "available": available,
            "data_source": data_source,
            "kline_days": len(closes) if closes else 0  # 添加调试信息
        })
