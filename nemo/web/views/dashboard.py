#!/usr/bin/env python3
# coding:utf-8

from flask import Blueprint
from flask import render_template
from flask import jsonify
from flask import request
from .authenticate import login_check

from nemo.core.database.ip import Ip
from nemo.core.database.domain import Domain
from nemo.core.tasks.taskapi import TaskAPI

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/dashboard', methods=['GET', 'POST'])
@login_check
def view_dashboard():
    '''dashbord页面显示
    '''
    if request.method == 'GET':
        return render_template('dashboard.html')
    # 统计信息
    r = TaskAPI().get_celery_workers()
    total = 0
    active = 0
    if r['status'] == 'success':
        for k, v in r['result'].items():
            for tk, tv in v['stats']['total'].items():
                total += tv

            active += len(v['active'])
    dashboard_data = {
        'ip_count': Ip().count(),
        'domain_count': Domain().count(),
        'task_total': total,
        'task_active': active
    }
    return jsonify(dashboard_data)


@dashboard.route('/dashboard-task-info', methods=['POST'])
@login_check
def view_dashboard_task_info():
    '''统计任务
    '''
    r = TaskAPI().get_celery_workers()
    total = 0
    active = 0
    if r['status'] == 'success':
        for k, v in r['result'].items():
            for tk, tv in v['stats']['total'].items():
                total += tv

            active += len(v['active'])
    data = {'task_info':'{}/{}'.format(active,total)}
    return jsonify(data)
