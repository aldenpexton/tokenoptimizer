import multiprocessing
import os

# Python path configuration
pythonpath = os.path.dirname(os.path.dirname(__file__))

# Worker configuration - reduce workers and optimize for memory
workers = 3  # Reduced from CPU-based calculation
worker_class = 'sync'
worker_connections = 1000
timeout = 120  # Increased timeout
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Performance tuning
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 30
preload_app = False  # Disable preloading to reduce memory usage

# Memory optimization
worker_tmp_dir = '/dev/shm'  # Use RAM-based temporary directory
worker_max_requests = 1000   # Restart workers periodically
worker_max_requests_jitter = 50

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