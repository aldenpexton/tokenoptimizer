import multiprocessing
import os

# Python path configuration
pythonpath = os.path.dirname(os.path.dirname(__file__))

# Worker configuration
workers = multiprocessing.cpu_count() * 2 + 1  # Standard formula for gunicorn workers
worker_class = 'sync'
worker_connections = 1000
timeout = 60
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Performance tuning
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 30
preload_app = True  # Enable preloading for faster worker startup

# Memory optimization
worker_tmp_dir = '/dev/shm'
worker_max_requests = 1000
worker_max_requests_jitter = 50

# Limit request line and headers
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Bind configuration
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# SSL (if needed)
keyfile = None
certfile = None 