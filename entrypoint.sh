#!/bin/bash
set -e

echo "✅ 确保 Playwright 浏览器已安装..."
playwright install --with-deps

echo "🚀 启动 Gunicorn 服务..."
exec gunicorn main:app --bind 0.0.0.0:${PORT:-10000}


