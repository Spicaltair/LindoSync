# zhihu_login.py

from playwright.sync_api import sync_playwright
import os

STATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "auth", "zhihu_state.json")

def save_login_state():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("🌐 打开知乎首页，请手动扫码登录...")
        page.goto("https://www.zhihu.com")
        page.wait_for_timeout(20000)  # 登录完成后等待 20 秒

        os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
        context.storage_state(path=STATE_PATH)

        print(f"✅ 登录状态已保存到 {STATE_PATH}")
        browser.close()

if __name__ == "__main__":
    save_login_state()
