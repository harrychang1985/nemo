#!/usr/bin/env python3
# coding:utf-8

import os

class Config:
    def __init__(self):
        pass

    WEB_USER = 'nemo'  
    WEB_PASSWORD = 'nemo'
    SECRET_KEY = os.urandom(16)
    WEB_HOST = '0.0.0.0'  
    WEB_PORT = 5000  
    VERSION = '1.0.0'


class ProductionConfig(Config):
    def __init__(self):
        super().__init__()

    # database
    DB_HOST = '127.0.0.1' 
    DB_PORT = 3306
    DB_NAME = 'nemo'
    DB_USERNAME = 'nemo'
    DB_PASSWORD = 'nemo2020'

    # rabbitmq
    MQ_HOST = 'localhost' 
    MQ_PORT = 5672
    MQ_USERNAME = 'nemo'
    MQ_PASSWORD = 'nemo2020'

    # flower
    FLOWER_BIND_ADDR = '127.0.0.1'
    FLWOER_PORT = 5555

