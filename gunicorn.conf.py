# Gunicorn配置文件

import multiprocessing
import os

# 绑定地址和端口（与 Nginx upstream 保持一致）
bind = "127.0.0.1:8081"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = "sync"

# 线程数
threads = 2

# 进程名称
proc_name = 'ohsteack'

# 设置守护进程
daemon = False

# 工作目录
chdir = os.path.dirname(os.path.abspath(__file__))

# 环境变量
raw_env = [
    'FLASK_ENV=production',
]

# 日志配置
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
loglevel = 'info'

# 访问日志格式
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 超时设置
timeout = 120
graceful_timeout = 30

# 最大请求数
max_requests = 1000
max_requests_jitter = 50

# 预加载应用
preload_app = True

# StatsD 监控（可选）
# statsd_host = 'localhost:8125'
# statsd_prefix = 'ohsteack'
