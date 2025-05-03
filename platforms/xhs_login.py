from playwright.sync_api import sync_playwright

def save_login_state():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://creator.xiaohongshu.com")

        print("👉 请手动登录小红书创作平台...")
        input("✅ 登录完成后按 Enter 键继续...")

        # 这一行非常关键！！！
        context.storage_state(path="auth/xhs_state.json")
        print("✅ 登录状态已保存到 auth/xhs_state.json")

        browser.close()

if __name__ == "__main__":
    save_login_state()
