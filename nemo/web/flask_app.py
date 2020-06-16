#!/usr/bin/env python3
# coding:utf-8
from flask import Flask
from nemo.web.views.authenticate import authenticate
from nemo.web.views.index import index
from nemo.web.views.dashboard import dashboard
from nemo.web.views.asset_manager import asset_manager
from nemo.web.views.org_manager import org_manager
from nemo.web.views.task_manager import task_manager
from nemo.web.views.config_manager import config_manager

from instance.config import ProductionConfig

web_app = Flask(__name__)
web_app.secret_key = ProductionConfig.SECRET_KEY

# blueprint register
web_app.register_blueprint(authenticate)
web_app.register_blueprint(index)
web_app.register_blueprint(dashboard)
web_app.register_blueprint(asset_manager)
web_app.register_blueprint(org_manager)
web_app.register_blueprint(task_manager)
web_app.register_blueprint(config_manager)

