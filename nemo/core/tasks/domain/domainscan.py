#!/usr/bin/env python3
# coding:utf-8

from nemo.common.utils.iputils import check_ip_or_domain
from nemo.core.tasks.fingerprint.httpx import Httpx
from nemo.core.tasks.fingerprint.webtitle import WebTitle
from nemo.core.tasks.fingerprint.whatweb import WhatWeb
from nemo.core.tasks.taskbase import TaskBase

from .ipdomain import IpDomain
from .jsfinderdomain import JSFinderDomain
from .subdomainbrute import SubDmainBrute
from .subfinder import Subfinder
from .sublist3r import Sublist3r


class DomainScan(TaskBase):
    '''域名扫描综合任务
    参数：options
        {   
            'target':   [ip1/domain,ip2/domain,ip3/domain...],domain列表
            'org_id':   id,target关联的组织机构ID
            'subdomain':True/False，是否扫描子域名(Sublist3r）
            'subdomainbrute': True/False，是否进行子域名爆破
            'fofasearch':   True/False，是否调用fofa
            'portscan': True/False，对域名扫描结果是否生成portscan任务
            'networkscan':True/False, 对域名结果的IP是否生成portscan任务
            'whatweb':  True/False,对域名是否调用whatweb
            'httpx':  True/False,对域名是否调用httpx,
            'jsfinder:  True/False,JSFinder
            'subfinder: True/False，subfinder
        }
    任务结果：
        保存为domain资产的格式
        {'domain': 'www.google.com', 'CNAME': [], 'A': ['8.8.8.8'],'title':['aaa','bbb']}, 
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
        self.subdomain = False
        self.whatweb = False
        self.httpx = False
        self.subdomainbrute = False
        self.jsfinder = False
        self.subfinder = False

    def prepare(self, options):
        '''解析参数
        '''
        self.org_id = self.get_option('org_id', options, self.org_id)
        self.subdomain = self.get_option('subdomain', options, self.subdomain)
        self.subdomainbrute = self.get_option('subdomainbrute', options, self.subdomainbrute)
        self.whatweb = self.get_option('whatweb', options, self.whatweb)
        self.httpx = self.get_option('httpx', options, self.httpx)
        self.jsfinder = self.get_option('jsfinder', options, self.jsfinder)
        self.subfinder = self.get_option('subfinder', options, self.subfinder)

        self.target = options['target']

    def execute(self):
        '''执行域名扫描
        '''
        domain_target = []
        # 筛选出域名目标
        for host in self.target:
            if not check_ip_or_domain(host):
                domain_target.append(host)
        # 采用set去除发现的重复域名
        domain_result_set = set()
        domain_result_set.update(domain_target)
        # sublist3r
        if self.subdomain:
            subdomain = Sublist3r()
            domain_result_set.update([d['domain'] for d in subdomain.execute(domain_target)])
        # 子域名爆破
        if self.subdomainbrute:
            subdomainbrute = SubDmainBrute()
            domain_result_set.update([d['domain'] for d in subdomainbrute.execute(domain_target)])
        # subfinder
        if self.subfinder:
            subfinder = Subfinder()
            domain_result_set.update([d['domain'] for d in subfinder.execute(domain_target)])
        # jsfinder
        if self.jsfinder:
            jsfinder = JSFinderDomain()
            domain_result_set.update([d['domain'] for d in jsfinder.execute(domain_target)])

        domain_result_list = []
        for host in domain_result_set:
            if not check_ip_or_domain(host):
                domain_result_list.append({'domain': host})
        # 获取域名的IP
        ipdomain = IpDomain()
        ipdomain.execute(domain_result_list)
        # 去除无法解析到IP的域名
        domain_result_valid_list = []
        for domain_resovled in domain_result_list:
            if domain_resovled['A'] or domain_resovled['CNAME']:
                domain_result_valid_list.append(domain_resovled)
        # whatweb
        if self.whatweb:
            whatweb = WhatWeb()
            whatweb.execute(domain_result_valid_list)
        # httpx
        if self.httpx:
            httpx_app = Httpx()
            httpx_app.execute(domain_result_valid_list)

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


class TestClass():
    def test_doaminscan(self):
        options = {'target': ['10086.cn'], 'subdomain': True, 'subdomainbrute': False, 'jsfinder': True,
                   'subfinder': True,'whatweb': True, 'httpx': True}
        app = DomainScan()
        app.prepare(options)
        domain_list = app.execute()
        print(domain_list)
        assert len(domain_list) > 0
