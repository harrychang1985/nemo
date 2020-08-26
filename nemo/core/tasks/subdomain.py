#!/usr/bin/env python3
# coding:utf-8

import sublist3r

from .ipdomain import IpDomain
from .taskbase import TaskBase


class SubDmain(TaskBase):
    '''子域名信息收集，使用Sublist3r
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
        self.task_name = 'subdomain'
        self.task_description = '子域名信息收集'
        self.source = 'subdomain'
        # sublist3r 参数
        self.threads = 5
        self.savefile = False
        self.ports = False
        self.silent = False
        self.verbose = False
        #
        self.bruteforce = False
        self.engines = 'baidu,yahoo,bing,netcraft,virustotal,threatcrowd,ssl,passivedns'
        '''
        supported_engines = {'baidu': BaiduEnum,
                         'yahoo': YahooEnum,
                         'google': GoogleEnum,
                         'bing': BingEnum,
                         'ask': AskEnum,
                         'netcraft': NetcraftEnum,
                         'dnsdumpster': DNSdumpster,
                         'virustotal': Virustotal,
                         'threatcrowd': ThreatCrowd,
                         'ssl': CrtSearch,
                         'passivedns': PassiveDNS
                         }
        '''

    def prepare(self, options):
        '''解析参数
        '''
        self.target = options['target']
        self.org_id = self.get_option('org_id',options,self.org_id)

    def execute(self, data):
        '''调用Sublist3r收集子域名
        '''
        domains = set()
        for domain in data:
            domains.update(sublist3r.main(domain, self.threads, self.savefile,
                                          self.ports, self.silent, self.verbose, self.bruteforce, self.engines))
        # 域名结果格式化
        domain_list = []
        for d in domains:
            domain = d.replace(
                'https://', '').replace('http://', '').split(':')[0]
            domain_list.append({'domain': domain})

        return domain_list

    def run(self, options):
        ''' 收集子域名信息
        '''
        self.prepare(options)
        domain_list = self.execute(self.target)
        # 查询域名IP地址
        ipdomain = IpDomain()
        ipdomain.execute(domain_list)
        #print(domain_list)
        # 保存结果：
        result = self.save_domain(domain_list)
        result['status'] = 'success'

        return result
