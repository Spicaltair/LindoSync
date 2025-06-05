FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# 安装浏览器和系统依赖
RUN playwright install --with-deps chromium

# 显式指定 Playwright 使用当前目录的浏览器（已被上面 install 安装）
ENV PLAYWRIGHT_BROWSERS_PATH=0

RUN mkdir -p /app/data

ENTRYPOINT ["bash", "entrypoint.sh"]
