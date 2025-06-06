FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# 安装 Chromium，并携带依赖（这个命令等于 --with-deps）
RUN playwright install chromium

# 确保运行时从正确路径加载浏览器
ENV PLAYWRIGHT_BROWSERS_PATH=0

CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:10000"]
