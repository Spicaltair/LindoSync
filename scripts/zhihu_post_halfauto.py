import os
import sys
import subprocess
import webbrowser

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CLIP_HELPER = os.path.join(BASE_DIR, "scripts", "clipboard_helper.py")

def main():
    # 打开知乎写文章页面
    print("[INFO] 打开知乎创作平台...")
    url = "https://zhuanlan.zhihu.com/write"
    webbrowser.open(url)

    # 调用 clipboard_helper.py，传递平台参数
    print("[INFO] 调用 Clipboard Helper (平台=zhihu)...")
    subprocess.Popen([sys.executable, CLIP_HELPER, "zhihu"])

if __name__ == "__main__":
    main()
