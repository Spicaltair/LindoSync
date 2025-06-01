# LindoSync 内容输入与一键发布工具

一个简洁优雅的 Flask 项目，支持将文字 + 图片上传并一键发布到知乎、小红书。

## 技术栈

- Flask + Tailwind 前端页面
- Pillow 处理封面图像
- Playwright 自动化登录与内容发布

## 部署方式（Render 免费云）

1. 推送本项目到 GitHub
2. 登录 [Render](https://render.com/)
3. 新建 Web Service，连接本项目
4. 设置：

   - Build Command:
     ```bash
     pip install -r requirements.txt && python -m playwright install
     ```
   - Start Command:
     ```bash
     python main.py
     ```

5. 首次部署成功后访问 `https://your-app.onrender.com`

## 注意事项

- 当前版本默认使用作者本地的知乎/XHS 登录状态
- 若计划上线收费，请添加用户识别 + 登录态隔离机制

