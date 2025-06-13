import multiprocessing
import os

# Python path configuration
pythonpath = os.path.dirname(os.path.dirname(__file__))

# Worker configuration optimized for memory constraints (512MB limit)
workers = 2  # Fixed number of workers for memory optimization
worker_class = 'gthread'  # Thread-based workers for better memory sharing
threads = 4  # Number of threads per worker
worker_connections = 1000
timeout = 30  # Reduced timeout
keepalive = 2  # Reduced keepalive

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Performance tuning
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 20
preload_app = False  # Disable preloading to save memory

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