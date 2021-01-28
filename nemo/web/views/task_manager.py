#!/usr/bin/env python3
# coding:utf-8
import traceback
from copy import deepcopy
from datetime import datetime

from flask import request
from flask import render_template
from flask import Blueprint
from flask import jsonify
from tld import get_fld

from nemo.common.utils.config import load_config
from nemo.common.utils.loggerutils import logger
from nemo.core.tasks.taskapi import TaskAPI
from nemo.core.database.task import Task

from .authenticate import login_check

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

def _copy_task_info_datetime(data_to, data_from, key):
    if key not in data_from:
        return
    if data_from[key] == '' or data_from[key] == None:
        return

    data_to[key] = datetime.fromtimestamp(data_from[key])


def _update_and_save_task(task_id):
    task_info_result = TaskAPI().get_task_info(task_id)
    if task_info_result['status'] == 'success':
        task_app = Task()
        task_data = {'task_id': task_id, 'task_name': task_info_result['result']['name']}
        task_app.copy_key(task_data, task_info_result['result'], 'args')
        task_app.copy_key(task_data, task_info_result['result'], 'kwargs')
        task_app.copy_key(task_data, task_info_result['result'], 'worker')
        task_app.copy_key(task_data, task_info_result['result'], 'state')
        task_app.copy_key(task_data, task_info_result['result'], 'result')
        _copy_task_info_datetime(task_data, task_info_result['result'], 'received')
        _copy_task_info_datetime(task_data, task_info_result['result'], 'retried')
        _copy_task_info_datetime(task_data, task_info_result['result'], 'revoked')
        _copy_task_info_datetime(task_data, task_info_result['result'], 'started')
        _copy_task_info_datetime(task_data, task_info_result['result'], 'succeeded')
        _copy_task_info_datetime(task_data, task_info_result['result'], 'failed')

        task_app.save_and_update(task_data)



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
        subtask = request.form.get('subtask')
        portscan_bin = request.form.get('bin')

        if not target:
            return jsonify({'status': 'fail', 'msg': 'no target or port'})
        result = {'status': 'success', 'result': {'task-id': 0}}
        # 格式化tatget
        target = list(set([x.strip() for x in target.split('\n')]))
        # 子任务模式，将每一个目标拆按行成分成多个目标分别启动
        if _str2bool(subtask):
            task_target = [[x] for x in target]
        else:
            task_target = [target]
        for t in task_target:
            # 任务选项options
            options = {'target': t, 'port': port, 'bin': portscan_bin,
                       'org_id': org_id, 'rate': rate, 'ping': _str2bool(ping), 'tech': nmap_tech,
                       'iplocation': _str2bool(iplocation), 'webtitle': _str2bool(webtitle),
                       'whatweb': _str2bool(whatweb)
                       }
            # 启动portscan任务
            if _str2bool(portscan):
                result = taskapi.start_task(
                    'portscan', kwargs={'options': deepcopy(options)})
                if result['status'] == 'success' and result['result']['task-id']:
                    _update_and_save_task(result['result']['task-id'])
            # IP归属地：如果有portscan任务，则在portscan启动，否则单独启动任务
            if _str2bool(iplocation) and not _str2bool(portscan):
                result = taskapi.start_task(
                    'iplocation', kwargs={'options': deepcopy(options)})
                if result['status'] == 'success' and result['result']['task-id']:
                    _update_and_save_task(result['result']['task-id'])
            # 启动FOFA搜索任务
            if _str2bool(fofasearch):
                result = taskapi.start_task(
                    'fofasearch', kwargs={'options': deepcopy(options)})
                if result['status'] == 'success' and result['result']['task-id']:
                    _update_and_save_task(result['result']['task-id'])
            # 启动Shodan搜索任务
            if _str2bool(shodansearch):
                result = taskapi.start_task('shodansearch', kwargs={
                    'options': deepcopy(options)})
                if result['status'] == 'success' and result['result']['task-id']:
                    _update_and_save_task(result['result']['task-id'])

        return jsonify(result)
    except Exception as e:
        logger.error(traceback.format_exc())
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
        subdomainbrute = request.form.get('subdomainbrute')
        webtitle = request.form.get('webtitle')
        whatweb = request.form.get('whatweb')
        fofasearch = request.form.get('fofasearch')
        portscan = request.form.get('portscan')
        networkscan = request.form.get('networkscan')
        fld_domain = request.form.get('fld_domain')
        subtask = request.form.get('subtask')

        if not target:
            return jsonify({'status': 'fail', 'msg': 'no target'})
        result = {'status': 'success', 'result': {'task-id': 0}}
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
        # 子任务模式，将每一个目标拆按行成分成多个目标分别启动
        if _str2bool(subtask):
            task_target = [[x] for x in target]
        else:
            task_target = [target]
        for t in task_target:
            # 任务选项options
            options = {'target': t,
                       'org_id': org_id, 'subdomain': _str2bool(subdomain), 'subdomainbrute': _str2bool(subdomainbrute),
                       'webtitle': _str2bool(webtitle),
                       'portscan': _str2bool(portscan), 'networkscan': _str2bool(networkscan),
                       'whatweb': _str2bool(whatweb)}
            # 是否有portscan任务
            if _str2bool(portscan) or _str2bool(networkscan):
                result = taskapi.start_task(
                    'domainscan_with_portscan', kwargs={'options': deepcopy(options)})
                if result['status'] == 'success' and result['result']['task-id']:
                    _update_and_save_task(result['result']['task-id'])
            else:
                result = taskapi.start_task(
                    'domainscan', kwargs={'options': deepcopy(options)})
                if result['status'] == 'success' and result['result']['task-id']:
                    _update_and_save_task(result['result']['task-id'])
            # 是否有FOFA搜索
            if _str2bool(fofasearch):
                result = taskapi.start_task('fofasearch', kwargs={
                    'options': deepcopy(options)})
                if result['status'] == 'success' and result['result']['task-id']:
                    _update_and_save_task(result['result']['task-id'])

        return jsonify(result)
    except Exception as e:
        logger.error(traceback.format_exc())
        print(e)
        return jsonify({'status': 'fail', 'msg': str(e)})


@task_manager.route('/task-list', methods=['GET', 'POST'])
@login_check
def task_list_view():
    '''任务列表展示
    '''
    if request.method == 'GET':
        return render_template('task-list.html')

    task_list = []
    json_data = {}
    index = 1

    try:
        draw = int(request.form.get('draw'))
        start = int(request.form.get('start'))
        length = int(request.form.get('length'))
        task_state = request.form.get('task_state')
        task_name = request.form.get('task_name')
        task_args = request.form.get('task_args')
        date_delta = request.form.get('date_delta')

        task_app = Task()
        task_results = task_app.gets_by_search(task_name=task_name, task_args=task_args, state=task_state,
                                               date_delta=date_delta,
                                               page=(start // length) + 1, rows_per_page=length)
        for row in task_results:
            # update  the task status
            if row['state'] not in ['SUCCESS','FAILURE','REVOKED']:
                _update_and_save_task(row['task_id'])
                row = task_app.get(row['id'])

            task = {'index': index + start, 'id': row['id'], 'task_id': row['task_id'], 'worker': row['worker'],
                    'task_name': row['task_name'].replace('nemo.core.tasks.tasks.', '').replace('_', '-'),
                    'state': row['state'], 'result': row['result']}
            row_args = ''
            if row['kwargs']:
                if len(row['kwargs']) > 150:
                    row_args = row['kwargs'][:150] + '...'
                else:
                    row_args = row['kwargs']
            task['kwargs'] = row_args
            task.update(received='', started='', succeeded='', failed='', retried='', revoked='')
            if row['received']:
                task.update(received=row['received'].strftime("%Y-%m-%d %H:%M:%S"))
            runtime = 0
            if row['started']:
                task.update(started=row['started'].strftime("%Y-%m-%d %H:%M:%S"))
                if row['succeeded']:
                    runtime = row['succeeded'].timestamp() - row['started'].timestamp()
                    task.update(succeeded=row['succeeded'].strftime("%Y-%m-%d %H:%M:%S"))
                elif row['failed']:
                    runtime = row['failed'].timestamp() - row['started'].timestamp()
                    task.update(failed=row['failed'].strftime("%Y-%m-%d %H:%M:%S"))
                elif row['retried']:
                    runtime = row['retried'].timestamp() - row['started'].timestamp()
                    task.update(retried=row['retried'].strftime("%Y-%m-%d %H:%M:%S"))
                elif row['revoked']:
                    runtime = row['revoked'].timestamp() - row['started'].timestamp()
                    task.update(revoked=row['revoked'].strftime("%Y-%m-%d %H:%M:%S"))
            task.update(runtime=_format_runtime(runtime))
            task.update(runtime=_format_runtime(runtime))

            task_list.append(task)
            index += 1

        count = task_app.count_by_search(task_name=task_name, task_args=task_args, state=task_state,
                                         date_delta=date_delta)
        json_data = {
            'draw': draw,
            'recordsTotal': count,
            'recordsFiltered': count,
            'data': task_list
        }
    except Exception as e:
        logger.error(traceback.format_exc())
        print(e)

    return jsonify(json_data)


@task_manager.route('/task-info', methods=['GET'])
@login_check
def task_info_view():
    task_id = request.args.get('task_id')
    task_app = Task()
    ips = task_app.gets(query={'task_id': task_id})
    if ips and len(ips) > 0:
        row = ips[0]
        # update  the task status
        if row['state'] not in ['SUCCESS', 'FAILURE', 'REVOKED']:
            _update_and_save_task(row['task_id'])
            row = task_app.get(row['id'])
        task = {'id': row['id'], 'task_id': row['task_id'], 'worker': row['worker'],
                'task_name': row['task_name'],
                'state': row['state'], 'result': row['result'], 'kwargs': row['kwargs']}

        task.update(received='', started='', succeeded='', failed='', retried='', revoked='')
        if row['received']:
            task.update(received=row['received'].strftime("%Y-%m-%d %H:%M:%S"))
        runtime = 0
        if row['started']:
            task.update(started=row['started'].strftime("%Y-%m-%d %H:%M:%S"))
            if row['succeeded']:
                runtime = row['succeeded'].timestamp() - row['started'].timestamp()
                task.update(succeeded=row['succeeded'].strftime("%Y-%m-%d %H:%M:%S"))
            elif row['failed']:
                runtime = row['failed'].timestamp() - row['started'].timestamp()
                task.update(failed=row['failed'].strftime("%Y-%m-%d %H:%M:%S"))
            elif row['retried']:
                runtime = row['retried'].timestamp() - row['started'].timestamp()
                task.update(retried=row['retried'].strftime("%Y-%m-%d %H:%M:%S"))
            elif row['revoked']:
                runtime = row['revoked'].timestamp() - row['started'].timestamp()
                task.update(revoked=row['revoked'].strftime("%Y-%m-%d %H:%M:%S"))
        task.update(runtime=_format_runtime(runtime))

        task.update(create_datetime=row['create_datetime'].strftime("%Y-%m-%d %H:%M:%S"))
        task.update(update_datetime=row['update_datetime'].strftime("%Y-%m-%d %H:%M:%S"))
    else:
        task = None

    return render_template('task-info.html', task_info=task)


@task_manager.route('/task-stop', methods=['POST'])
@login_check
def task_stop_view():
    '''取消一个任务
    '''
    task_id = request.form.get('task-id')
    if not task_id:
        return jsonify({'status': 'fail'})

    result = TaskAPI().revoke_task(task_id)
    _update_and_save_task(task_id)

    return jsonify(result)


@task_manager.route('/task-delete', methods=['POST'])
@login_check
def task_delete_view():
    '''删除一个任务
    '''
    task_id = request.form.get('task-id')
    if not task_id:
        return jsonify({'status': 'fail'})

    task_app = Task()
    task_objs = task_app.gets({'task_id': task_id})
    if task_objs and len(task_objs) > 0:
        task_app.delete(task_objs[0]['id'])
        return jsonify({'status': 'success'})

    return jsonify({'status': 'fail'})
