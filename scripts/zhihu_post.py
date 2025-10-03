# zhihu_post.py
import subprocess
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    try:
        # 调用半自动发布脚本
        halfauto_path = os.path.join(BASE_DIR, "zhihu_post_halfauto.py")
        print(f"[DEBUG] 调用半自动脚本: {halfauto_path}")
        subprocess.run([sys.executable, halfauto_path], check=True)
    except Exception as e:
        print(f"[ERROR] 发布知乎失败: {e}")

if __name__ == "__main__":
    main()
