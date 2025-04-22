from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import time
import os

def load_cookies(driver, path):
    with open(path, "rb") as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)

def publish_to_zhihu(title, content):
    options = Options()
    options.set_preference("dom.webnotifications.enabled", False)
    driver = webdriver.Firefox(options=options)

    driver.get("https://www.zhihu.com")
    time.sleep(3)
    load_cookies(driver, "cookies/zhihu_cookies.pkl")

    driver.get("https://zhuanlan.zhihu.com/write")
    print("🚀 打开知乎专栏编辑页中...")

    wait = WebDriverWait(driver, 20)

    # ✅ 等待并填写标题
    title_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea")))
    title_input.send_keys(title)

    # ✅ 等待并填写正文
    # 等待并定位编辑器
    

    try:
        # 1. 点击“请输入正文”提示区域（定位它的 placeholder）
        placeholder = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), '请输入正文')]")))
        placeholder.click()
        time.sleep(1)

        # 2. 现在再查找实际的编辑区域
        editor = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ql-editor")))
        editor.click()
        time.sleep(0.5)

        # 3. 使用 execCommand 模拟真实输入
        js_script = f"""
            const text = `{content}`;
            const editor = document.querySelector("div.ql-editor");
            editor.focus();
            document.execCommand("insertText", false, text);
        """
        driver.execute_script(js_script)

        print("✅ 成功激活并注入知乎正文")

    except Exception as e:
        print("❌ 注入失败，准备截图")
        driver.save_screenshot("debug_zhihu_final.png")
        print(f"错误详情：{e}")

    
    
    # 点击一下，激活编辑器（触发 focus）
    editor.click()
    time.sleep(1)

    # 使用 JS 注入 HTML 内容
    driver.execute_script("""
        const editor = document.querySelector("div.ql-editor");
        if (editor) {
            editor.innerHTML = arguments[0];
        }
    """, content.replace("\n", "<br>"))

    print("✅ 正文已通过 JS 注入")



    # ✅ 等待并点击发布按钮
    publish_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '发布')]")))
    time.sleep(1)
    publish_button.click()

    print("✅ 已点击发布按钮，请查看知乎后台是否成功")
    time.sleep(5)
    driver.quit()

if __name__ == "__main__":
    with open("data/content.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        title = lines[0].strip()
        content = "".join(lines[1:]).strip()

    publish_to_zhihu(title, content)
