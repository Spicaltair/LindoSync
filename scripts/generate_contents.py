import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# DeepSeek API Key 和 Endpoint
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 项目目录
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

def load_origin():
    origin_path = os.path.join(DATA_DIR, "origin.txt")
    if not os.path.exists(origin_path):
        raise FileNotFoundError("❌ 未找到 origin.txt")
    with open(origin_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines:
        raise ValueError("❌ origin.txt 内容为空")
    title = lines[0].strip()
    content = "".join(lines[1:]).strip()
    return title, content

def call_deepseek(prompt):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",  # 可以改成你的具体模型名称
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f"❌ DeepSeek API 调用失败: {response.status_code}, {response.text}")
    data = response.json()
    return data["choices"][0]["message"]["content"]

def save_content(platform, title, content):
    path = os.path.join(DATA_DIR, f"content_{platform}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(title + "\n\n" + content)
    print(f"✅ 已生成 {platform} 稿件：{path}")

def generate_for_platform(platform, base_content, style_instruction):
    prompt = f"""
你是一个专业内容编辑。请基于以下原文，按照"{platform}"平台的文风改写内容：
要求：{style_instruction}

原文：
{base_content}
"""
    styled_content = call_deepseek(prompt)
    return styled_content

if __name__ == "__main__":
    print("🚀 开始处理 origin.txt 内容...")
    title, content = load_origin()

    # 平台风格定义
    platforms = {
        "zhihu": "保持正式、逻辑严谨、自然换行、适当总结、结尾鼓励点赞收藏",
        "xhs": "轻松口语化、多用短句、自然空行、增加emoji符号、适合小红书口吻"
    }

    for platform, instruction in platforms.items():
        styled_content = generate_for_platform(platform, content, instruction)
        save_content(platform, title, styled_content)

    print("🎉 全部平台内容生成完成！")
