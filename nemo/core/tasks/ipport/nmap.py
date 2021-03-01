#!/usr/bin/env python3
# coding:utf-8
import os
import re
import subprocess
from tempfile import NamedTemporaryFile

from nemo.common.utils.parseservice import ParsePortService
from .ipportbase import IPPortBase


class Nmap(IPPortBase):
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
        [{'port':'192.168.1.1','status':'alive','port':[{'port':80,'service':'http','banner':'ngix'},...]},...]
    '''

    def __init__(self):
        super().__init__()

        # 任务名称
        self.task_name = 'nmap'
        # 任务描述
        self.task_description = '调用nmap进行端口扫描'
        # 参数
        self.source = 'portscan'

    def __parse_nmap_grepable_file(self, nmap_grepable_file):
        '''解析nmap扫描输出的grepable文件
        '''
        results = []
        service_app = ParsePortService()
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
                        service_custom = service_app.get_service(port)
                        if service_custom and service_custom != 'unknown':
                            service = service_custom
                        ports.append(
                            {'port': port, 'service': service, 'banner': banner})
                results.append({'ip': ip, 'status': 'alive', 'port': ports})

        return results

    def execute_scan(self, target, port):
        '''调用nmap对指定IP和端口进行扫描
        '''
        with  NamedTemporaryFile('w+t') as tfile_ip, NamedTemporaryFile('w+t') as tfile_output:
            # 将所有目标一次性写入文件中
            tfile_ip.write('\n'.join(target))
            tfile_ip.seek(0)
            nmap_bin = [self.nmap_bin, self.tech, '-T4', '-oG', tfile_output.name, '--open',
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
            nmap_bin.append('-iL')
            nmap_bin.append(tfile_ip.name)
            if self.exclude:
                nmap_bin.append('--exclude')
                nmap_bin.append(self.exclude)
            # 调用nmap进行扫描
            child = subprocess.Popen(nmap_bin, stdout=subprocess.PIPE)
            child.wait()
            # 解析nmap扫描结果
            return self.__parse_nmap_grepable_file(tfile_output.read())
