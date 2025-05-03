import os
import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 配置路径
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
COOKIES_PATH = os.path.join(DATA_DIR, "xhs_cookies.pkl")

def load_cookies(driver, path):
    with open(path, "rb") as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            if "sameSite" in cookie and cookie["sameSite"] == "None":
                cookie["sameSite"] = "Strict"
            try:
                driver.add_cookie(cookie)
            except Exception:
                pass

def publish_to_xiaohongshu(title, content):
    # 初始化浏览器
    options = Options()
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    # 打开首页加载 Cookie
    driver.get("https://www.xiaohongshu.com")
    time.sleep(3)

    if not os.path.exists(COOKIES_PATH):
        print("❌ 缺少 cookies，请先运行 save_cookies.py 登录并保存！")
        driver.quit()
        return

    load_cookies(driver, COOKIES_PATH)
    print("✅ Cookies 加载完毕，准备刷新页面")
    driver.refresh()
    time.sleep(3)

    # 进入创作中心
    driver.get("https://creator.xiaohongshu.com/publish")
    print("🚀 打开小红书发布页面...")
    time.sleep(5)

    try:
        # 等待标题输入框
        title_input = wait.until(EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='请输入标题']")))
        title_input.clear()
        title_input.send_keys(title)
        print("✅ 已输入标题")

        # 正文输入框
        content_input = wait.until(EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='这一刻你想分享什么...']")))
        content_input.clear()
        content_input.send_keys(content)
        print("✅ 已输入正文")

        time.sleep(10)  # 暂时人工检查，未来可加自动上传图和点击发布
    except Exception as e:
        print("❌ 发布流程出错")
        print(f"📋 错误详情：{type(e).__name__}: {e}")
        screenshot_path = os.path.join(DATA_DIR, "debug_xhs_publish_error.png")
        driver.save_screenshot(screenshot_path)
        print(f"📸 已截图保存至：{screenshot_path}")


    driver.quit()

if __name__ == "__main__":
    with open(os.path.join(DATA_DIR, "content_xhs.txt"), "r", encoding="utf-8") as f:
        lines = f.readlines()
        title = lines[0].strip()
        content = "".join(lines[1:]).strip()

    publish_to_xiaohongshu(title, content)
