#!/usr/bin/env python3
# coding: utf-8

import logging.handlers

'''
捕获运行时的异常的日志
'''
_runtime_log_file = 'instance/nemo.runtime.log'
_runtime_log_fmt = '%(asctime)s - %(levelname)s - %(filename)s#%(funcName)s():%(lineno)s - %(name)s - %(message)s'
_runtime_handler = logging.handlers.RotatingFileHandler(_runtime_log_file, maxBytes=1024 * 1024, backupCount=5)
_runtime_handler.setFormatter(logging.Formatter(_runtime_log_fmt))
logger = logging.getLogger("main")
logger.addHandler(_runtime_handler)
logger.setLevel(logging.DEBUG)

'''
flask的web访问日志处理handler，在flask app实始化时调用
'''
_web_log_file = 'instance/nemo.web.log'
_web_log_fmt = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
web_handler = logging.handlers.RotatingFileHandler(_web_log_file, maxBytes=1024 * 1024, backupCount=5)
web_handler.setFormatter(logging.Formatter(_web_log_fmt))
