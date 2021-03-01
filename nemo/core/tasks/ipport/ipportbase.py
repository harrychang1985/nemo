#!/usr/bin/env python3
# coding:utf-8
import traceback

from nemo.common.utils.config import load_config
from nemo.common.utils.loggerutils import logger
from nemo.core.tasks.taskbase import TaskBase


class IPPortBase(TaskBase):
    '''IP端口扫描基础类
    因此参数格式遵循nmap调用格式
    参数:options  
            {   
                'target':   [ip1,ip2,ip3...],ip列表（nmap格式）
                'port':     '1-65535'/'--top-ports 1000',nmap能识别的端口格式
                'org_id':   id,target关联的组织机构ID
                'rate':     1000,扫描速率
                'ping':     True/False，是否PING
                'tech':     '-sT'/'-sS'/'-sV'，扫描技术
                'exclude':  'host1,host2'，要排除的ip地址
            }
    任务结果:
        保存为ip资产格式的列表：
        [{'ip':'192.168.1.1','status':'alive','port':[{'port':80,'service':'http','banner':'ngix'},...]},...]
    '''

    def __init__(self):
        super().__init__()

        # 任务名称
        self.task_name = 'ipportbase'
        # 任务描述
        self.task_description = '端口扫描'
        # 参数
        self.source = 'ipportbase'
        self.result_attr_keys = ('service', 'banner')
        # 默认的参数
        config_datajson = load_config()
        self.port = config_datajson['nmap']['port']
        self.rate = config_datajson['nmap']['rate']
        self.tech = config_datajson['nmap']['tech']
        self.ping = config_datajson['nmap']['ping']
        self.nmap_bin = config_datajson['nmap']['nmap_bin']
        self.masscan_bin = config_datajson['nmap']['masscan_bin']
        self.exclude = None

    def execute_scan(self, target, port):
        '''对指定IP和端口进行扫描
        由继承类实现
        '''

    def prepare(self, options):
        '''解析参数
        '''
        self.target = options['target']
        self.port = self.get_option('port', options, self.port)
        if not self.port:
            self.port = '--top-ports 1000'
        self.rate = self.get_option('rate', options, self.rate)
        self.tech = self.get_option('tech', options, self.tech)
        self.ping = self.get_option('ping', options, self.ping)
        self.org_id = self.get_option('org_id', options, self.org_id)
        self.exclude = self.get_option('exclude', options, self.exclude)

    def execute(self):
        '''调用执行扫描任务
        '''
        ip_ports = []
        try:
            ip_ports.extend(self.execute_scan(self.target, self.port))
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error('{} scan target:{},port:{}'.format(self.task_name, self.target, self.port))

        return ip_ports

    def run(self, options):
        '''执行任务
        '''
        try:
            self.prepare(options)
            ip_ports = self.execute()
            result = self.save_ip(ip_ports)
            result['status'] = 'success'

            return result
        except Exception as e:
            logger.error(traceback.format_exc())
            return {'status': 'fail', 'msg': str(e)}
