FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app
COPY . /app

# 安装 Python 包
RUN pip install --no-cache-dir -r requirements.txt

# 安装 chromium 浏览器
RUN playwright install chromium

# 设置 Playwright 浏览器路径：0 表示当前项目目录中（非默认 cache 路径）
ENV PLAYWRIGHT_BROWSERS_PATH=0

# 清理 Render 可能的缓存路径（可选）
RUN rm -rf /opt/render/.cache/ms-playwright || true

# 启动入口
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:10000"]
