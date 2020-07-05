#!/usr/bin/env python3
# coding:utf-8
import os
import re
import traceback
import subprocess
from tempfile import NamedTemporaryFile

from nemo.common.utils.config import load_config
from nemo.common.utils.loggerutils import logger

from .taskbase import TaskBase


class Nmap(TaskBase):
    '''调用Nmap的扫描任务
    通过nmap执行扫描任务，因此参数格式遵循nmap调用格式
    参数:options  
            {   
                'target':   [ip1,ip2,ip3...],ip列表（nmap格式）
                'port':     '1-65535'/'--top-ports 1000',nmap能识别的端口格式
                'org_id':   id,target关联的组织机构ID
                'rate':     1000,扫描速率
                'ping':     True/False，是否PING
                'tech':     '-sT'/'-sS'/'-sV'，扫描技术
            }
    任务结果:
        保存为ip资产格式的列表：
        [{'ip':'192.168.1.1','status':'alive','port':[{'port':80,'service':'http','banner':'ngix'},...]},...]
    '''

    def __init__(self):
        super().__init__()

        # 任务名称
        self.task_name = 'nmap'
        # 任务描述
        self.task_description = '调用nmap进行端口扫描'
        # 参数
        self.org_id = None
        self.source = 'portscan'
        self.result_attr_keys = ('service', 'banner')
        # 默认的参数
        self.target = []
        config_datajson = load_config()
        self.port = config_datajson['nmap']['port']
        self.rate = config_datajson['nmap']['rate']
        self.tech = config_datajson['nmap']['tech']
        self.ping = config_datajson['nmap']['ping']
        self.nmap_bin = config_datajson['nmap']['nmap_bin']

    def __parse_nmap_grepable_file(self, nmap_grepable_file):
        '''解析nmap扫描输出的grepable文件
        '''
        results = []
        for line in nmap_grepable_file.split(os.linesep):
            line_str = line.strip()
            if line_str.startswith('#'):
                continue
            if line_str == '':
                continue
            m = re.findall(r'^Host:(.+)Ports:(.+)', line_str)
            if m and len(m[0]) >= 2:
                ip = re.findall(
                    r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', m[0][0])[0]
                ports_info = m[0][1].strip().split(',')
                ports = []
                for pi in ports_info:
                    p = pi.split('/')
                    status = p[1]
                    if status == 'open':
                        port = int(p[0].strip())
                        service = p[4].strip()
                        banner = p[6].strip()
                        ports.append(
                            {'port': port, 'service': service, 'banner': banner, 'status': status})
                results.append({'ip': ip, 'status': 'alive', 'port': ports})

        return results

    def __nmap_scan(self, ip, port):
        '''调用nmap对指定IP和端口进行扫描
        '''
        with NamedTemporaryFile('w+t') as tfile_output:
            nmap_bin = [self.nmap_bin, self.tech, '-T4', '-oG', tfile_output.name,  '--open',
                        '-n', '--randomize-hosts', '--min-rate', str(self.rate)]
            if not self.ping:
                nmap_bin.append('-Pn')
            # 两种方式：指定端口（包括全端口）和常用top端口（--top-ports 1000）
            if port.startswith('--top'):
                nmap_bin.append('--top-ports')
                nmap_bin.append(port.split(' ')[1].strip())
            else:
                nmap_bin.append('-p')
                nmap_bin.append(port)
            nmap_bin.append(ip)
            # 调用nmap进行扫描
            child = subprocess.Popen(nmap_bin, stdout=subprocess.PIPE)
            child.wait()
            # 解析nmap扫描结果
            return self.__parse_nmap_grepable_file(tfile_output.read())

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

    def execute(self):
        '''调用nmap执行扫描任务
        '''
        ip_ports = []
        try:
            for ip in self.target:
                ip_ports.extend(self.__nmap_scan(ip, self.port))
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error('nmap scan target:{},port:{}'.format(self.target,self.port))

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
