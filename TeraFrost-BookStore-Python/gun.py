import os 
import gevent.monkey
gevent.monkey.patch_all()

import multiprocessing

#debug = True
#loglevel = 'debug'

bind = "127.0.0.1:5000"
#pidfile = 'log/gunicorn.pid'
#logfile = 'log/debug.log'
workers = multiprocessing.cpu_count()*2+1
#workers = 4
worker_class = 'gevent'
threads = 10
preload_app = True
reload = True
x_forwarder_for_header = 'X-FORWARDED-FOR'
accesslog = 'log.txt'