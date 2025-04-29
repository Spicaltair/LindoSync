import os
import sys
import time
import pickle
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ⭕ 修正路径，保证上级目录模块可用
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# ⭕ 导入自定义模块
from utils.browser_manager import get_driver

# ⭕ 其他正常逻辑

driver = get_driver(browser_type="chrome", headless=False)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def load_cookies(driver, path):
    with open(path, "rb") as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)


def upload_cover_image(driver, wait):
    try:
        file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
        cover_path = os.path.join(BASE_DIR, "data", "cover.jpg")
        if os.path.exists(cover_path):
            file_input.send_keys(os.path.abspath(cover_path))
            print("✅ 已上传封面图片")
            time.sleep(3)
        else:
            print("⚠️ 未找到封面图 cover.jpg，跳过上传")
    except Exception as e:
        print("⚠️ 上传封面图失败，跳过")
        print(f"错误详情：{e}")


def input_title(driver, wait, title):
    title_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea")))
    title_input.send_keys(title)
    print("✅ 已输入标题")


def input_content(driver, wait, content):
    editor = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "public-DraftEditor-content")))
    editor.click()
    for line in content.splitlines():
        editor.send_keys(line)
        editor.send_keys(Keys.SHIFT, Keys.ENTER)
        time.sleep(0.1)
    print("✅ 已输入正文内容")


def try_select_topic(driver, wait, keyword="副业"):
    print(f"🧠 输入关键词：{keyword}")
    try:
        add_topic_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), '添加话题')]")))
        driver.execute_script("arguments[0].click();", add_topic_button)
        time.sleep(1)

        topic_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='搜索话题...']")))
        topic_input.clear()
        topic_input.send_keys(keyword)
        time.sleep(5)

        dropdown_items = driver.find_elements(By.CSS_SELECTOR, "ul[class*='AutoComplete'] li")
        if dropdown_items:
            driver.execute_script("arguments[0].click();", dropdown_items[0])
            print(f"✅ 成功点击下拉项：{dropdown_items[0].text}")
            time.sleep(2)
            page = driver.page_source
            if keyword in page:
                print("✅ 页面确认话题添加成功")
                return True
        else:
            print("❌ 下拉列表为空，尝试键盘盲选")
            topic_input.send_keys(Keys.ARROW_DOWN)
            topic_input.send_keys(Keys.ENTER)
            time.sleep(2)
            page = driver.page_source
            if keyword in page:
                print("✅ 盲选后页面确认话题添加成功")
                return True

    except Exception as e:
        print("❌ 话题添加失败")
        print(f"错误详情：{e}")

    return False


def publish_article(driver, wait):
    try:
        publish_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., '发布')]")))
        driver.execute_script("arguments[0].click();", publish_button)
        print("✅ 已点击发布按钮")
        time.sleep(5)
        current_url = driver.current_url
        if "/p/" in current_url and not current_url.endswith("/edit"):
            print(f"🎉 发布成功！文章链接：{current_url}")
        else:
            print("⚠️ 页面跳转仍为草稿编辑页，可能未真正发布")
    except Exception as e:
        print("❌ 发布操作失败")
        print(f"错误详情：{e}")


def publish_to_zhihu(title, content):
    options = Options()
    options.set_preference("dom.webnotifications.enabled", False)

    driver = webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install()),
        options=options
    )

    driver.get("https://www.zhihu.com")
    time.sleep(3)
    load_cookies(driver, os.path.join(BASE_DIR, "cookies", "zhihu_cookies.pkl"))

    driver.get("https://zhuanlan.zhihu.com/write")
    print("🚀 打开知乎专栏编辑页中...")
    wait = WebDriverWait(driver, 20)

    input_title(driver, wait, title)
    upload_cover_image(driver, wait)
    input_content(driver, wait, content)

    allow_publish = try_select_topic(driver, wait, keyword="副业")

    if allow_publish:
        publish_article(driver, wait)
    else:
        print("🛑 未成功添加话题，跳过发布操作，已保存草稿。")
        driver.save_screenshot("debug_topic_not_added.png")
        print("👉 请人工登录知乎后台，进入草稿列表，选择该草稿补充话题后手动发布。")

    driver.quit()


if __name__ == "__main__":
    with open("data/content_zhihu.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        title = lines[0].strip()
        content = "".join(lines[1:]).strip()

    publish_to_zhihu(title, content)
