#!/usr/bin/env python3
# coding:utf-8
import copy
from datetime import datetime
from celery import Celery, Task

from instance.config import ProductionConfig

from .domainscan import DomainScan
from .fofa import Fofa
from .iplocation import IpLocation
from .portscan import PortScan
from .shodan_search import Shodan
from .pocsuite3 import Pocsuite3
from .xray import XRay
from .taskapi import TaskAPI
from nemo.core.database.task import Task as TaskDatabase

broker = 'amqp://{}:{}@{}:{}/'.format(ProductionConfig.MQ_USERNAME,
                                      ProductionConfig.MQ_PASSWORD, ProductionConfig.MQ_HOST, ProductionConfig.MQ_PORT)
celery_app = Celery('nemo', broker=broker, backend='rpc://')

TASK_ACTION = {
    'portscan':   PortScan().run,
    'iplocation':   IpLocation().run,
    'fofasearch':   Fofa().run,
    'shodansearch':   Shodan().run,
    'domainscan':   DomainScan().run,
    'pocsuite3':  Pocsuite3().run,
    'xray':   XRay().run,
}


class UpdateTaskStatus(Task):
    '''在celery的任务异步完成时，显示完成状态和结果
    '''

    def __format_datetime(self,timestamp):
        '''将timestamp时间戳格式化
        '''
        if not timestamp:
            return ''
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def __copy_not_null(self,data_to, data_from, key):
        if key not in data_from:
            return
        if data_from[key] == '' or data_from[key] == None:
            return

        data_to[key] = copy.copy(data_from[key])

    def __save_and_update_task(self,task_id, task_result):
        if not task_id:
            return

        task_data = {'task_id': task_id, 'task_name': task_result['task_name'], 'state': task_result['state']}

        task_api = TaskAPI()
        task_result_now = task_api.get_task_info(task_id)
        if task_result_now['status'] == 'success':
            task_data['started'] = self.__format_datetime(task_result_now['result']['started'])
            task_data['received'] = self.__format_datetime(task_result_now['result']['received'])

        self.__copy_not_null(task_data, task_result, 'result')
        self.__copy_not_null(task_data, task_result, 'succeeded')
        self.__copy_not_null(task_data, task_result, 'failed')
        self.__copy_not_null(task_data, task_result, 'revoked')
        self.__copy_not_null(task_data, task_result, 'retried')

        task_app = TaskDatabase()
        task_app.save_and_update(task_data)

    def on_success(self, retval, task_id, args, kwargs):
        print('task {} done: {}'.format(task_id, retval))
        task_result = {'task_name':self.name,'result':str(retval),'state':'SUCCESS','succeeded':datetime.now()}
        self.__save_and_update_task(task_id,task_result)

        return super(UpdateTaskStatus, self).on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('task {} fail, reason: {}'.format(task_id, exc))
        task_result = {'task_name': self.name, 'result': str(exc), 'state': 'FAILURE', 'failed': datetime.now()}
        self.__save_and_update_task(task_id, task_result)

        return super(UpdateTaskStatus, self).on_failure(exc, task_id, args, kwargs, einfo)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        print('task {} retry, reason: {}'.format(task_id, exc))
        task_result = {'task_name': self.name, 'result': str(exc), 'state': 'RETRY', 'retried': datetime.now()}
        self.__save_and_update_task(task_id, task_result)

        return super(UpdateTaskStatus, self).on_failure(exc, task_id, args, kwargs, einfo)

def new_task(action, options):
    '''开始一个任务
    '''
    if action in TASK_ACTION:
        task_run = TASK_ACTION.get(action)
        result = task_run(options)
        return result
    else:
        return {'status': 'fail', 'msg': 'no task'}


@celery_app.task(base=UpdateTaskStatus)
def portscan(options):
    '''端口扫描综合任务
    '''
    return new_task('portscan', options)


@celery_app.task(base=UpdateTaskStatus)
def fofasearch(options):
    '''调用fofa API
    '''
    return new_task('fofasearch', options)

@celery_app.task(base=UpdateTaskStatus)
def shodansearch(options):
    '''调用shodan API
    '''
    return new_task('shodansearch', options)

@celery_app.task(base=UpdateTaskStatus)
def domainscan(options):
    '''域名收集综合信息
    '''
    return new_task('domainscan', options)

@celery_app.task(base=UpdateTaskStatus)
def iplocation(options):
    '''IP归属地
    '''
    return new_task('iplocation', options)


@celery_app.task(base=UpdateTaskStatus)
def domainscan_with_portscan(options):
    '''域名收集综合信息
    '''
    domainscan = DomainScan()
    portscan = PortScan()
    # 域名任务
    domainscan.prepare(options)
    domain_list = domainscan.execute()
    result  =  domainscan.save_domain(domain_list)
    # 得到域名的IP及C段
    ip_set = set()
    for domain in domain_list:
        if 'A' in domain and domain['A']:
            for ip in domain['A']:
                if options['networkscan']:
                    network = ip.split('.')[0:3]
                    network.append('0/24')
                    ip_set.update(['.'.join(network)])
                else:
                    ip_set.update(domain['A'])
    # 生成portscan的默认参数
    options_portscan = {'target': list(ip_set), 'iplocation':True,'webtitle': options['webtitle'],
                        'whatweb':options['whatweb'], 'org_id': None if 'org_id' not in options else options['org_id']}
    # 执行portscan任务
    result.update(portscan.run(options_portscan))

    return result

@celery_app.task(base=UpdateTaskStatus)
def pocsuite3(options):
    '''pocsuite3漏洞验证
    '''
    return new_task('pocsuite3', options)

@celery_app.task(base=UpdateTaskStatus)
def xray(options):
    '''xray
    '''
    return new_task('xray', options)
