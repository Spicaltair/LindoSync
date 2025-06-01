from playwright.sync_api import sync_playwright
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CONTENT_PATH = os.path.join(DATA_DIR, "content_xhs.txt")
STATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "auth", "xhs_state.json")
COVER_PATH = None

# 读取封面路径
cover_path_file = os.path.join(DATA_DIR, "cover_path.txt")
if os.path.exists(cover_path_file):
    with open(cover_path_file, "r", encoding="utf-8") as f:
        COVER_PATH = f.read().strip()


def publish_to_xhs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        if not os.path.exists(STATE_PATH):
            print("[ERROR] Login state not found. Please run xhs_login.py first.")
            return

        context = browser.new_context(storage_state=STATE_PATH)
        page = context.new_page()

        print("[INFO] Opening Xiaohongshu creation platform...")
        page.goto("https://creator.xiaohongshu.com/publish")
        page.wait_for_timeout(3000)

        print("[INFO] Clicking 'Publish Note' button...")
 
        try:
            page.wait_for_selector("span:has-text('发布笔记')", timeout=10000)
            page.click("span:has-text('发布笔记')")
            print("[INFO] 点击成功：发布笔记")
        except Exception as e:
            print("[ERROR] 点击“发布笔记”失败:", e)
            page.screenshot(path="xhs_publish_note_fail.png")
            return


        print("[INFO] Switching to image-text publishing tab...")
        try:
            tab = page.locator("span.title:has-text('上传图文')").first
            tab.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            tab.evaluate("el => el.click()")  # 强制点击
            print("[INFO] 成功点击“上传图文”")
        except Exception as e:
            print("[ERROR] 点击“上传图文”失败:", e)
            page.screenshot(path="xhs_tab_fail.png")
            return

        page.wait_for_timeout(2000)

        print("[INFO] Uploading cover image...")
        if COVER_PATH and os.path.exists(COVER_PATH):
            try:
                page.set_input_files("input.upload-input", COVER_PATH)
                print("[INFO] Cover image uploaded")
            except Exception as e:
                print("[ERROR] 上传封面失败:", e)
                page.screenshot(path="xhs_cover_upload_fail.png")
                return
        else:
            print("[WARN] Cover image not found or path invalid.")
            return

        page.wait_for_timeout(3000)

        with open(CONTENT_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            title = lines[0].strip()
            content = "".join(lines[1:]).strip()

        print("[INFO] Waiting for editor to load...")
        page.wait_for_selector("input.d-text[placeholder*='标题']", timeout=15000)

        print("[INFO] Filling in title and content...")
        page.fill("input.d-text[placeholder*='标题']", title)
        page.focus("div.ql-editor[contenteditable='true']")
        page.keyboard.type(content)
        page.wait_for_timeout(2000)

        # 点击一个话题（可选）
        try:
            hashtag = page.locator("span:has-text('#')").first
            if hashtag.is_visible():
                hashtag.click()
                print("[INFO] Clicked first suggested hashtag.")
                page.wait_for_timeout(1000)
        except Exception as e:
            print("[WARN] No hashtag clicked:", e)

        print("[INFO] Attempting to click publish button...")
        try:
            page.locator("div.d-button-content >> span:has-text('发布')").click()
            print("[INFO] Publish button clicked")
        except Exception as e:
            print("[ERROR] Failed to click publish button:", e)
            page.screenshot(path="xhs_publish_button_fail.png")

        page.wait_for_timeout(8000)
        browser.close()


if __name__ == "__main__":
    publish_to_xhs()
