#!/usr/bin/env python3
# coding:utf-8

from nemo.common.thirdparty.ESD import EnumSubDomain

from .domainbase import DomainBase


class SubDmainBrute(DomainBase):
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
        self.task_description = 'ESD子域名爆破'
        self.source = 'subdomainbrute'

    def fetch_domain(self, domain):
        domain_result = []
        domains = EnumSubDomain(domain).run()
        for k, v in domains.items():
            domain_result.append(k)

        return domain_result
