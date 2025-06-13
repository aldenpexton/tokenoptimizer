import multiprocessing
import os

# Python path configuration
pythonpath = os.path.dirname(os.path.dirname(__file__))

# Worker configuration
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 60
keepalive = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Performance tuning
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 30
preload_app = True

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