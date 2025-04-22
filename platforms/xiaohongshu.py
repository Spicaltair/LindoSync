# 文件：platforms/xiaohongshu.py

import time

def publish(content: str):
    print("🚀 正在发布到小红书...")

    # 模拟一些处理时间
    time.sleep(1.5)

    # 模拟发布成功
    print("✅ 小红书发布成功！")

    # 写入日志
    with open('data/publish_log.txt', 'a', encoding='utf-8') as f:
        f.write("[小红书] 发布成功：\n")
        f.write(content + "\n")
        f.write("-" * 40 + "\n")
