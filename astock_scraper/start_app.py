#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web.app import app

if __name__ == "__main__":
    print("启动A股数据采集分析系统...")
    print("服务将在 http://localhost:5000 运行")
    app.run(debug=False, host="0.0.0.0", port=5000)