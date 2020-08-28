#!/bin/bash

export PYTHONOPTIMIZE=1
ps aux|grep celery|awk '{print $2}'|xargs kill
ps aux|grep "app.py"|awk '{print $2}'|xargs kill
nohup python3.7 -m celery -A nemo.core.tasks.tasks worker --loglevel info -c 2 &
sleep 5
nohup python3.7 -m celery flower -A nemo.core.tasks.tasks --basic_auth=nemo:nemo --address=127.0.0.1 -port-5555 &
nohup python3.7 app.py &

tail -f nohup.out instance/*.log
