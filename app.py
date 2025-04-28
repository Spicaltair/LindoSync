# LindoSync 极简美学版内容输入器（Flask+Tailwind）+ 内容风格化+发布按钮

from flask import Flask, render_template, request, redirect, url_for
import os
import subprocess

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if title and content:
            with open(os.path.join(DATA_DIR, "origin.txt"), "w", encoding="utf-8") as f:
                f.write(title + "\n\n" + content.replace("（空一行）", "").replace("(空一行)", ""))
            return redirect(url_for("success"))
    return render_template("index.html")

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/generate_zhihu", methods=["POST"])
def generate_zhihu():
    try:
        subprocess.run(["python", "scripts/generate_contents.py", "zhihu"], check=True)
        return redirect(url_for("home"))
    except Exception as e:
        return f"❌ 生成知乎版失败：{e}"

@app.route("/generate_xhs", methods=["POST"])
def generate_xhs():
    try:
        subprocess.run(["python", "scripts/generate_contents.py", "xhs"], check=True)
        return redirect(url_for("home"))
    except Exception as e:
        return f"❌ 生成小红书版失败：{e}"

@app.route("/publish_zhihu", methods=["POST"])
def publish_zhihu():
    try:
        subprocess.run(["python", "platforms/zhihu_selenium.py"], check=True)
        return redirect(url_for("home"))
    except Exception as e:
        return f"❌ 发布知乎失败：{e}"

if __name__ == "__main__":
    app.run(debug=True)