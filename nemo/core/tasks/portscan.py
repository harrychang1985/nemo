#!/usr/bin/env python3
# coding:utf-8
from .taskbase import TaskBase
from .nmap import Nmap
from .ipdomain import IpDomain
from .webtitle import WebTitle
from .whatweb import WhatWeb
from nemo.common.utils.iputils import check_ip_or_domain


class PortScan(TaskBase):
    '''端口扫描综合任务
    参数：options
        {   
            'target':   [ip1,ip2,ip3...],ip列表（nmap格式）
            'port':     '1-65535'或者'--top-ports 1000',nmap能识别的端口格式
            'org_id':   id,target关联的组织机构ID
            'rate':     1000,扫描速率
            'ping':     True/False，是否PING
            'tech':     '-sT'/'-sS'/'-sV'，扫描技术
            'webtitle': True/False，是否读取网站IP地址
            'iplocation':   True/False，是否获取IP归属地
            'whatweb':      True/False,是否调用whatweb
        }
    '''

    def __init__(self):
        super().__init__()
        # 任务名称
        self.task_name = 'portscan'
        # 任务描述
        self.task_description = '端口扫描综合任务'
        # 默认参数：
        self.source = 'portscan'
        self.result_attr_keys = ('service', 'banner', 'title', 'whatweb','server')
        self.webtitle = False
        self.iplocation = False
        self.whatweb = False

    def prepare(self, options):
        '''解析参数
        '''
        self.org_id = self.get_option('org_id', options, self.org_id)
        self.webtitle = self.get_option('webtitle', options, self.webtitle)
        self.iplocation = self.get_option(
            'iplocation', options, self.iplocation)
        self.whatweb = self.get_option('whatweb', options, self.whatweb)
        # 将域名转换为IP
        target_ip = []
        ipdomain = IpDomain()
        for t in options['target']:
            host = t.strip()
            if check_ip_or_domain(host):
                target_ip.append(host)
            else:
                # 获取域名IP信息
                iplist = ipdomain.fetch_domain_ip(host)
                # 保存到数据库
                self.save_domain([iplist, ])
                # 如果没有CDN，则将ip地址加入到扫描目标地址
                if len(iplist['CNAME']) == 0 and len(iplist['A']) > 0:
                    target_ip.extend(iplist['A'])

        options['target'] = target_ip

    def run(self, options):
        '''执行端口扫描任务
        '''
        self.prepare(options)
        # nmap扫描
        nmap_app = Nmap()
        nmap_app.prepare(options)
        ip_ports = nmap_app.execute()
        # IP归属地
        if self.iplocation:
            ipdomain_app = IpDomain()
            ipdomain_app.execute_iplocation(ip_ports)
        # 端口的title
        if self.webtitle:
            webtitle_app = WebTitle()
            webtitle_app.execute_ip(ip_ports)
        # 是否调用whatweb
        if self.whatweb:
            whatweb_app = WhatWeb()
            whatweb_app.execute(ip_ports)

        # 保存数据
        result = self.save_ip(ip_ports)
        result['status'] = 'success'

        return result
