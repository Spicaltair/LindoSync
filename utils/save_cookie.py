from playwright.sync_api import sync_playwright

def save_cookie():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # ✅ 使用自带 Chromium
        context = browser.new_context()

        page = context.new_page()
        page.goto("https://www.zhihu.com")

        print("👉 请扫码登录知乎，完成后回到终端按回车继续")
        input()

        context.storage_state(path="zhihu_cookie.json")
        print("✅ Cookie 已保存")
        browser.close()

if __name__ == "__main__":
    save_cookie()
