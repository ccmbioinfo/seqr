command = 'gunicorn'
bind = '0.0.0.0:8000'
workers = 1
loglevel = 'debug'
timeout = 3600   # seconds (default is 30)
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
