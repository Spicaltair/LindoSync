import os
import sys
import openai
from dotenv import load_dotenv

load_dotenv()

# 设置 API 基础信息
API_MODE = os.getenv("API_MODE", "deepseek")  # "deepseek" or "openai"
API_KEY = os.getenv("API_KEY")

# 根据不同平台设置 API参数
if API_MODE.lower() == "deepseek":
    openai.api_key = API_KEY
    openai.api_base = "https://api.deepseek.com/v1"
    MODEL_NAME = "deepseek-chat"
    print("🚀 当前使用 DeepSeek API")
elif API_MODE.lower() == "openai":
    openai.api_key = API_KEY
    MODEL_NAME = "gpt-3.5-turbo"
    print("🚀 当前使用 OpenAI API")
else:
    raise ValueError(f"❌ 未知 API_MODE: {API_MODE}")

# 基本路径设置
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def load_origin():
    origin_path = os.path.join(DATA_DIR, "origin.txt")
    if not os.path.exists(origin_path):
        raise FileNotFoundError("❌ 没有找到 origin.txt，请先在网页输入内容保存！")
    
    with open(origin_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    title = lines[0].strip()
    content = "".join(lines[1:]).strip()
    return title, content

def style_content(title, content, platform="zhihu"):
    if platform == "zhihu":
        prompt = f"将以下内容优化成适合知乎专栏发布的风格，注意分段自然、正式有条理，不要加表情符号：\n\n标题：{title}\n\n内容：{content}"
    elif platform == "xhs":
        prompt = f"将以下内容优化成适合小红书发布的风格，语言轻松，分段短小，可适当加入表情符号，吸引读者注意力：\n\n标题：{title}\n\n内容：{content}"
    else:
        raise ValueError(f"未知平台：{platform}")

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
        print(f"❌ 调用API失败：{e}")
        sys.exit(1)

def save_styled_content(platform, styled_text):
    target_file = os.path.join(DATA_DIR, f"content_{platform}.txt")
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(styled_text.strip())
    print(f"✅ 已生成 {target_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法示例：python generate_contents.py zhihu")
        print("或：python generate_contents.py xhs")
        sys.exit(1)

    platform = sys.argv[1]

    title, content = load_origin()
    styled_text = style_content(title, content, platform=platform)
    save_styled_content(platform, styled_text)
