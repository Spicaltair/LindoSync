from platforms import wechat, xiaohongshu, zhihu, bilibili
from utils import logger

def load_content():
    with open('data/content.txt', 'r', encoding='utf-8') as f:
        return f.read()

def main():
    print("🎯 欢迎使用 LindoSync 原型工具")
    print("请选择发布平台：")
    print("1. 微信公众号\n2. 小红书\n3. 知乎\n4. B站")
    choice = input("请输入编号（支持多选，用逗号分隔）：")
    platforms = choice.split(',')

    content = load_content()
    for p in platforms:
        p = p.strip()
        if p == '1':
            wechat.publish(content)
        elif p == '2':
            xiaohongshu.publish("这是测试内容")
        elif p == '3':
            zhihu.publish(content)
        elif p == '4':
            bilibili.publish(content)

if __name__ == "__main__":
    main()
