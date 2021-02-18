#!/usr/bin/env python3
# coding:utf-8
import time
from datetime import datetime

from celery import Celery, Task

from instance.config import ProductionConfig
from nemo.core.database.task import Task as TaskDatabase
from nemo.core.tasks.domain.domainscan import DomainScan
from nemo.core.tasks.ipport.portscan import PortScan
from nemo.core.tasks.onlineapi.fofa import Fofa
from nemo.core.tasks.onlineapi.iplocation import IpLocation
from nemo.core.tasks.onlineapi.shodan_search import Shodan
from nemo.core.tasks.poc.pocsuite3 import Pocsuite3
from nemo.core.tasks.poc.xray import XRay

broker = 'amqp://{}:{}@{}:{}/'.format(ProductionConfig.MQ_USERNAME,
                                      ProductionConfig.MQ_PASSWORD, ProductionConfig.MQ_HOST, ProductionConfig.MQ_PORT)
celery_app = Celery('nemo', broker=broker, backend='rpc://')


def save_task(task_id, task_name, kwargs, state):
    '''
    保存新的任务信息
    '''
    task_app = TaskDatabase()
    task_data = {'task_id': task_id, 'task_name': task_name, 'state': state, 'result': '',
                 'args': '()', 'kwargs': str(kwargs), 'received': datetime.now()}

    task_app.save_and_update(task_data)


def update_task(task_id, state, result=None, succeeded=None, failed=None, started=None, retried=None,
                received=None, revoked=None, worker=None):
    '''
    更新任务状态及相关信息
    '''
    task_data = {'task_id': task_id, 'state': state}
    if result:
        task_data['result'] = str(result)
    if succeeded:
        task_data['succeeded'] = succeeded
    if failed:
        task_data['failed'] = failed
    if started:
        task_data['started'] = started
    if retried:
        task_data['retried'] = retried
    if received:
        task_data['received'] = received
    if revoked:
        task_data['revoked'] = revoked
    if worker:
        task_data['worker'] = worker

    task_app = TaskDatabase()
    task_app.save_and_update(task_data)


class UpdateTaskStatus(Task):
    '''在celery的任务异步完成时，显示完成状态和结果
    '''

    def __init__(self):
        self.task_track_started = True
        self.task_ignore_result = True

        super(UpdateTaskStatus, self).__init__()

    def on_success(self, retval, task_id, args, kwargs):
        time.sleep(1)
        print('task {} done: {}'.format(task_id, retval))
        update_task(task_id, 'SUCCESS', result=retval, succeeded=datetime.now())
        return super(UpdateTaskStatus, self).on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        time.sleep(1)
        print('task {} fail, reason: {}'.format(task_id, exc))
        update_task(task_id, 'FAILURE', failed=datetime.now())
        return super(UpdateTaskStatus, self).on_failure(exc, task_id, args, kwargs, einfo)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        time.sleep(1)
        print('task {} retry, reason: {}'.format(task_id, exc))
        update_task(task_id, 'RETRY', retried=datetime.now())

        return super(UpdateTaskStatus, self).on_failure(exc, task_id, args, kwargs, einfo)


@celery_app.task(base=UpdateTaskStatus, bind=True)
def portscan(self, options):
    '''端口扫描综合任务
    '''
    # 由于对数据库操作的并发未采用“锁”机制，导致写库的时候会出现异常，因此简单采用延时机制“降低”冲突
    time.sleep(1)
    update_task(self.request.id, 'STARTED', started=datetime.now(), worker=self.request.hostname)
    return PortScan().run(options)


@celery_app.task(base=UpdateTaskStatus, bind=True)
def fofasearch(self, options):
    '''调用fofa API
    '''
    time.sleep(1)
    update_task(self.request.id, 'STARTED', started=datetime.now(), worker=self.request.hostname)
    return Fofa().run(options)


@celery_app.task(base=UpdateTaskStatus, bind=True)
def shodansearch(self, options):
    '''调用shodan API
    '''
    time.sleep(1)
    update_task(self.request.id, 'STARTED', started=datetime.now(), worker=self.request.hostname)
    return Shodan().run(options)


@celery_app.task(base=UpdateTaskStatus, bind=True)
def domainscan(self, options):
    '''域名收集综合信息
    '''
    time.sleep(1)
    update_task(self.request.id, 'STARTED', started=datetime.now(), worker=self.request.hostname)
    return DomainScan().run(options)


@celery_app.task(base=UpdateTaskStatus, bind=True)
def iplocation(self, options):
    '''IP归属地
    '''
    time.sleep(1)
    update_task(self.request.id, 'STARTED', started=datetime.now(), worker=self.request.hostname)
    return IpLocation().run(options)


@celery_app.task(base=UpdateTaskStatus, bind=True)
def domainscan_with_portscan(self, options):
    '''域名收集综合信息
    '''
    time.sleep(1)
    update_task(self.request.id, 'STARTED', started=datetime.now(), worker=self.request.hostname)

    domainscan = DomainScan()
    portscan = PortScan()
    # 域名任务
    domainscan.prepare(options)
    domain_list = domainscan.execute()
    result = domainscan.save_domain(domain_list)
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
    options_portscan = {'target': list(ip_set), 'iplocation': True, 'webtitle': options['webtitle'],
                        'whatweb': options['whatweb'], 'httpx': options['httpx'], 'org_id': None if 'org_id' not in options else options['org_id']}
    # 执行portscan任务
    result.update(portscan.run(options_portscan))
    return result


@celery_app.task(base=UpdateTaskStatus, bind=True)
def pocsuite3(self, options):
    '''pocsuite3漏洞验证
    '''
    time.sleep(1)
    update_task(self.request.id, 'STARTED', started=datetime.now(), worker=self.request.hostname)
    return Pocsuite3().run(options)


@celery_app.task(base=UpdateTaskStatus, bind=True)
def xray(self, options):
    '''xray
    '''
    time.sleep(1)
    update_task(self.request.id, 'STARTED', started=datetime.now(), worker=self.request.hostname)
    return XRay().run(options)
