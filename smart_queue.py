"""
Smart Queue Manager for CyberCJ - Handles 30 concurrent users intelligently
"""

import time
import threading
from collections import defaultdict, deque
from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

class SmartQueueManager:
    def __init__(self):
        # Rate limiting
        self.request_counts = defaultdict(list)
        self.ai_queue = deque()
        self.ai_processing = 0
        self.max_ai_concurrent = 3  # Maximum AI requests processing simultaneously
        
        # User session tracking
        self.active_sessions = defaultdict(dict)
        self.queue_lock = threading.Lock()
        
    def rate_limit_check(self, client_ip, max_requests=15, window=60):
        """Check if user exceeds rate limit"""
        now = time.time()
        
        # Clean old requests
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip]
            if now - req_time < window
        ]
        
        return len(self.request_counts[client_ip]) < max_requests
    
    def add_request(self, client_ip):
        """Record a new request"""
        self.request_counts[client_ip].append(time.time())
    
    def can_process_ai_request(self):
        """Check if we can process another AI request"""
        with self.queue_lock:
            return self.ai_processing < self.max_ai_concurrent
    
    def start_ai_processing(self):
        """Mark start of AI processing"""
        with self.queue_lock:
            self.ai_processing += 1
    
    def finish_ai_processing(self):
        """Mark end of AI processing"""
        with self.queue_lock:
            self.ai_processing = max(0, self.ai_processing - 1)
    
    def get_queue_status(self):
        """Get current queue status"""
        with self.queue_lock:
            return {
                'ai_processing': self.ai_processing,
                'queue_length': len(self.ai_queue),
                'estimated_wait': len(self.ai_queue) * 10  # Estimate 10s per request
            }

# Global queue manager instance
queue_manager = SmartQueueManager()

def smart_rate_limit(max_requests=15, window=60):
    """Smart rate limiting decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get client IP
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', 
                                           request.environ.get('REMOTE_ADDR', 'unknown'))
            
            # Check rate limit
            if not queue_manager.rate_limit_check(client_ip, max_requests, window):
                return jsonify({
                    'error': '请求过于频繁，请稍后再试 🕐',
                    'retry_after': window,
                    'message': '为了保证所有用户的体验，请适度使用AI聊天功能'
                }), 429
            
            # Record request
            queue_manager.add_request(client_ip)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def ai_queue_control(func):
    """AI request queue control decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if we can process immediately
        if not queue_manager.can_process_ai_request():
            status = queue_manager.get_queue_status()
            return jsonify({
                'error': 'AI系统繁忙，请稍后重试 🤖',
                'queue_status': status,
                'message': f'当前有 {status["ai_processing"]} 个用户在使用AI，预计等待时间 {status["estimated_wait"]} 秒'
            }), 503
        
        try:
            # Start processing
            queue_manager.start_ai_processing()
            result = func(*args, **kwargs)
            return result
        finally:
            # Always finish processing
            queue_manager.finish_ai_processing()
    
    return wrapper

def get_smart_response_for_busy_system():
    """Get helpful response when system is busy"""
    tips = [
        "💡 提示：您可以先浏览学习模块，稍后再尝试AI聊天",
        "📚 建议：查看课程内容和案例研究，这些不需要AI处理",
        "⏰ 小贴士：AI响应需要时间，请耐心等待不要重复点击",
        "🎯 建议：尝试提出更具体的问题，AI能给出更好的回答"
    ]
    return {
        'response': '系统当前用户较多，为保证服务质量，请稍后再试。',
        'tip': tips[int(time.time()) % len(tips)],
        'suggested_actions': [
            '浏览课程模块',
            '查看案例研究', 
            '复习知识检查',
            '稍后再试AI聊天'
        ]
    }