# scripts/generate_contents.py
# 说明：
# - 从 data/origin.txt 读取标题&正文（第1行=标题，之后全部=正文）
# - 生成平台文案到 data/content_{platform}.txt、data/title_{platform}.txt
# - 对封面/音频/视频：若提供了上传路径 => 复制并重命名到 data/
#                 若未提供 => 自动生成“占位文件”，统一放到 data/ 下
#   占位规则：
#     - 封面：cover_{platform}.jpg（白底+文字）
#     - 音频：audio_{platform}.wav（1秒静音 wav）
#     - 视频：video_{platform}.mp4（空壳占位文件，提醒后续替换）

import os
import shutil
import argparse
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import wave
import struct

# ---------- 可选：接 DeepSeek 生成 ----------
import openai
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()
API_KEY = os.getenv("API_KEY")
openai.api_key = API_KEY
openai.api_base = "https://api.deepseek.com/v1"
MODEL_NAME = "deepseek-chat"

# 路径：scripts/ 在下面，data 在项目根目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)


def load_origin():
    origin_path = os.path.join(DATA_DIR, "origin.txt")
    if not os.path.exists(origin_path):
        raise FileNotFoundError("origin.txt 不存在，请先在 GUI 上传原始文本（或手工创建 data/origin.txt）")

    with open(origin_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        raise ValueError("origin.txt 为空")

    title = lines[0].strip()
    content = "".join(lines[1:]).strip()
    return title, content


def style_content(title, content, platform):
    """依平台风格生成文案（DeepSeek）。若你暂时不想调 API，可直接 return content。"""
    if not API_KEY:
        # 无 key，直接返回原文，避免中断
        return f"{title}\n\n{content}"

    if platform == "zhihu":
        prompt = f"将以下内容优化成适合知乎专栏发布的风格，注意分段自然、正式有条理，不要加表情符号，第一行只写标题：\n\n标题：{title}\n\n内容：{content}"
    elif platform == "xhs":
        prompt = f"将以下内容优化成适合小红书发布的风格，语言轻松、分段短小，可少量表情，标题≤20字、正文≤1000字。第一行只写标题：\n\n标题：{title}\n\n内容：{content}"
    else:
        raise ValueError(f"未知平台：{platform}")

    try:
        resp = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个擅长内容优化的AI助手。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        return resp["choices"][0]["message"]["content"]
    except Exception as e:
        print("[WARN] 生成失败，回退到原文：", e)
        return f"{title}\n\n{content}"


# ----------------- 媒体占位/复制工具 -----------------

def _copy_with_target(src_path, target_path):
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    shutil.copyfile(src_path, target_path)
    return target_path


def _safe_ext(path, default_ext):
    """如果 path 存在，用其后缀；否则用默认后缀"""
    if path and os.path.exists(path):
        return os.path.splitext(path)[1] or default_ext
    return default_ext


def _placeholder_cover(target_path, platform):
    """生成占位封面：白底 1200x675，写上平台字样"""
    w, h = 1200, 675
    img = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    text = f"cover_{platform}"
    # 尝试系统字体，找不到就用默认
    try:
        font = ImageFont.truetype("arial.ttf", 48)
    except:
        font = ImageFont.load_default()
    tw, th = draw.textsize(text, font=font)
    draw.text(((w - tw) / 2, (h - th) / 2), text, fill=(0, 0, 0), font=font)
    img.save(target_path, "JPEG")


def _placeholder_audio_wav(target_path, duration_sec=1, sample_rate=44100):
    """生成1秒静音 WAV 占位。"""
    n_frames = int(duration_sec * sample_rate)
    with wave.open(target_path, "w") as wf:
        wf.setnchannels(1)        # mono
        wf.setsampwidth(2)        # 16-bit
        wf.setframerate(sample_rate)
        silence = (0).to_bytes(2, byteorder="little", signed=True)
        for _ in range(n_frames):
            wf.writeframesraw(silence)


def _placeholder_video_mp4(target_path):
    """
    生成一个极小的“占位”mp4文件（非有效视频，仅占位方便管道继续）。
    真要自动化视频占位，建议后续集成 ffmpeg 再做。
    """
    with open(target_path, "wb") as f:
        f.write(b"")  # 占位空文件
    # 同时写一个说明
    note = target_path + ".READ_ME.txt"
    with open(note, "w", encoding="utf-8") as nf:
        nf.write("这是一个视频占位文件（空）。如需真实视频，请在 GUI 上传或后续用 ffmpeg 生成。")


def ensure_media(platform, kind, uploaded_path):
    """
    统一入口：
      kind ∈ {'cover', 'audio', 'video'}
      uploaded_path：GUI 上传路径（可能为 None）
    逻辑：
      - 有上传：复制并重命名到 data/ 统一名
      - 无上传：生成占位文件到 data/
    返回：目标文件绝对路径
    """
    assert kind in {"cover", "audio", "video"}

    if kind == "cover":
        ext = _safe_ext(uploaded_path, ".jpg")
        target = os.path.join(DATA_DIR, f"cover_{platform}{ext}")
        if uploaded_path and os.path.exists(uploaded_path):
            _copy_with_target(uploaded_path, target)
        else:
            # 生成占位封面（jpg）
            if not target.lower().endswith(".jpg"):
                target = os.path.join(DATA_DIR, f"cover_{platform}.jpg")
            _placeholder_cover(target, platform)
        return target

    if kind == "audio":
        ext = _safe_ext(uploaded_path, ".wav")  # 没上传时用 .wav（纯Python可生成）
        target = os.path.join(DATA_DIR, f"audio_{platform}{ext}")
        if uploaded_path and os.path.exists(uploaded_path):
            _copy_with_target(uploaded_path, target)
        else:
            # 生成 1s 静音 wav
            if not target.lower().endswith(".wav"):
                target = os.path.join(DATA_DIR, f"audio_{platform}.wav")
            _placeholder_audio_wav(target)
        return target

    if kind == "video":
        ext = _safe_ext(uploaded_path, ".mp4")
        target = os.path.join(DATA_DIR, f"video_{platform}{ext}")
        if uploaded_path and os.path.exists(uploaded_path):
            _copy_with_target(uploaded_path, target)
        else:
            # 生成空壳占位 mp4 + 说明文件
            if not target.lower().endswith(".mp4"):
                target = os.path.join(DATA_DIR, f"video_{platform}.mp4")
            _placeholder_video_mp4(target)
        return target


def save_texts(platform, styled_text, title):
    # content_{platform}.txt
    content_file = os.path.join(DATA_DIR, f"content_{platform}.txt")
    with open(content_file, "w", encoding="utf-8") as f:
        f.write(styled_text.strip())

    # title_{platform}.txt
    title_file = os.path.join(DATA_DIR, f"title_{platform}.txt")
    with open(title_file, "w", encoding="utf-8") as f:
        f.write(title.strip())

    print(f"[INFO] 文案已生成: {title_file}, {content_file}")
    return title_file, content_file


def main():
    parser = argparse.ArgumentParser(description="Generate styled content + media copies")
    parser.add_argument("platform", choices=["zhihu", "xhs"], help="目标平台")
    parser.add_argument("--cover", help="封面图片上传路径（可选）", default=None)
    parser.add_argument("--audio", help="音频上传路径（可选）", default=None)
    parser.add_argument("--video", help="视频上传路径（可选）", default=None)
    args = parser.parse_args()

    platform = args.platform.lower()
    print(f" Generating content for {platform}...")

    # 1) 读 origin
    title, content = load_origin()

    # 2) 平台风格生成
    styled = style_content(title, content, platform=platform)

    # 3) 存文本
    save_texts(platform, styled, title)

    # 4) 处理媒体：复制/改名；若无上传，生成占位
    cover_path = ensure_media(platform, "cover", args.cover)
    audio_path = ensure_media(platform, "audio", args.audio)
    video_path = ensure_media(platform, "video", args.video)

    print(f"[INFO] 媒体定位：\n  封面: {cover_path}\n  音频: {audio_path}\n  视频: {video_path}")
    print(" Done.")


if __name__ == "__main__":
    main()
