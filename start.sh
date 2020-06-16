#!/bin/sh

# start service
service rabbitmq-server start 
service mysql start 

cd /opt/nemo
# start celery
export PYTHONOPTIMIZE=1
nohup celery -A nemo.core.tasks.tasks worker --loglevel info &
nohup celery flower -A nemo.core.tasks.tasks --address=127.0.0.1 -port-5555 &
#star web
nohup python3.7 app.py &
/bin/bash

