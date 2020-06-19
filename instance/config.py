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
    MQ_USERNAME = 'guest'
    MQ_PASSWORD = 'guest'

    # flower
    FLOWER_BIND_ADDR = '127.0.0.1'
    FLWOER_PORT = 5555


class APIConfig():
    # FOFA
    FOFA_EMAIL = 'hancool@163.com'
    FOFA_KEY = '238ebb08523bff5cf297b96364f62440'
    # Shodan
    SHODAN_API_KEY = "Dw8SUKGAnaQ58FuZyqS3kXCCfFyIsekQ"


