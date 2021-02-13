#!/usr/bin/env python3
# coding:utf-8
from datetime import datetime

from celery.result import AsyncResult

from .tasks import portscan, fofasearch, shodansearch, domainscan, domainscan_with_portscan, iplocation, pocsuite3, xray
from .tasks import save_task, update_task


class TaskAPI():
    '''
    任务接口API，用于创建、查询和取消应用
    采用celery原生接口
    '''

    def __init__(self):
        '''
        任务对应关系
        '''
        self.task_map = {'portscan': portscan,
                         'fofasearch': fofasearch,
                         'shodansearch': shodansearch,
                         'domainscan': domainscan,
                         'domainscan_with_portscan': domainscan_with_portscan,
                         'iplocation': iplocation,
                         'pocsuite3': pocsuite3,
                         'xray': xray
                         }

    def start_task(self, task_name, args=None, kwargs=None):
        '''
        启动一个task
        '''
        task_result = {}
        task_run = self.task_map.get(task_name)
        try:
            aResult = task_run.apply_async(kwargs=kwargs)
            task_result['status'] = 'success'
            task_result['result'] = {'task-id': aResult.id, 'state': aResult.state}

            save_task(aResult.id, task_name, kwargs, aResult.state)

        except Exception as ex:
            task_result['status'] = 'fail'
            task_result['result'] = {'msg': str(ex)}

        return task_result

    def get_task_info(self, task_id):
        '''
        获取一个task的信息
        '''
        task_result = {}
        try:
            aResult = AsyncResult(task_id)
            task_result['status'] = 'success'
            task_result['result'] = {'task-id': aResult.task_id, 'name': aResult.name, 'state': aResult.state,
                                     'worker': aResult.worker}
        except Exception as ex:
            task_result['status'] = 'fail'
            task_result['result'] = {'msg': str(ex)}

        return task_result

    def revoke_task(self, task_id):
        '''
        取消一个任务的执行
        '''
        task_result = {}
        try:
            aResult = AsyncResult(task_id)
            aResult.revoke(terminate=True)
            task_result['status'] = 'success'
            update_task(task_id, 'REVOKED', revoked=datetime.now())
        except Exception as ex:
            task_result['status'] = 'fail'
            task_result['result'] = {'msg': str(ex)}

        return task_result
