#!/usr/bin/env python3
# coding:utf-8

from nemo.common.thirdparty.JSFinder import JSFinder
from .domainbase import DomainBase


class JSFinderDomain(DomainBase):
    '''子域名信息收集，使用JSFinder从js文件中获取子域名信息
    参数：options
            {
                'target':   ['domain',...],domain列表
                'org_id':   域名所属的组织
                'deep_mode':    True/False，是否深度爬取二级页面的js文件
            }
    任务结果：
        保存为domain资产的格式
        {'domain': 'www.google.com', 'CNAME': [], 'A': ['8.8.8.8']}, 
        {'domain': 'dns.google.com', 'CNAME': [], 'A': ['9.9.9.9']}]
    '''

    def __init__(self):
        super().__init__()
        self.task_name = 'JSFinder'
        self.task_description = 'JSFinder子域名信息收集'
        self.source = 'jsfinder'
        self.verbose = True
        self.deep_mode = True

    def __parse_domain_from_urls(self, urls, domian):
        '''从urls提取子域名
        '''
        if not urls:
            return None
        if self.verbose:
            print("Find " + str(len(urls)) + " URL:")
            for url in urls:
                print(url)
        subdomains = JSFinder.find_subdomain(urls, domian)
        if self.verbose:
            print("\nFind " + str(len(subdomains)) + " Subdomain:")
            for subdomain in subdomains:
                print(subdomain)

        return subdomains

    def fetch_domain(self, domain):
        '''获取子域名信息
        '''
        domain_results = set()
        for schema in ['http', 'https']:
            url = '{}://{}'.format(schema, domain)
            if self.deep_mode:
                urls = JSFinder.find_by_url_deep(url)
            else:
                urls = JSFinder.find_by_url(url)
            subdomains = self.__parse_domain_from_urls(urls, url)
            if subdomains:
                domain_results.update(subdomains)

        return list(domain_results)
