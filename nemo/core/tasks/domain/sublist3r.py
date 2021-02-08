#!/usr/bin/env python3
# coding:utf-8

from nemo.common.thirdparty.Sublist3r import sublist3r
from .domainbase import DomainBase


class Sublist3r(DomainBase):
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
        self.task_name = 'sublist3r'
        self.task_description = 'sublist3r子域名信息收集'
        self.source = 'sublist3r'
        # sublist3r 参数
        self.threads = 5
        self.save_file = False
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

    def fetch_domain(self, domain):
        return sublist3r.main(domain, self.threads, self.save_file,
                              self.ports, self.silent, self.verbose, self.bruteforce, self.engines)
