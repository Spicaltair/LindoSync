# zhihu_playwright.py

from playwright.sync_api import sync_playwright
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CONTENT_PATH = os.path.join(DATA_DIR, "content_zhihu.txt")
STATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "auth", "zhihu_state.json")
# 替换旧的 COVER_PATH
# COVER_PATH = os.path.join(DATA_DIR, "cover.jpg")

# 改为动态读取
cover_path_file = os.path.join(DATA_DIR, "cover_path.txt")
COVER_PATH = None

if os.path.exists(cover_path_file):
    with open(cover_path_file, "r", encoding="utf-8") as f:
        COVER_PATH = f.read().strip()



def publish_to_zhihu():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        if not os.path.exists(STATE_PATH):
            print(" 未找到登录状态，请先运行 zhihu_login.py 登录并保存")
            return

        context = browser.new_context(storage_state=STATE_PATH)
        page = context.new_page()

        print("open zhihu publish page...")
        page.goto("https://zhuanlan.zhihu.com/write")
        page.wait_for_timeout(3000)

        print("fill in title ")
        with open(CONTENT_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            title = lines[0].strip()
            content = "".join(lines[1:]).strip()

        page.fill("textarea[placeholder*='标题']", title)

        if os.path.exists(COVER_PATH):
            print("upload cover")
            try:
                page.set_input_files("input[type='file']", COVER_PATH)
                page.wait_for_timeout(2000)
            except Exception as e:
                print("upload cover failed", e)
        else:
            print(" cannot find cover.jpg，skip uploading")

        print("waiting for editor")
        editor = page.locator("div.public-DraftEditor-content")
        # 检查是否有引导弹窗或遮罩
        if page.locator("div.Modal-backdrop").is_visible():
            print("[INFO] Detected modal backdrop, trying to close it...")
            try:
                page.locator("button:has-text('知道了')").click(timeout=3000)
                page.wait_for_timeout(1000)
            except:
                print("[WARN] Modal detected but no known close button found.")

        editor.click()
        page.keyboard.type(content[:1000])
        page.wait_for_timeout(1000)
        print("Text has been filled")

        try:
            print(" Try to add default topics")
            page.click("button:has-text('添加话题')")
            page.fill("input[placeholder*='搜索话题']", "AI")
            page.wait_for_timeout(2000)

            ai_button = page.locator("button", has_text="AI").first
            if ai_button.is_visible():
                ai_button.click()
                print("wait for topic to be chosen...")
                page.wait_for_timeout(2000)
                selected_topics = page.locator("div.css-1gguqv1")
                if selected_topics.locator("text=AI").count() > 0:
                    print(" topic has been added: AI")
                else:
                    print(" topic has been chosen")
            else:
                print(" Not found AI button of topic")
        except Exception as e:
            print(" Fail to add topic : ", e)

        print(" Try to click on the button... ")
        try:
            publish_btn = page.locator("button.Button--primary", has_text="发布").last
            publish_btn.click()
            page.wait_for_timeout(5000)

            if "/p/" in page.url:
                print("Successful link:" + page.url)
            else:
                print(" Page still in draft editting, may not be published")
                page.screenshot(path="debug_zhihu_publish_fail.png")
        except Exception as e:
            print(" Fail to publish:", e)
            page.screenshot(path="debug_zhihu_publish_fail.png")

        browser.close()

if __name__ == "__main__":
    publish_to_zhihu()
