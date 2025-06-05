from flask import Flask, render_template, request, redirect, url_for
import os
import subprocess
from PIL import Image
from shutil import copyfile
from threading import Thread


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)


def process_image(input_path, output_path, size=(1280, 720), quality=85):
    with Image.open(input_path) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail(size)
        img.save(output_path, format="JPEG", quality=quality)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        cover = request.files.get("cover")

        if title and content:
            with open(os.path.join(DATA_DIR, "origin.txt"), "w", encoding="utf-8") as f:
                f.write(f"{title}\n\n{content}")

        if cover and cover.filename:
            ext = os.path.splitext(cover.filename)[1].lower()
            if ext in [".jpg", ".jpeg", ".png", ".webp"]:
                # 清理旧封面图
                for fname in os.listdir(DATA_DIR):
                    if fname.startswith("cover.") and os.path.splitext(fname)[1].lower() in [".jpg", ".jpeg", ".png", ".webp"]:
                        os.remove(os.path.join(DATA_DIR, fname))
                # 保存原图
                raw_path = os.path.join(DATA_DIR, f"cover{ext}")
                cover.save(raw_path)

                # 确保 static 目录存在
                static_dir = os.path.join(BASE_DIR, "static")
                os.makedirs(static_dir, exist_ok=True)

                # 统一保存处理后的封面图
                final_path = os.path.join(static_dir, "cover.jpg")
                try:
                    process_image(raw_path, final_path)
                except Exception as e:
                    print(f"[ERROR] 图片处理失败: {e}")
                    return "⚠️ 上传的图片无法处理，请上传 JPG/PNG 格式图像", 400


                # 写入 cover_path.txt
                with open(os.path.join(DATA_DIR, "cover_path.txt"), "w", encoding="utf-8") as f:
                    f.write(final_path)


        return redirect(url_for("preview"))

    return render_template("index.html")


@app.route("/preview")
def preview():
    title, content, cover_url = "", "", None

    origin_path = os.path.join(DATA_DIR, "origin.txt")
    if os.path.exists(origin_path):
        with open(origin_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            title = lines[0].strip() if lines else ""
            content = "".join(lines[2:]).strip() if len(lines) > 2 else ""

    cover_path_file = os.path.join(DATA_DIR, "cover_path.txt")
    if os.path.exists(cover_path_file):
        real_path = open(cover_path_file).read().strip()
        if os.path.exists(real_path):
            rel_path = os.path.relpath(real_path, BASE_DIR)
            #cover_url = "/" + rel_path.replace("\\", "/")
            cover_url = url_for("static", filename="cover.jpg")


    return render_template("preview.html", title=title, content=content, cover_url=cover_url)


def run_platform_tasks(platforms):
    log_path = os.path.join(DATA_DIR, "publish_log.txt")
    with open(log_path, "w", encoding="utf-8") as log:
        for platform in platforms:
            log.write(f"\n📌 正在处理平台：{platform}\n")
            log.flush()
            try:
                subprocess.run(
                    ["python", "scripts/generate_contents.py", platform],
                    check=True, capture_output=True, text=True
                )
                subprocess.run(
                    ["python", f"scripts/{platform}_playwright.py"],
                    check=True, capture_output=True, text=True
                )
                log.write(f"✅ {platform} 发布成功！\n")
            except subprocess.CalledProcessError as e:
                log.write(f"❌ {platform} 发布失败！\n")
                log.write(f"命令：{e.cmd}\n")
                log.write(f"输出：{e.stdout}\n")
                log.write(f"错误：{e.stderr}\n")
            log.flush()



@app.route("/publish_all", methods=["POST"])
def publish_all():
    platforms = request.form.getlist("platforms")
    Thread(target=run_platform_tasks, args=(platforms,)).start()
    return redirect(url_for("success"))



@app.route("/success")
def success():
    log_path = os.path.join("data", "publish_log.txt")
    log_content = ""

    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            log_content = f.read()

    return render_template("success.html", log=log_content)


if __name__ == "__main__":
    app.run(debug=True)
