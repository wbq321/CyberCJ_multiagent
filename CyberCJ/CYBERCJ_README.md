# CyberCJ Website with CJ-Mentor Integration

## 概述

这是一个完全整合了 CJ-Mentor 高级聊天机器人系统的 CyberCJ 网站。该系统将原本的独立聊天机器人升级为支持战略学习规划、脚手架教学、人在环反馈系统的智能教育助手。

## 功能特性

### 🚀 CJ-Mentor 聊天机器人
- **战略学习规划**: 自动生成个性化4-6步学习计划
- **脚手架教学**: 基于学习理论的渐进式教学方法
- **智能对话**: 理解用户意图，提供针对性回答
- **Markdown支持**: 支持**粗体**、*斜体*、`代码`、列表等富文本格式
- **模块选择器**: 快速选择特定网络安全模块进行学习
- **新话题功能**: 一键开始新的学习话题

### 📊 人在环反馈系统
- **实时反馈收集**: 👍👎 按钮收集用户反馈
- **数据持久化**: JSONL格式存储反馈数据
- **质量改进**: 通过用户反馈持续优化系统性能

### 🎨 增强UI设计
- **现代化界面**: 渐变色彩和动画效果
- **响应式设计**: 适配不同屏幕尺寸
- **流畅交互**: 平滑的打开/关闭动画
- **统一主题**: 与CyberCJ网站风格保持一致

## 文件结构

```
CyberCJ/
├── app_cybercj.py          # 主Flask服务器
├── index.html              # 网站主页（已整合聊天机器人）
├── css/
│   └── chatbot.css         # 升级版聊天机器人样式
├── js/
│   ├── chatbot.js          # CJ-Mentor聊天机器人功能
│   └── navBar.js           # 网站导航功能
├── images/                 # 网站图像资源
├── computer-security/      # 计算机安全模块
├── internet-security/      # 网络安全模块
├── privacy/                # 隐私模块
└── introduction/           # 入门模块
```

## 安装和运行

### 1. 环境要求
- Python 3.8+
- Flask
- Flask-CORS
- LangChain
- Groq API密钥

### 2. 安装依赖
```bash
cd "d:\UW\CyberCJ\Chat_bot\CyberCJ"
pip install flask flask-cors langchain-community langchain-groq faiss-cpu
```

### 3. 配置API密钥
确保在父目录的 `.env` 文件中设置了Groq API密钥：
```bash
GROQ_API_KEY=your_groq_api_key_here
```

### 4. 启动服务器
```bash
python app_cybercj.py
```

### 5. 访问网站
打开浏览器访问：http://127.0.0.1:5001

## API端点

### 聊天机器人
- **POST** `/chat_multi_agent`
  - 发送消息给CJ-Mentor
  - 请求格式: `{"message": "用户消息", "conversation_id": "会话ID"}`
  - 响应格式: `{"response": "AI回复", "system_message": "系统消息(可选)"}`

### 反馈系统
- **POST** `/feedback`
  - 提交用户反馈
  - 请求格式: `{"message_id": "消息ID", "rating": "positive/negative", ...}`

### 状态检查
- **GET** `/health` - 服务器健康检查
- **GET** `/api/status` - API状态信息

## 使用指南

### 1. 打开聊天机器人
- 点击右下角的"🤖 CJ-Mentor"按钮
- 聊天窗口将滑入显示

### 2. 选择学习模块
- 使用下拉菜单选择特定模块
- 系统将自动生成该模块的学习计划

### 3. 开始新话题
- 点击"New Topic"按钮开始新的学习话题
- 系统将清空当前对话并重新开始

### 4. 提供反馈
- 在AI回复上悬停显示👍👎按钮
- 点击按钮提供反馈帮助改进系统

## 技术架构

### 前端技术
- **HTML5**: 语义化网页结构
- **CSS3**: 现代化样式和动画效果
- **JavaScript ES6+**: 异步通信和交互逻辑
- **Bootstrap 5**: 响应式布局框架

### 后端技术
- **Flask**: Python Web框架
- **LangChain**: LLM应用开发框架
- **Groq API**: 高性能LLM推理
- **FAISS**: 向量数据库用于RAG检索

### 智能特性
- **RAG检索**: 基于knowledge.txt的上下文检索
- **对话管理**: 多轮对话状态维护
- **学习规划**: THINK-PLAN-ACT循环策略规划
- **反馈循环**: 人在环质量改进机制

## 数据存储

### 反馈数据
- 位置: `../feedback_data/cybercj_feedback.jsonl`
- 格式: 每行一个JSON对象
- 字段: timestamp, message_id, rating, response_text等

### 知识库
- 位置: `../knowledge.txt`
- 格式: 纯文本网络安全教程内容
- 用途: RAG检索增强生成

## 开发说明

### 自定义修改
1. **样式调整**: 修改 `css/chatbot.css`
2. **功能扩展**: 修改 `js/chatbot.js`
3. **后端逻辑**: 修改 `app_cybercj.py`
4. **AI行为**: 修改 `../multi_agent_tutor.py`

### 调试模式
- Flask运行在debug模式，代码修改自动重载
- 浏览器开发者工具查看网络请求和错误
- 服务器控制台查看后端日志

## 故障排除

### 常见问题
1. **端口冲突**: 确保5001端口未被占用
2. **API密钥**: 检查GROQ_API_KEY环境变量
3. **CORS错误**: 确保Flask-CORS正确安装
4. **模块导入**: 确保multi_agent_tutor.py在正确路径

### 性能优化
- 使用CDN加速静态资源加载
- 实施消息缓存减少API调用
- 优化向量数据库查询速度

## 更新历史

### v1.0.0 - 完整整合版
- ✅ 将CJ-Mentor完全整合到CyberCJ网站
- ✅ 实现模块选择器和新话题功能
- ✅ 添加人在环反馈系统
- ✅ 支持Markdown富文本显示
- ✅ 现代化UI设计和交互动画

---

**作者**: GitHub Copilot
**版本**: 1.0.0
**最后更新**: 2025年11月6日