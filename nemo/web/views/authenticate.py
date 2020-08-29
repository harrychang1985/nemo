#!/usr/bin/env python3
# coding:utf-8
from functools import wraps
import traceback

from flask import Flask
from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from instance import config
from nemo.common.utils.loggerutils import logger

authenticate = Blueprint('authenticate', __name__)
ProductionConfig = config.ProductionConfig

limiter = Limiter(
    Flask(__name__),
    key_func=get_remote_address,
    default_limits=["5/minute", "30/hour"]
)

@authenticate.route('/login', methods=['GET'])
def login_view():
    return render_template('login.html')


@authenticate.route('/login', methods=['POST'])
@limiter.limit("10/minute;30/hour;60/day")
def login_check_view():
    password = request.form.get('password')
    if password == ProductionConfig.WEB_PASSWORD:
        try:
            session['login'] = 'A1akPTQJiz9wi9yo4rDz8ubM1b1xqvH'
            logger.info('[login success] from {}'.format(request.remote_addr))
            return redirect(url_for('index.view_index'))
        except Exception as e:
            logger.error(traceback.format_exc())
            return redirect(url_for('authenticate.login_view'))
    else:
        logger.info('[login fail] from {}'.format(request.remote_addr))
        return redirect(url_for('authenticate.login_view'))

    
@authenticate.route('/logout', methods=['GET'])
def logout():
    session['login'] = ''
    logger.info('[logout] from {}'.format(request.remote_addr))
    return redirect(url_for('authenticate.login_view'))


def login_check(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            if session['login'] == 'A1akPTQJiz9wi9yo4rDz8ubM1b1xqvH':
                return f(*args, **kwargs)
            else:
                return redirect(url_for('authenticate.login_view'))
        except:
            return redirect(url_for('authenticate.login_view'))
            
    return wrapper
