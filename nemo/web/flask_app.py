#!/usr/bin/env python3
# coding:utf-8
import logging
from flask import Flask
from nemo.web.views.authenticate import authenticate
from nemo.web.views.index import index
from nemo.web.views.dashboard import dashboard
from nemo.web.views.ip_manager import ip_manager
from nemo.web.views.domain_manager import domain_manager
from nemo.web.views.org_manager import org_manager
from nemo.web.views.task_manager import task_manager
from nemo.web.views.config_manager import config_manager

from instance.config import ProductionConfig
from nemo.common.utils.loggerutils import web_handler

web_app = Flask(__name__)
web_app.secret_key = ProductionConfig.SECRET_KEY

# save web access log to file
web_logger = logging.getLogger('werkzeug')
web_logger.addHandler(web_handler)

# blueprint register
web_app.register_blueprint(authenticate)
web_app.register_blueprint(index)
web_app.register_blueprint(dashboard)
web_app.register_blueprint(ip_manager)
web_app.register_blueprint(domain_manager)
web_app.register_blueprint(org_manager)
web_app.register_blueprint(task_manager)
web_app.register_blueprint(config_manager)