# 免费方案优化配置
# 针对高并发优化的 Gunicorn 配置

import os

# Server socket  
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"

# 异步处理配置 - 提高并发能力
workers = 1
worker_class = "gevent"  # 改为异步worker
worker_connections = 2000  # 增加连接数
gevent_pool_size = 500    # 异步池大小

# 超时配置
timeout = 60              # 缩短超时，快速释放资源
keepalive = 2
graceful_timeout = 30

# 内存管理
max_requests = 500        # 更频繁重启worker
max_requests_jitter = 50
preload_app = True

# 限制资源使用
limit_request_line = 2048
limit_request_fields = 50
limit_request_field_size = 4096

# 日志
loglevel = "warning"      # 减少日志输出
accesslog = None         # 禁用访问日志节省内存
errorlog = "-"