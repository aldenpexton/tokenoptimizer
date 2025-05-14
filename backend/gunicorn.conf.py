import os
import multiprocessing

# Gunicorn settings
bind = f"{os.getenv('HOST', '0.0.0.0')}:{os.getenv('PORT', '5000')}"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
timeout = 120
worker_class = "gthread"
accesslog = "-"
errorlog = "-"

# Import app from the correct module
wsgi_app = "backend.app:create_app()" 