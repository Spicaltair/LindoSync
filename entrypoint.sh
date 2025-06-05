#!/bin/bash
# 预启动动作

echo "🔧 Running playwright install to ensure browsers are ready..."
playwright install --with-deps || true

echo "🚀 Starting the app..."
exec "$@"
