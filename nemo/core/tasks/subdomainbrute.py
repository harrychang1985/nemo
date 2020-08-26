#!/usr/bin/env python3
# coding:utf-8

import traceback

from nemo.common.thirdparty.ESD import EnumSubDomain
from nemo.common.utils.loggerutils import logger

from .taskbase import TaskBase


class SubDmainBrute(TaskBase):
    '''子域名爆破，使用ESD（https://github.com/FeeiCN/ESD）
    ESD为修改版本，去除了搜索引擎和API接口，只保留了爆破、CA、域传输方式
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
        self.task_name = 'subdomainbrute'
        self.task_description = '子域名爆破'
        self.source = 'subdomainbrute'

    def prepare(self, options):
        '''解析参数
        '''
        self.target = options['target']
        self.org_id = self.get_option('org_id', options, self.org_id)

    def execute(self, data):
        '''调用子域名爆破
        '''
        domain_list = []
        for domain in data:
            try:
                # engines = []，不启用接口查询功能
                domains = EnumSubDomain(domain).run()
                for k, v in domains.items():
                    d = {'domain': k, 'A': v}
                    domain_list.append(d)
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error('subdomain target:{}'.format(domain))

        return domain_list

    def run(self, options):
        ''' 子域名爆破
        '''
        self.prepare(options)
        domain_list = self.execute(self.target)
        # print(domain_list)
        # 保存结果：
        result = self.save_domain(domain_list)
        result['status'] = 'success'

        return result
