from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import pickle
import os

def save_cookie():
    options = Options()
    options.set_preference("dom.webnotifications.enabled", False)

    # 启动系统 Firefox 浏览器
    driver = webdriver.Firefox(options=options)
    driver.get("https://www.zhihu.com")

    print("👉 请扫码登录知乎，登录完成后等待 20 秒...")
    time.sleep(20)

    # 创建 cookie 文件夹
    os.makedirs("cookies", exist_ok=True)
    with open("cookies/zhihu_cookies.pkl", "wb") as f:
        pickle.dump(driver.get_cookies(), f)

    print("✅ Cookie 已保存到 cookies/zhihu_cookies.pkl")
    driver.quit()

if __name__ == "__main__":
    save_cookie()
