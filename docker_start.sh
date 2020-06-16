#!/bin/sh

# service
service rabbitmq-server start 
service mysql start 

# start celery and flower
export PYTHONOPTIMIZE=1
cd /opt/nemo
nohup celery -A nemo.core.tasks.tasks worker --loglevel info &
nohup celery flower -A nemo.core.tasks.tasks --address=127.0.0.1 -port-5555 &

# star web
nohup python3.7 app.py &

# keep running...
/bin/bash
