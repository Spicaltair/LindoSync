import os
import time
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def save_cookie(name: str, url: str, file: str):
    print(f"🌐 打开 {url} 页面，请登录完成...")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(url)

    time.sleep(30)  # 手动登录

    os.makedirs("data", exist_ok=True)
    cookies = driver.get_cookies()

    with open(file, "wb") as f:
        pickle.dump(cookies, f)

    print(f"✅ {name} cookies 已保存到 {file}")
    print("📋 cookies 中的 domain 字段如下：")
    for c in cookies:
        print(f"  - {c.get('domain')}")

    driver.quit()

if __name__ == "__main__":
    #save_cookie("知乎", "https://www.zhihu.com", "data/zhihu_cookies.pkl")
    save_cookie("小红书", "https://creator.xiaohongshu.com", "data/xhs_cookies.pkl")
