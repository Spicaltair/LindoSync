# 文件：platforms/zhihu.py
import time
import os

def publish(content: str):
    print("🚀 正在发布到知乎...")

    time.sleep(1.2)  # 模拟网络延迟

    print("✅ 知乎发布成功！")

    log_path = 'data/publish_log.txt'
    os.makedirs('data', exist_ok=True)
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write("[知乎] 发布成功：\n")
        f.write(content.strip() + "\n")
        f.write("-" * 40 + "\n")
