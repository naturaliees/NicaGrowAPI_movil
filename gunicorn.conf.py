import os
bind = '0.0.0.0:' + os.getenv('PORT', '8000')
workers = int(os.getenv('WEB_CONCURRENCY', '2'))
worker_class = 'sync'
timeout = 90
accesslog = '-'
errorlog = '-'
capture_output = True
# Trust forwarded headers only from the App Service proxy inside this instance.
forwarded_allow_ips = '127.0.0.1,::1'
