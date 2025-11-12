# Gunicorn configuration file for CyberCJ on Render
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"

# Worker processes
workers = 1  # Use only 1 worker to avoid memory issues on Render free tier
worker_class = "sync"
worker_connections = 1000

# Timeouts
timeout = 120  # Increased timeout for ML model initialization
keepalive = 5
graceful_timeout = 120

# Restart workers
max_requests = 1000
max_requests_jitter = 100

# Preload app for memory efficiency
preload_app = True

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "cybercj-server"

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190