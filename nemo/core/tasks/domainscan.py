#!/usr/bin/env python3
# coding:utf-8
from nemo.common.utils.iputils import check_ip_or_domain

from .ipdomain import IpDomain
from .subdomain import SubDmain
from .taskbase import TaskBase
from .webtitle import WebTitle
from .whatweb import WhatWeb


class DomainScan(TaskBase):
    '''域名扫描综合任务
    参数：options
        {   
            'target':   [ip1/domain,ip2/domain,ip3/domain...],domain列表
            'org_id':   id,target关联的组织机构ID
            'subdomain':True/False，是否扫描子域名
            'webtitle': True/False，是否读取网站标题
            'fofasearch':   True/False，是否调用fofa
            'portscan': True/False，对域名扫描结果是否生成portscan任务
            'networkscan':True/False, 对域名结果的IP是否生成portscan任务
            'whatweb':  True/False,对域名是否调用whatweb
        }
    任务结果：
        保存为domain资产的格式
        {'domain': 'www.sgcc.com.cn', 'CNAME': [], 'A': ['210.77.176.16'],'title':['aaa','bbb']}, 
    注意：
        fofasearch、portscan不由DomainScan启动，由上一级调用者进行启动
    '''

    def __init__(self):
        super().__init__()
        # 任务名称
        self.task_name = 'domainscan'
        # 任务描述
        self.task_description = '域名扫描综合任务'
        # 默认参数
        self.source = 'domainscan'
        self.subdomain = True
        self.webtitle = True
        self.whatweb = False

    def prepare(self, options):
        '''解析参数
        '''
        self.org_id = self.get_option('org_id', options, self.org_id)
        self.webtitle = self.get_option('webtitle', options, self.webtitle)
        self.subdomain = self.get_option('subdomain', options, self.subdomain)
        self.whatweb = self.get_option('whatweb', options, self.whatweb)
        self.target = options['target']

    def execute(self):
        '''执行域名扫描
        '''
        # 获取当前域名的IP
        ipdomain = IpDomain()
        domain_target = []
        # 筛选出域名目标
        for host in self.target:
            if not check_ip_or_domain(host):
                domain_target.append({'domain': host})
        # 解析域名IP
        domain_result_list = ipdomain.execute(domain_target)
        # 子域名查询
        if self.subdomain:
            subdomain = SubDmain()
            sub_domain_list = subdomain.execute(self.target)
            domain_result_list.extend(ipdomain.execute(sub_domain_list))
        # 获取域名的title
        if self.webtitle:
            webtitle = WebTitle()
            webtitle.execute_domain(domain_result_list)
        # whatweb
        if self.whatweb:
            whatweb = WhatWeb()
            whatweb.execute(domain_result_list)

        return domain_result_list

    def run(self, options):
        '''执行任务
        '''
        self.prepare(options)
        domain_list = self.execute()
        # 保存结果
        result = self.save_domain(domain_list)
        result['status'] = 'success'

        return result
