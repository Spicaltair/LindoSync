# platforms/zhihu_auto.py
from playwright.sync_api import sync_playwright
import os

def publish(title: str, content: str):
    if not os.path.exists("zhihu_cookie.json"):
        print("❌ 缺少 cookie，请先运行 utils/save_cookie.py 登录知乎")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="zhihu_cookie.json")
        page = context.new_page()

        print("🚀 正在打开知乎专栏写作页面...")
        page.goto("https://zhuanlan.zhihu.com/write")

        page.wait_for_selector("textarea[placeholder='请输入文章标题']")
        page.fill("textarea[placeholder='请输入文章标题']", title)

        page.wait_for_selector("div.ql-editor")
        page.fill("div.ql-editor", content)

        page.wait_for_selector("button:has-text('发布')")
        page.click("button:has-text('发布')")

        print("✅ 发布成功，请在知乎后台确认文章是否已上线")
        page.wait_for_timeout(5000)
        browser.close()

if __name__ == "__main__":
    # 简单测试用法（使用 content.txt）
    with open('data/content.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        title = lines[0].strip()
        content = "".join(lines[1:]).strip()

    publish(title, content)
