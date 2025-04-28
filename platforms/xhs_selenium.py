import os
import time
import sys
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 确保可以 import 上级目录下的 utils
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.browser_manager import get_driver

driver = get_driver(browser_type="chrome", headless=False)

# 获取当前项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def load_cookies(driver, path):
    with open(path, "rb") as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)

def publish_to_xhs(title, content):
    options = Options()
    options.set_preference("dom.webnotifications.enabled", False)

    driver = webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install()),
        options=options
    )

    driver.get("https://www.xiaohongshu.com")  # 小红书首页
    time.sleep(3)

    # 加载登录cookies
    try:
        load_cookies(driver, os.path.join(DATA_DIR, "xhs_cookies.pkl"))
        print("✅ 成功加载小红书cookies")
        driver.refresh()
        time.sleep(3)
    except Exception as e:
        print(f"⚠️ 加载cookies失败，请先手动保存 xhs_cookies.pkl：{e}")
        driver.quit()
        return

    # 跳转到创作中心（小红书网页版要求）
    driver.get("https://creator.xiaohongshu.com/publish")
    print("🚀 打开小红书发布页面...")
    time.sleep(5)

    wait = WebDriverWait(driver, 20)

    try:
        # 输入标题
        title_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder='请输入标题']")))
        title_input.send_keys(title)
        print("✅ 填写标题完成")

        # 输入正文
        content_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[placeholder='这一刻你想分享什么...']")))
        content_input.send_keys(content)
        print("✅ 填写正文完成")

        # TODO：添加封面上传（后续）
        # TODO：选择分类（后续）

        time.sleep(1)

        # 点击发布按钮
        publish_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'发布')]")))
        driver.execute_script("arguments[0].click();", publish_button)
        print("✅ 已点击发布按钮")

        time.sleep(5)

        current_url = driver.current_url
        if "/note/" in current_url:
            print(f"🎉 发布成功！笔记链接：{current_url}")
        else:
            print("⚠️ 发布后页面未跳转到笔记，可能需要人工检查")

    except Exception as e:
        print(f"❌ 发布流程出错：{e}")
        driver.save_screenshot("debug_publish_xhs_fail.png")

    driver.quit()

if __name__ == "__main__":
    with open(os.path.join(DATA_DIR, "content_xhs.txt"), "r", encoding="utf-8") as f:
        lines = f.readlines()
        title = lines[0].strip()
        content = "".join(lines[1:]).strip()

    publish_to_xhs(title, content)
