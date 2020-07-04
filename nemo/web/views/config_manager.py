#!/usr/bin/env python3
# coding:utf-8

from flask import Blueprint
from flask import render_template
from flask import jsonify
from flask import request

from nemo.common.utils.config import load_config, save_config

from .authenticate import login_check

config_manager = Blueprint('config_manager', __name__)


def _str2bool(v):
    return str(v).lower() in ('true', 'success', 'yes', '1')


@config_manager.route('/adv-config-list', methods=['GET', 'POST'])
@login_check
def config_view():
    '''显示配置页面
    '''
    if request.method == 'GET':
        return render_template('config.html')

    config_data = load_config()
    
    return jsonify(config_data)


@config_manager.route('/adv-config-save-nmap', methods=['POST'])
@login_check
def config_save_nmap_view():
    '''保存NMAP设置
    '''
    nmap_config = {'nmap_bin': request.form.get('nmap_bin'), 'masscan_bin': request.form.get('masscan_bin'),'port': request.form.get('nmap_port'),
                   'tech': request.form.get('nmap_tech'), 'rate': request.form.get('nmap_rate'), 
                   'ping': _str2bool(request.form.get('nmap_ping'))}

    config_jsondata = load_config()
    config_jsondata.update(nmap=nmap_config)

    save_config(config_jsondata)
    return jsonify({'status': 'success'})

@config_manager.route('/adv-config-save-whatweb', methods=['POST'])
@login_check
def config_save_whatweb_view():
    '''保存whatweb设置
    '''
    whatweb_config = {'bin': request.form.get('whatweb_bin')}

    config_jsondata = load_config()
    config_jsondata.update(whatweb=whatweb_config)

    save_config(config_jsondata)
    return jsonify({'status': 'success'})
