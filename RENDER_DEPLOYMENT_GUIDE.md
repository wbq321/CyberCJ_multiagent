# Render Deployment Guide for CyberCJ Backend

## 后端服务说明

您的后端服务使用：
- **文件**: `server.py`
- **功能**: 完整的 CyberCJ 网站 + 多智能体聊天 + 调查系统
- **端点**: `/`, `/multi_agent_chat.html`, `/chat_multi_agent`, `/feedback`, `/submit_survey`

这是一个一体化的解决方案，包含了前端和后端功能。

## Prerequisites
1. GitHub repository with your backend code
2. Render account (render.com)
3. GROQ API key

## Files Required for Render Deployment

### 1. Procfile
```
web: gunicorn server:app --bind 0.0.0.0:$PORT
```

### 2. requirements.txt
Already updated with gunicorn dependency

### 3. Environment Variables
Set these in Render dashboard:
- GROQ_API_KEY=your_groq_api_key_here

## Deployment Steps

### Step 1: Push Code to GitHub
```bash
git init
git add .
git commit -m "Initial commit for Render deployment"
git branch -M main
git remote add origin https://github.com/yourusername/cybercj-backend.git
git push -u origin main
```

### Step 2: Create New Web Service on Render
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: cybercj-backend (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: main
   - **Root Directory**: Leave empty
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn server:app --bind 0.0.0.0:$PORT`

### Step 3: Environment Variables
In Render service settings → Environment:
- Key: `GROQ_API_KEY`
- Value: Your actual Groq API key

### Step 4: Deploy
Click "Create Web Service" and wait for deployment

## Important Notes

1. **Complete Solution**: `server.py` 包含前端和后端，部署后即可直接使用
2. **Port Configuration**: Render automatically assigns PORT environment variable
3. **CORS**: Already configured to allow all origins
4. **Vector Store**: The FAISS index will be rebuilt on first run

## 部署后的使用方式

### 选项 1: 直接使用 Render 上的完整网站 (推荐)
部署后，您可以直接使用 Render 上的网站：
- **主网站**: `https://your-service-name.onrender.com/`
- **多智能体聊天**: `https://your-service-name.onrender.com/multi_agent_chat.html`
- **健康检查**: `https://your-service-name.onrender.com/health`

### 选项 2: 保持 Netlify 前端，连接 Render 后端
如果您想继续使用 Netlify 上的前端，需要更新前端的 API 调用：

运行更新脚本：
```bash
python update_api_urls.py https://your-service-name.onrender.com
```

这会将前端代码中的 `localhost` 地址替换为您的 Render URL。

## Testing
Your backend will be available at: `https://your-service-name.onrender.com`

Test endpoints:
- Main website: `GET https://your-service-name.onrender.com/`
- Health check: `GET https://your-service-name.onrender.com/health`
- Multi-agent chat: `POST https://your-service-name.onrender.com/chat_multi_agent`
- Survey submission: `POST https://your-service-name.onrender.com/submit_survey`