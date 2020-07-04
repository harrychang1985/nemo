#!/usr/bin/env python3
# coding:utf-8
import shodan

from instance.config import APIConfig
from nemo.common.utils.iputils import check_ip_or_domain, parse_ip

from .taskbase import TaskBase


class Shodan(TaskBase):
    '''调用Shodan API接口进行资产收集
    支持ip与域名两种方式
    参数:options  
            {   
                'target':   [ip/domain,ip/domain...]
                'org_id':   id,target关联的组织机构ID
            }
    任务结果:
        保存为ip或domain资产格式的列表：
        {'ip': '61.133.196.53', 'status': 'N/A', 'port': [{'port': '80', 'status': 'N/A', 'title': 'xxx', 'server': 'nginx/1.16.0'}]}
        {'domain': 'www.csg.cn', 'A': ['218.19.148.193']}
    '''

    def __init__(self):
        super().__init__()
        # API KEY
        self.key = APIConfig.SHODAN_API_KEY
        # 默认参数
        self.target = []
        self.source = 'shodan'
        self.result_attr_keys = (
            'data', 'server', 'product', 'cpe', 'os')  # 要保存的属性字段

    def __shodan_search(self, target):
        '''查询FOFA
        '''
        api = shodan.Shodan(self.key)
        try:
            host = api.host(target)
            return self.__parse_ip_port(host)
        except Exception as ex:
            print(ex)
            return None

    def __parse_ip_port(self, host):
        '''解析shoadon的host查询结果
        '''
        port_result = []
        for item in host['data']:
            p = {}
            p['port'] = item['port']
            if 'data' in item:
                p['data'] = item['data'].strip()
            if 'product' in item:
                p['product'] = item['product'].strip()
            if 'cpe' in item:
                p['cpe'] = ', '.join(item['cpe'])
            if item['os']:
                p['os'] = item['os'].strip()
            port_result.append(p)

        return {'ip': host['ip_str'], 'port': port_result, 'status': 'N/A'}

    def prepare(self, options):
        '''解析参数
        '''
        for t in options['target']:
            if check_ip_or_domain(t):
                ip_target = parse_ip(t)
                if ip_target and isinstance(ip_target,(tuple,list)):
                    self.target.extend(ip_target)
                else:
                    self.target.append(ip_target)
            else:
                self.target.append(t)
               
        self.org_id = self.get_option('org_id', options, self.org_id)

    def execute(self, target):
        '''查询Shodan
        '''
        ip_port = []
        for t in target:
            # 查询host
            if check_ip_or_domain(t):
                result = self.__shodan_search(t)
                if result:
                    ip_port.append(result)

        return ip_port

    def run(self, options):
        '''执行任务
        '''
        self.prepare(options)
        # 查询API
        ip_port = self.execute(self.target)
        # 保存数据
        result = self.save_ip(ip_port)
        result['status'] = 'success'

        return result
