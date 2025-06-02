FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["bash", "entrypoint.sh"]
