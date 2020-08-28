#!/bin/sh

# service
service rabbitmq-server start 
service mysql start 

# start celery and flower
export PYTHONOPTIMIZE=1
cd /opt/nemo
nohup python3.7 -m celery -A nemo.core.tasks.tasks worker --loglevel info -c 4 &
nohup python3.7 -m celery flower -A nemo.core.tasks.tasks --basic_auth=nemo:nemo --address=127.0.0.1 -port-5555 &

# star web
nohup python3.7 app.py &

# keep running...
/bin/bash
