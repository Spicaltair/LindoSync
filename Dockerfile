FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# 没必要再 playwright install，镜像已内置所有浏览器

ENTRYPOINT ["python", "main.py"]
