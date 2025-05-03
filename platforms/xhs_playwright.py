# xhs_playwright.py

from playwright.sync_api import sync_playwright
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CONTENT_PATH = os.path.join(DATA_DIR, "content_xhs.txt")
COVER_PATH = os.path.join(DATA_DIR, "cover.png")
STATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "auth", "xhs_state.json")


def publish_to_xhs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        if not os.path.exists(STATE_PATH):
            print("❌ 未找到登录状态，请先运行 xhs_login.py 登录并保存")
            return

        context = browser.new_context(storage_state=STATE_PATH)
        page = context.new_page()

        print("🚀 打开小红书创作平台...")
        page.goto("https://creator.xiaohongshu.com/publish")

        print("🖱️ 点击“发布笔记”按钮...")
        page.wait_for_selector("a.btn:has-text('发布笔记')", timeout=10000)
        page.click("a.btn:has-text('发布笔记')")
        page.wait_for_timeout(2000)

        print("🖱️ 切换到图文发布 tab...")
        page.click("text=上传图文")
        page.wait_for_timeout(2000)

        print("🖼️ 上传封面图 cover.jpg...")
        if os.path.exists(COVER_PATH):
            page.set_input_files("input.upload-input", COVER_PATH)
            print("✅ 封面图上传完成")
        else:
            print("⚠️ 未找到 cover.jpg，跳过上传")
            return

        page.wait_for_timeout(3000)

        with open(CONTENT_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            title = lines[0].strip()
            content = "".join(lines[1:]).strip()

        print("⌛ 等待图文编辑器加载...")
        page.wait_for_selector("input.d-text[placeholder*='标题']", timeout=15000)

        print("📝 自动填写标题与正文...")
        page.fill("input.d-text[placeholder*='标题']", title)
        page.focus("div.ql-editor[contenteditable='true']")
        page.keyboard.type(content)

        print("🚀 尝试点击发布按钮...")
        try:
            page.locator("div.d-button-content >> span:has-text('发布')").click()
            print("✅ 已点击发布按钮")
        except Exception as e:
            print("❌ 点击发布按钮失败")
            print(f"错误详情：{e}")
            page.screenshot(path="debug_publish_fail.png")

        page.wait_for_timeout(10000)
        browser.close()


if __name__ == "__main__":
    publish_to_xhs()
