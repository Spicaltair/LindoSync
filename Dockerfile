FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

# 设置工作目录
WORKDIR /app
COPY . /app

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Playwright 浏览器（关键）
RUN playwright install --with-deps

# 清理可能的缓存路径避免 Render 残留导致识别失败
RUN rm -rf /root/.cache/ms-playwright /opt/render/.cache/ms-playwright || true

# 显式指定浏览器路径（让 Playwright 确保能找到）
ENV PLAYWRIGHT_BROWSERS_PATH=0

# 目录
RUN mkdir -p /app/data

# 启动命令
ENTRYPOINT ["bash", "entrypoint.sh"]
