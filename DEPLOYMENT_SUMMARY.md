# 🚀 CyberCJ Backend 部署到 Render 总结

## ✅ 已完成的配置

1. **Procfile** - 配置为使用 `server.py`
2. **requirements.txt** - 已添加 `gunicorn` 依赖
3. **server.py** - 已配置动态端口支持 Render
4. **.gitignore** - 防止上传敏感文件和大文件
5. **API URLs** - 前端聊天机器人已配置为使用相对路径

## 🎯 您的 server.py 包含的功能

- ✅ 完整的 CyberCJ 网站
- ✅ 多智能体聊天系统
- ✅ 调查问卷系统
- ✅ 反馈收集系统
- ✅ 健康检查端点

## 📋 部署步骤

### 1. 推送到 GitHub
```bash
git init
git add .
git commit -m "CyberCJ backend ready for Render deployment"
git branch -M main
git remote add origin https://github.com/yourusername/cybercj-backend.git
git push -u origin main
```

### 2. 在 Render 上创建服务
1. 去 https://render.com
2. 点击 "New +" → "Web Service"
3. 连接您的 GitHub 仓库
4. 配置：
   - **Name**: cybercj-backend
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn server:app --bind 0.0.0.0:$PORT`

### 3. 设置环境变量
在 Render 的环境变量设置中添加：
- `GROQ_API_KEY` = 您的 Groq API 密钥

### 4. 部署完成后
您的网站将在以下地址可用：
- **主网站**: `https://your-service-name.onrender.com/`
- **聊天界面**: `https://your-service-name.onrender.com/multi_agent_chat.html`

## 💡 关于前端的选择

**选项 A (推荐)**: 直接使用 Render 上的完整网站
- 优点: 一站式解决方案，无需额外配置
- 地址: 直接使用 Render 提供的 URL

**选项 B**: 继续使用 Netlify 前端 + Render 后端
- 如果选择这个，运行: `python update_api_urls.py https://your-render-url.onrender.com`
- 然后重新部署到 Netlify

## 🔧 有用的工具

- `python check_deployment.py` - 检查部署准备状态
- `python update_api_urls.py <render-url>` - 更新前端 API 地址

## ⚠️ 注意事项

1. 首次部署时 FAISS 索引会重新构建，可能需要几分钟
2. 确保在 Render 上设置了 `GROQ_API_KEY` 环境变量
3. Render 免费计划在不活跃时会休眠，首次访问可能较慢