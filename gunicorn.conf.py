import os
bind=os.getenv("GUNICORN_BIND","127.0.0.1:8000")
workers=int(os.getenv("GUNICORN_WORKERS","4"))
worker_class=os.getenv("GUNICORN_WORKER_CLASS","gthread")
threads=int(os.getenv("GUNICORN_THREADS","2"))
timeout=int(os.getenv("GUNICORN_TIMEOUT","60"));graceful_timeout=30;keepalive=5
max_requests=int(os.getenv("GUNICORN_MAX_REQUESTS","2000"));max_requests_jitter=200
accesslog="-";errorlog="-";capture_output=True
