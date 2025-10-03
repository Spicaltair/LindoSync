import os
import sys
import subprocess
import webbrowser

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CLIP_HELPER = os.path.join(BASE_DIR, "scripts", "clipboard_helper.py")

def main():
    # 打开小红书创作发布页面
    print("[INFO] 打开小红书创作平台...")
    url = "https://creator.xiaohongshu.com/publish/publish?source=official"
    webbrowser.open(url)

    # 调用 clipboard_helper.py，传递平台参数
    print("[INFO] 调用 Clipboard Helper (平台=xhs)...")
    subprocess.Popen([sys.executable, CLIP_HELPER, "xhs"])

if __name__ == "__main__":
    main()
