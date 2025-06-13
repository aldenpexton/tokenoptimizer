import multiprocessing
import os

# Python path configuration
pythonpath = os.path.dirname(os.path.dirname(__file__))

# Worker configuration - absolute minimum for memory conservation
workers = 2  # Minimum number of workers
worker_class = 'sync'
worker_connections = 100  # Reduced connections
timeout = 30  # Reduced timeout
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Performance tuning
max_requests = 100  # Reduced to prevent memory buildup
max_requests_jitter = 10
graceful_timeout = 20
preload_app = False  # Disable preloading to reduce memory usage

# Memory optimization
worker_tmp_dir = '/dev/shm'  # Use RAM-based temporary directory
worker_max_requests = 100    # Restart workers more frequently
worker_max_requests_jitter = 10

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

# SSL
keyfile = None
certfile = None 