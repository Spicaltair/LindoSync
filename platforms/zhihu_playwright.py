# zhihu_playwright.py

from playwright.sync_api import sync_playwright
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CONTENT_PATH = os.path.join(DATA_DIR, "content_zhihu.txt")
STATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "auth", "zhihu_state.json")
COVER_PATH = os.path.join(DATA_DIR, "cover.jpg")


def publish_to_zhihu():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        if not os.path.exists(STATE_PATH):
            print("❌ 未找到登录状态，请先运行 zhihu_login.py 登录并保存")
            return

        context = browser.new_context(storage_state=STATE_PATH)
        page = context.new_page()

        print("🚀 打开知乎专栏发布页面...")
        page.goto("https://zhuanlan.zhihu.com/write")
        page.wait_for_timeout(3000)

        # 填写标题
        print("📝 填写标题...")
        with open(CONTENT_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            title = lines[0].strip()
            content = "".join(lines[1:]).strip()

        page.fill("textarea[placeholder*='标题']", title)

        # 上传封面（可选）
        if os.path.exists(COVER_PATH):
            print("🖼 上传封面图...")
            try:
                page.set_input_files("input[type='file']", COVER_PATH)
                page.wait_for_timeout(2000)
            except Exception as e:
                print("⚠️ 封面上传失败：", e)
        else:
            print("⚠️ 未找到封面图 cover.jpg，跳过上传")

        # 填写正文
        print("⌛ 等待正文编辑器加载...")
        editor = page.locator("div.public-DraftEditor-content")
        editor.click()
        page.keyboard.type(content[:1000])  # 避免太长引发卡顿
        page.wait_for_timeout(1000)
        print("✅ 正文内容已注入")

        # 添加话题（简化版）
        try:
            print("🔍 尝试添加默认话题（如 AI）...")
            page.click("button:has-text('添加话题')")
            page.fill("input[placeholder*='搜索话题']", "AI")
            page.wait_for_timeout(1500)
            dropdown = page.locator("ul li").first
            dropdown.click()
            print("✅ 话题添加成功")
        except Exception as e:
            print("⚠️ 添加话题失败，可手动补充", e)

        # 点击发布按钮
        print("🚀 尝试点击发布按钮...")
        try:
            # 使用更精确定位，避免匹配到“发布设置”
            publish_btn = page.locator("button.Button--primary", has_text="发布").last
            publish_btn.click()
            page.wait_for_timeout(5000)

            if "/p/" in page.url:
                print(f"🎉 发布成功！文章链接：{page.url}")
            else:
                print("⚠️ 页面跳转仍为草稿编辑页，可能未真正发布")
                page.screenshot(path="debug_zhihu_publish_fail.png")
        except Exception as e:
            print("❌ 发布失败：", e)
            page.screenshot(path="debug_zhihu_publish_fail.png")

        browser.close()


if __name__ == "__main__":
    publish_to_zhihu()
