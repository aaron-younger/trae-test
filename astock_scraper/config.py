import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/stocks.db")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

SCRAPER_CONFIGS = {
    "ths": {
        "enabled": True,
        "timeout": 10,
        "retry": 3
    },
    "tencent": {
        "enabled": True,
        "timeout": 10,
        "retry": 3
    },
    "mootdx": {
        "enabled": True,
        "timeout": 15,
        "retry": 2
    }
}

DEFAULT_SOURCE = "tencent"

CHART_COLORS = {
    "up": "#FF6B6B",
    "down": "#4ECDC4",
    "neutral": "#95A5A6",
    "background": "#1A1A2E",
    "text": "#EAEAEA"
}

CACHE_EXPIRY_MINUTES = 30
