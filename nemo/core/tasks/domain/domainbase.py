#!/usr/bin/env python3
# coding:utf-8
import traceback

from nemo.common.utils.loggerutils import logger
from nemo.core.tasks.taskbase import TaskBase
from .ipdomain import IpDomain


class DomainBase(TaskBase):
    '''域名信息收集方法的基类
    参数：options
            {
                'target':   ['domain',...],domain列表
                'org_id':   域名所属的组织
            }
    任务结果：
        保存为domain资产的格式
        {'domain': 'www.google.com', 'CNAME': [], 'A': ['8.8.8.8']}, 
        {'domain': 'dns.google.com', 'CNAME': [], 'A': ['9.9.9.9']}]
    '''

    def __init__(self):
        super().__init__()
        self.task_name = 'domainbase'
        self.task_description = '域名信息收集的基础类'
        self.source = 'domainbase'

    def fetch_domain(self, domain):
        '''调用收集域名信息
        由各继承类实现
        '''

    def prepare(self, options):
        '''解析参数
        '''
        self.target = options['target']
        self.org_id = self.get_option('org_id', options, self.org_id)

    def execute(self, data):
        '''收集域名
        '''
        domains = set()
        for domain in data:
            try:
                domains.update(self.fetch_domain(domain))
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error('{} target:{}'.format(self.task_name, domain))
        # 域名结果格式化
        domain_list = []
        for d in domains:
            domain = d.strip().strip('/').replace('https://', '').replace('http://', '').split(':')[0]
            domain_list.append({'domain': domain})

        return domain_list

    def run(self, options):
        ''' 收集域名信息
        '''
        self.prepare(options)
        domain_list = self.execute(self.target)
        # 查询域名IP地址
        ipdomain = IpDomain()
        ipdomain.execute(domain_list)
        print(domain_list)
        # 保存结果：
        result = self.save_domain(domain_list)
        result['status'] = 'success'

        return result
