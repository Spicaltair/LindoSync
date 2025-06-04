#!/bin/bash

echo "✅ Running playwright install..."
playwright install --with-deps

# 然后执行主逻辑
exec gunicorn main:app

