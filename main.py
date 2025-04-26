# LindoSync 极简美学版内容输入器（Flask+Tailwind）

from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# 自动定位 data 目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        print(f"收到标题：{title}")
        print(f"收到正文：{content}")

        if title and content:
            file_path = os.path.join(DATA_DIR, "origin.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"{title}\n\n{content}")
            print(f"✅ 已保存到 {file_path}")
            return redirect(url_for("success"))
        else:
            print("⚠️ 表单未填写完整，未保存")
    return render_template("index.html")

@app.route("/success")
def success():
    return render_template("success.html")

if __name__ == "__main__":
    app.run(debug=True)
