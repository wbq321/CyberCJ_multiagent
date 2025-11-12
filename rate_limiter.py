# 请求队列和速率限制
# 添加到 server.py 来处理高并发

from collections import defaultdict
import time
from functools import wraps

# 简单的速率限制
request_counts = defaultdict(list)
MAX_REQUESTS_PER_MINUTE = 10  # 每分钟最多10个AI请求

def rate_limit(max_requests=10, window=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取客户端IP
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', 
                                           request.environ.get('REMOTE_ADDR', 'unknown'))
            
            now = time.time()
            
            # 清理过期记录
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip]
                if now - req_time < window
            ]
            
            # 检查速率限制
            if len(request_counts[client_ip]) >= max_requests:
                return jsonify({
                    'error': '请求过于频繁，请稍后再试',
                    'retry_after': window
                }), 429
            
            # 记录当前请求
            request_counts[client_ip].append(now)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 使用示例:
# @rate_limit(max_requests=5, window=60)  # 每分钟最多5个请求
# @app.route('/chat_multi_agent', methods=['POST'])
# def chat_multi_agent():
#     ...