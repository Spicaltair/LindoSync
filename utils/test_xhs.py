# utils/test_cookies_xhs.py
import os
import pickle
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.browser_manager import get_driver


# 定位到项目根目录 /data/xhs_cookies.pkl
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
cookies_path = os.path.join(DATA_DIR, "xhs_cookies.pkl")

driver = get_driver(browser_type="chrome", headless=False)
driver.get("https://creator.xiaohongshu.com/publish")

try:
    with open(cookies_path, "rb") as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)

    print("✅ Cookies 加载完毕，准备刷新页面")
    driver.refresh()

except Exception as e:
    print(f"❌ 加载 cookies 失败：{e}")
