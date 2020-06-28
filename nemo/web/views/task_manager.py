#!/usr/bin/env python3
# coding:utf-8
from datetime import datetime
from copy import deepcopy

from flask import request
from flask import render_template
from flask import Blueprint
from flask import jsonify
from tld import get_fld

from .authenticate import login_check
from nemo.core.database.organization import Organization
from nemo.core.database.ip import Ip
from nemo.core.database.domain import Domain
from nemo.core.tasks.taskapi import TaskAPI
from nemo.common.utils.config import load_config


task_manager = Blueprint("task_manager", __name__)


def _str2bool(v):
    return str(v).lower() in ('true', 'success', 'yes', '1')


def _format_datetime(timestamp):
    '''将timestamp时间戳格式化
    '''
    if not timestamp:
        return ''
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _format_runtime(seconds):
    '''将执行时长的秒数转换为小时、分钟和秒
    '''
    if not seconds:
        return ''
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    result = []
    if h > 0:
        result.append('{}时'.format(h))
    if m > 0:
        result.append('{}分'.format(m))
    if s > 0:
        result.append('{}秒'.format(s))
    if len(result) == 0:
        result.append('<1秒')

    return ''.join(result)


@task_manager.route('/task-start-portscan', methods=['POST'])
@login_check
def task_start_portscan_view():
    '''启动IP端口扫描任务
    '''
    taskapi = TaskAPI()
    config_datajson = load_config()
    try:
        # 获取参数
        target = request.form.get('target', default='')
        portscan = request.form.get('portscan')
        port = request.form.get(
            'port', default=config_datajson['nmap']['port'])
        org_id = request.form.get('org_id', type=int, default=None)
        rate = request.form.get(
            'rate', type=int, default=config_datajson['nmap']['rate'])
        nmap_tech = request.form.get(
            'nmap_tech', type=str, default=config_datajson['nmap']['tech'])
        iplocation = request.form.get('iplocation')
        ping = request.form.get('ping')
        webtitle = request.form.get('webtitle')
        whatweb = request.form.get('whatweb')
        fofasearch = request.form.get('fofasearch')
        shodansearch = request.form.get('shodansearch')

        if not target:
            return jsonify({'status': 'fail', 'msg': 'no target or port'})
        # 格式化tatget
        target = list(set([x.strip() for x in target.split('\n')]))
        # 任务选项options
        options = {'target': target, 'port': port,
                   'org_id': org_id, 'rate': rate, 'ping': _str2bool(ping), 'tech': nmap_tech,
                   'iplocation': _str2bool(iplocation), 'webtitle': _str2bool(webtitle), 'whatweb': _str2bool(whatweb)
                   }
        result = {'status': 'success', 'result': {'task-id': 0}}
        # 启动portscan任务
        if _str2bool(portscan):
            result = taskapi.start_task(
                'portscan', kwargs={'options': deepcopy(options)})
        # IP归属地：如果有portscan任务，则在portscan启动，否则单独启动任务
        if _str2bool(iplocation) and not _str2bool(portscan):
            result = taskapi.start_task(
                'iplocation', kwargs={'options': deepcopy(options)})
        # 启动FOFA搜索任务
        if _str2bool(fofasearch):
            result = taskapi.start_task(
                'fofasearch', kwargs={'options': deepcopy(options)})
        # 启动Shodan搜索任务
        if _str2bool(shodansearch):
            result = taskapi.start_task('shodansearch', kwargs={
                                        'options': deepcopy(options)})

        return jsonify(result)
    except Exception as e:
        print(e)
        return jsonify({'status': 'fail', 'msg': str(e)})


@task_manager.route('/task-start-domainscan', methods=['POST'])
@login_check
def task_start_domainscan_view():
    ''' 启动域名扫描任务
    '''
    taskapi = TaskAPI()
    try:
        # 获取参数
        target = request.form.get('target', default='')
        org_id = request.form.get('org_id', type=int, default=None)
        subdomain = request.form.get('subdomain')
        webtitle = request.form.get('webtitle')
        whatweb = request.form.get('whatweb')
        fofasearch = request.form.get('fofasearch')
        portscan = request.form.get('portscan')
        networkscan = request.form.get('networkscan')
        fld_domain = request.form.get('fld_domain')

        if not target:
            return jsonify({'status': 'fail', 'msg': 'no target'})
        # 格式化tatget
        target = list(set([x.strip() for x in target.split('\n')]))
        # 提取顶级域名加入到目标中
        if _str2bool(fld_domain):
            fld_set = set()
            for t in target:
                d = get_fld(t, fix_protocol=True)
                if d:
                    fld_set.add(d)
            if fld_set:
                target.extend(fld_set)
        # 任务选项options
        options = {'target': target,
                   'org_id': org_id, 'subdomain': _str2bool(subdomain), 'webtitle': _str2bool(webtitle),
                   'portscan': _str2bool(portscan), 'networkscan': _str2bool(networkscan), 'whatweb': _str2bool(whatweb)}
        # 是否有portscan任务
        if _str2bool(portscan) or _str2bool(networkscan):
            result = taskapi.start_task(
                'domainscan_with_portscan', kwargs={'options': deepcopy(options)})
        else:
            result = taskapi.start_task(
                'domainscan', kwargs={'options': deepcopy(options)})
        # 是否有FOFA搜索
        if _str2bool(fofasearch):
            taskapi.start_task('fofasearch', kwargs={
                               'options': deepcopy(options)})

        return jsonify(result)
    except Exception as e:
        print(e)
        return jsonify({'status': 'fail', 'msg': str(e)})


@task_manager.route('/task-list', methods=['GET', 'POST'])
@login_check
def task_list_view():
    '''任务列表展示
    '''
    if request.method == 'GET':
        return render_template('task-list.html')

    taskapi = TaskAPI()
    data = []
    try:
        draw = int(request.form.get('draw'))
        start = int(request.form.get('start'))
        length = int(request.form.get('length'))

        task_status = request.form.get('task_status')
        task_limit = request.form.get('task_limit', default=None)
        task_status = None if not task_status else task_status

        task_result = taskapi.get_tasks(limit=task_limit, state=task_status)
        if task_result['status'] == 'success':
            for k, t in task_result['result'].items():
                try:
                    task = {'uuid': t['uuid'], 'name': t['name'].replace('nemo.core.tasks.tasks.', '').replace('_', '-'),
                            'state': t['state'], 'args': t['args'], 'kwargs': t['kwargs'], 'result': t['result']}
                    task.update(received=_format_datetime(t['received']))
                    task.update(started=_format_datetime(t['started']))
                    task.update(runtime=_format_runtime(t['runtime']))
                    # 获取worker信息
                    task_info = taskapi.get_task_info(t['uuid'])
                    if task_info['status'] == 'success':
                        task.update(worker=task_info['result']['worker'])
                    else:
                        task.update(worker='')
                    data.append(task)
                except Exception as e:
                    print(e)
        count = len(data)
        json_data = {
            'draw': draw,
            'recordsTotal': count,
            'recordsFiltered': count,
            'data': data
        }
        return jsonify(json_data)
    except Exception as e:
        print(e)
        return jsonify({'draw': draw, 'data': [], 'recordsTotal': 0, 'recordsFiltered': 0})


@task_manager.route('/task-stop', methods=['POST'])
@login_check
def task_stop_view():
    '''取消一个任务
    '''
    task_id = request.form.get('task-id')
    if not task_id:
        return jsonify({'status': 'fail'})

    taskapi = TaskAPI()
    result = taskapi.revoke_task(task_id)

    return jsonify(result)
