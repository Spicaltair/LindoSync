import os
import pickle
import time
from utils.browser_manager import get_driver

PLATFORMS = {
    "zhihu": "https://www.zhihu.com",
    "xiaohongshu": "https://www.xiaohongshu.com",
}

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
COOKIE_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(COOKIE_DIR, exist_ok=True)

def save_cookie_for(platform_name, url, browser_type="chrome"):
    driver = get_driver(browser_type=browser_type, headless=False)
    driver.get(url)
    print(f"👉 打开 {platform_name} 页面，请登录完成...")
    time.sleep(60)

    cookies = driver.get_cookies()
    cookie_file = os.path.join(COOKIE_DIR, f"{platform_name}_cookies.pkl")
    with open(cookie_file, "wb") as f:
        pickle.dump(cookies, f)

    print(f"✅ {platform_name} cookies 已保存到 {cookie_file}")
    driver.quit()

if __name__ == "__main__":
    for platform, url in PLATFORMS.items():
        try:
            save_cookie_for(platform, url, browser_type="chrome")
        except Exception as e:
            print(f"❌ 保存 {platform} cookies 失败：{e}")
