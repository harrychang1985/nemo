#!/bin/bash

export PYTHONOPTIMIZE=1
ps aux|grep celery|awk '{print $2}'|xargs kill
ps aux|grep "app.py"|awk '{print $2}'|xargs kill
nohup celery -A nemo.core.tasks.tasks worker --loglevel info -c 4 &
sleep 5
nohup celery flower -A nemo.core.tasks.tasks --address=127.0.0.1 -port-5555 &
nohup python3 app.py &

tail -f nohup.out instance/*.log
