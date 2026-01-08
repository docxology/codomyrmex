
import os
from codomyrmex.scrape.config import ScrapeConfig

try:
    config = ScrapeConfig.from_env()
    config.validate()
    print("API Key present: YES")
except Exception as e:
    print(f"API Key present: NO ({e})")
