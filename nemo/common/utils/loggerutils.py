#!/usr/bin/env python3
# coding: utf-8
# author: xu3352<xu3352@gmail.com>
"""
Python 日志工具包
@see https://blog.csdn.net/chosen0ne/article/details/7319306
"""
import logging
import logging.handlers

log_file = 'output.log'
fmt = '%(asctime)s - %(levelname)s - %(filename)s#%(funcName)s():%(lineno)s - %(name)s - %(message)s'

# 实例化handler
handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
formatter = logging.Formatter(fmt)  # 实例化formatter
handler.setFormatter(formatter)     # 为handler添加formatter

logger = logging.getLogger("main")  # 获取名为tst的logger
logger.addHandler(handler)          # 为logger添加handler
logger.setLevel(logging.DEBUG)      # 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'


if __name__ == '__main__':
    logger.debug("first message debug")
    logger.info("first message info")
    logger.warning("first message warning")
    logger.error("first message error")
    logger.critical("first message critical")