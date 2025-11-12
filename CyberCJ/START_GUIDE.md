# 🚀 CyberCJ 网站启动指南

## 快速启动

### 1. 启动服务器
```bash
cd "d:\UW\CyberCJ\Chat_bot\CyberCJ"
python app_cybercj.py
```

### 2. 访问网站
浏览器打开：http://127.0.0.1:5001

### 3. 使用CyberCJ Tutor
- 在主页顶部导航栏中点击 "CyberCJ Tutor 🤖"
- 新标签页将打开完整的聊天机器人界面
- 使用模块选择器快速创建学习计划
- 享受AI驱动的个性化学习体验！

## 功能特色

✅ **完整网站整合** - CJ-Mentor完美嵌入CyberCJ网站
✅ **独立页面体验** - 聊天机器人在新标签页中提供全屏体验
✅ **智能学习规划** - 自动生成个性化学习路径
✅ **Markdown支持** - 富文本格式显示增强学习体验
✅ **人在环反馈** - 👍👎 按钮收集用户反馈持续改进
✅ **现代化UI** - 美观的渐变设计和流畅动画效果

## 文件结构

```
CyberCJ/
├── app_cybercj.py      # Flask服务器 (端口5001)
├── index.html          # 主网站页面
├── tutor.html          # CyberCJ Tutor聊天页面
├── css/chatbot.css     # 聊天机器人样式
└── js/
    ├── chatbot.js      # 聊天机器人逻辑
    └── navBar.js       # 网站导航逻辑
```

## API端点

- `POST /chat_multi_agent` - 聊天机器人API
- `POST /feedback` - 反馈收集API
- `GET /health` - 健康检查
- `GET /api/status` - 系统状态

现在你的CyberCJ网站已经完全整合了高级的CJ-Mentor聊天机器人系统！🎉