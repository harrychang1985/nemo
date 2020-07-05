#!/usr/bin/env python3
# coding:utf-8
from functools import wraps
import traceback

from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session

from instance import config
from nemo.common.utils.loggerutils import logger

authenticate = Blueprint('authenticate', __name__)
ProductionConfig = config.ProductionConfig


@authenticate.route('/login', methods=['POST', 'GET'])
def login_view():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if password == ProductionConfig.WEB_PASSWORD:
            try:
                session['login'] = 'A1akPTQJiz9wi9yo4rDz8ubM1b1'
                logger.info('[login success] from {}'.format(request.remote_addr))
                return redirect(url_for('index.view_index'))
            except Exception as e:
                logger.error(traceback.format_exc())

                return render_template('login.html', msg='Internal Server Error')
        else:
            logger.info('[login fail] from {}'.format(request.remote_addr))
            return render_template('login.html', msg='Invalid Password')

    else:
        return render_template('login.html')


@authenticate.route('/logout', methods=['GET'])
def logout():
    session['login'] = ''
    logger.info('[logout] from {}'.format(request.remote_addr))
    return redirect(url_for('authenticate.login_view'))


def login_check(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            if session['login'] == 'A1akPTQJiz9wi9yo4rDz8ubM1b1':
                return f(*args, **kwargs)
            else:
                return redirect(url_for('authenticate.login_view'))
        except:
            return redirect(url_for('authenticate.login_view'))
            
    return wrapper
