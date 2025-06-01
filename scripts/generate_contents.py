# generate_contents.py (DeepSeek 专用版)

import os
import sys
from dotenv import load_dotenv
import openai

load_dotenv()

# DeepSeek API 设置
API_KEY = os.getenv("API_KEY")
openai.api_key = API_KEY
openai.api_base = "https://api.deepseek.com/v1"
MODEL_NAME = "deepseek-chat"
print(" DeepSeek API activated.")

# 基本路径设置
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_origin():
    origin_path = os.path.join(DATA_DIR, "origin.txt")
    if not os.path.exists(origin_path):
        raise FileNotFoundError("    origin.txt not found. Please input content on the web interface first.")

    with open(origin_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    title = lines[0].strip()
    content = "".join(lines[1:]).strip()
    return title, content


def style_content(title, content, platform="zhihu"):
    if platform == "zhihu":
        prompt = f"将以下内容优化成适合知乎专栏发布的风格，注意分段自然、正式有条理，不要加表情符号,第一行就写标题本身，不写其他内容：\n\n标题：{title}\n\n内容：{content}"
    elif platform == "xhs":
        prompt = f"将以下内容优化成适合小红书发布的风格，语言轻松，分段短小，可适当加入表情符号，吸引读者注意力,整个标题不要超过20个字符,全文不超过1000个字符：\n\n标题：{title}\n\n内容：{content}"
    else:
        raise ValueError(f"Unknown platform: {platform}")

    try:
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个擅长内容优化的AI助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print("    API call failed:")
        print(e)
        sys.exit(1)


def save_styled_content(platform, styled_text):
    target_file = os.path.join(DATA_DIR, f"content_{platform}.txt")
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(styled_text.strip())
    print(f" Saved to {target_file}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("[USAGE] Example: python generate_contents.py zhihu or python generate_contents.py xhs")
        sys.exit(1)

    platform = sys.argv[1].lower()
    print(f" Generating content for {platform}...")
    try:
        title, content = load_origin()
        styled_text = style_content(title, content, platform=platform)
        save_styled_content(platform, styled_text)
    except Exception as e:
        print(f"    Failed to generate content for {platform}:")
        print(e)
