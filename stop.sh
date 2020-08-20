#!/bin/bash

ps aux|grep celery|awk '{print $2}'|xargs kill
ps aux|grep "app.py"|awk '{print $2}'|xargs kill
