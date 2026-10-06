import os
import multiprocessing

port = os.getenv("PORT", "8001")
bind = f"0.0.0.0:{port}"
workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Log to stdout/stderr on Render or containerized environments
if os.getenv("RENDER"):
    accesslog = "-"
    errorlog = "-"
else:
    accesslog = "logs/gunicorn_access.log"
    errorlog = "logs/gunicorn_error.log"

loglevel = "info"

