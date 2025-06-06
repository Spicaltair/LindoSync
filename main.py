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

@app.route("/")
def index():
    return "LindoSync 服务运行中"

# 触发脚本
@app.route("/run_zhihu")
def run_zhihu():
    from scripts.zhihu_playwright import publish_to_zhihu
    publish_to_zhihu()
    return "已尝试运行 zhihu 脚本"

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

def log(msg):
    with open("data/publish_log.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)


def run_platform_tasks(platforms):
    log_path = os.path.join(DATA_DIR, "publish_log.txt")
    env = os.environ.copy()
    env["PLAYWRIGHT_BROWSERS_PATH"] = "0"

    try:
        with open(log_path, "a", encoding="utf-8") as log:
            for p in platforms:
                log.write(f"🔧 正在处理平台：{p}\n")
                print(f"[INFO] ⏳ 开始处理平台：{p}")

                subprocess.run(["python", "scripts/generate_contents.py", p], check=True, capture_output=True, text=True)

                if p == "zhihu":
                    res = subprocess.run(["python", "scripts/zhihu_playwright.py"], capture_output=True, text=True, env=env)

                elif p == "xhs":
                    res = subprocess.run(["python", "scripts/xhs_playwright.py"], capture_output=True, text=True)

                log.write(f"✅ {p} 脚本输出:\n{res.stdout}\n")
                log.write(f"⚠️ {p} 脚本错误:\n{res.stderr}\n")

                print(f"[INFO] ✅ {p} 脚本输出:\n{res.stdout}")
                print(f"[INFO] ⚠️ {p} 脚本错误:\n{res.stderr}")

            log.write("[INFO] ✅ 所有发布任务完成\n")

    except subprocess.CalledProcessError as e:
        with open(log_path, "a", encoding="utf-8") as log:
            log.write(f"[ERROR] ❌ 执行失败: {e}\n")
            log.write(f"[ERROR] ⛔ 输出: {e.stdout}\n")
            log.write(f"[ERROR] 🚨 错误: {e.stderr}\n")

        print(f"[ERROR] ❌ 平台执行失败: {e}")
        print(f"[ERROR] ⛔ 输出: {e.stdout}")
        print(f"[ERROR] 🚨 错误: {e.stderr}")


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
