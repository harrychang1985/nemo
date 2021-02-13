#!/usr/bin/env python3
# coding:utf-8
import traceback

import requests
from requests.auth import HTTPBasicAuth

from instance.config import ProductionConfig
from nemo.common.utils.loggerutils import logger


class TaskAPI():
    '''
       任务接口API，用于创建、查询和取消应用
       采用Flower的API接口
    '''

    def __init__(self):
        # flower  build ip and port
        self.api_host = 'http://{}:{}'.format(
            ProductionConfig.FLOWER_BIND_ADDR, ProductionConfig.FLOWER_PORT)
        # task package
        self.task_package = 'nemo.core.tasks.tasks'
        # request timeout
        self.timeout = 5
        # flower Authenticate
        self.auth = HTTPBasicAuth(ProductionConfig.FLOWER_AUTH_USER, ProductionConfig.FLOWER_AUTH_PASSWORD)

    def __process_result(self, response):
        '''处理返回数据
        '''
        result = {}
        result['result'] = []
        try:
            result['code'] = response.status_code
            if response.status_code == requests.codes.ok:
                result['status'] = 'success'
                result['result'] = response.json()
            else:
                result['status'] = 'fail'
        except Exception as e:
            logger.error(traceback.format_exc())
            result['code'] = '-1'
            result['status'] = str(e)

        return result

    def start_task(self, task_name, args=None, kwargs=None):
        '''启动一个task
        '''
        api = 'api/task/async-apply/{}.{}'.format(self.task_package, task_name)
        url = '{}/{}'.format(self.api_host, api)
        data = {}
        if args:
            data['args'] = args
        if kwargs:
            data['kwargs'] = kwargs
        result = {}
        try:
            r = requests.post(url, auth=self.auth, json=data,
                              timeout=self.timeout)
            result = self.__process_result(r)
        except Exception as e:
            logger.error(traceback.format_exc())
            result['code'] = '-1'
            result['status'] = str(e)

        return result

    def get_tasks(self, limit=10, task_name=None, state=None):
        '''获取所有task，包括已执行完成的
        建议设置filter条件
        state:  PENDING,STARTED,SUCCESS,FAILURE,REVOKED,RETRY
        #
        Query Parameters:
        limit – maximum number of tasks
        workername – filter task by workername
        taskname – filter tasks by taskname
        state – filter tasks by state
        '''
        api = 'api/tasks'
        url = '{}/{}'.format(self.api_host, api)
        params = {}
        if limit:
            params['limit'] = limit
        if state:
            params['state'] = state
        if task_name:
            params['taskname'] = task_name
        result = {}
        try:
            r = requests.get(url, auth=self.auth,
                             params=params, timeout=self.timeout)
            result = self.__process_result(r)
        except Exception as e:
            logger.error(traceback.format_exc())
            result['code'] = '-1'
            result['status'] = str(e)

        return result

    def get_task_result(self, task_id):
        '''获取一个task的执行结果
        '''
        api = 'api/task/result/{}'.format(task_id)
        url = '{}/{}'.format(self.api_host, api)
        result = {}
        try:
            r = requests.get(url, auth=self.auth, timeout=self.timeout)
            result = self.__process_result(r)
        except Exception as e:
            logger.error(traceback.format_exc())
            result['code'] = '-1'
            result['status'] = str(e)

        return result

    def get_task_info(self, task_id):
        '''获取一个task的信息
        '''
        api = 'api/task/info/{}'.format(task_id)
        url = '{}/{}'.format(self.api_host, api)
        result = {}
        try:
            r = requests.get(url, auth=self.auth, timeout=self.timeout)
            result = self.__process_result(r)
        except Exception as e:
            logger.error(traceback.format_exc())
            result['code'] = '-1'
            result['status'] = str(e)

        return result

    def revoke_task(self, task_id, terminate=True):
        '''取消一个task的执行
        '''
        api = 'api/task/revoke/{}?terminate={}'.format(
            task_id, 'true' if terminate else 'false')
        url = '{}/{}'.format(self.api_host, api)
        result = {}
        try:
            r = requests.post(url, auth=self.auth, timeout=self.timeout)
            result = self.__process_result(r)
        except Exception as e:
            logger.error(traceback.format_exc())
            result['code'] = '-1'
            result['status'] = str(e)

        return result

    def get_celery_workers(self):
        '''得到worker的统计信息
        '''
        api = 'api/workers?refresh=1'
        url = '{}/{}'.format(self.api_host, api)
        result = {}
        try:
            r = requests.get(url, auth=self.auth, timeout=self.timeout)
            result = self.__process_result(r)
        except Exception as e:
            logger.error(traceback.format_exc())
            result['code'] = '-1'
            result['status'] = str(e)

        return result
