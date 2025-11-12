# 🚀 CyberCJ 部署到 Render - 操作清单

## ✅ 已完成
- [x] Git 仓库初始化完成
- [x] 所有文件已提交到本地仓库
- [x] Procfile 配置 (使用 server.py)
- [x] requirements.txt 包含 gunicorn
- [x] server.py 支持动态端口
- [x] API 路径已配置为相对路径

## 📋 接下来需要您执行的操作

### 1. 创建 GitHub 仓库并推送代码

```bash
# 在 GitHub 上创建新仓库后，执行以下命令：
git branch -M main
git remote add origin https://github.com/yourusername/cybercj-backend.git
git push -u origin main
```

> **注意**: 将 `yourusername/cybercj-backend` 替换为您实际的 GitHub 用户名和仓库名

### 2. 在 Render 上创建 Web Service

1. 访问 https://render.com
2. 登录后点击 "New +" → "Web Service"
3. 连接您刚创建的 GitHub 仓库
4. 配置服务：
   - **Name**: cybercj-backend (或您喜欢的名字)
   - **Region**: 选择离您用户最近的区域
   - **Branch**: main
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn server:app --bind 0.0.0.0:$PORT`

### 3. 设置环境变量

在 Render 服务设置页面，Environment 部分：
- **Key**: `GROQ_API_KEY`
- **Value**: 您的 Groq API 密钥

### 4. 部署并测试

1. 点击 "Create Web Service" 开始部署
2. 等待部署完成（初次部署可能需要几分钟）
3. 部署成功后，访问您的网站：
   - 主网站: `https://your-service-name.onrender.com/`
   - 聊天系统: `https://your-service-name.onrender.com/multi_agent_chat.html`

## 🎉 部署完成后

您将拥有一个完整的 CyberCJ 网站，包括：
- ✅ 完整的学习模块 (Introduction, Computer Security, Internet Security, Privacy)
- ✅ CyberCJ Challenges 场景练习
- ✅ AI 多智能体聊天系统
- ✅ 调查问卷系统
- ✅ 反馈收集系统

## 💡 关于 Netlify

由于您的 `server.py` 已经包含了完整的前端服务，您可以：
- **停用 Netlify 上的项目** (节省资源)
- 直接使用 Render 提供的完整解决方案

## ❓ 需要帮助？

如果遇到问题，检查：
1. Render 部署日志中是否有错误
2. 环境变量 `GROQ_API_KEY` 是否正确设置
3. GitHub 仓库是否包含所有必要文件

---
**下一步**: 创建 GitHub 仓库并推送代码 → 在 Render 创建服务 → 设置 API 密钥 → 完成！