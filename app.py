#!/usr/bin/env python3
# coding:utf-8
import sys
from gevent.pywsgi import WSGIServer
from nemo.web.flask_app import web_app
from instance.config import ProductionConfig


'''
系统入口，启动web server
'''


host = ProductionConfig.WEB_HOST
port = ProductionConfig.WEB_PORT


def web_server():
    http_server = WSGIServer((host, port), web_app)
    http_server.serve_forever()


def main_debug():
    web_app.run(host=host, port=port, debug=True)


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'debug':
        main_debug()
    else:
        web_server()
