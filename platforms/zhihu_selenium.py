import os
import time
import pickle
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 获取当前项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def load_cookies(driver, path):
    with open(path, "rb") as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)

def try_select_topic(driver, wait, keyword="副业") -> bool:
    print(f"🧠 输入关键词：{keyword}")
    allow_publish = False

    try:
        # 点击“添加话题”按钮
        add_topic_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), '添加话题')]")))
        driver.execute_script("arguments[0].click();", add_topic_button)
        time.sleep(1)

        # 找到搜索框，输入关键词
        topic_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='搜索话题...']")))
        driver.execute_script("arguments[0].focus();", topic_input)
        topic_input.clear()
        topic_input.send_keys(keyword)
        print("⌨️ 已输入关键词")
        time.sleep(4)  # 给足时间等待联想项渲染

        # 精确查找知乎“官方话题”项：li 带 data-value
        topic_items = driver.find_elements(By.XPATH, "//li[contains(@class, 'AutoComplete-item') and @data-value]")
        print(f"📋 共检测到 {len(topic_items)} 个候选话题项")

        for i, item in enumerate(topic_items):
            text = item.text.strip()
            data_id = item.get_attribute("data-value")
            print(f"  [{i+1}] {text} ｜ data-id={data_id}")
            if keyword in text and data_id:
                driver.execute_script("arguments[0].click();", item)
                print(f"✅ 成功点击知乎官方话题：{text}")
                time.sleep(1)
                allow_publish = True
                break

        if not allow_publish:
            print("❌ 没有找到官方话题项，跳过发布")
            driver.save_screenshot("debug_topic_not_found.png")

    except Exception as e:
        print("❌ 话题选择过程出错")
        driver.save_screenshot("debug_topic_exception.png")
        print(f"错误详情：{e}")

    return allow_publish

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

    # 输入标题
    title_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea")))
    title_input.send_keys(title)

    # 注入正文
    try:
        editor = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "public-DraftEditor-content")))
        safe_content = content.replace("\n", "\n\n")
        js_script = """
            const editor = document.querySelector(".public-DraftEditor-content");
            editor.focus();
            const selection = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(editor);
            range.collapse(true);
            selection.removeAllRanges();
            selection.addRange(range);
            document.execCommand("insertText", false, arguments[0]);
        """
        driver.execute_script(js_script, safe_content)
        print("✅ 成功注入知乎正文内容")
    except Exception as e:
        print("❌ 正文注入失败")
        driver.save_screenshot("debug_editor_fail.png")
        return

    # 尝试选择话题
    allow_publish = try_select_topic(driver, wait, keyword="副业")

    if allow_publish:
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
                driver.save_screenshot("debug_publish.png")

        except Exception as e:
            print("❌ 发布操作失败")
            driver.save_screenshot("debug_publish_fail.png")
            print(f"错误详情：{e}")
    else:
        print("🛑 未成功添加话题，跳过发布操作")

    driver.quit()

if __name__ == "__main__":
    with open("data/content.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        title = lines[0].strip()
        content = "".join(lines[1:]).strip()

    publish_to_zhihu(title, content)
