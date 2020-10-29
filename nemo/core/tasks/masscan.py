#!/usr/bin/env python3
# coding:utf-8
import os
import re
import traceback
import subprocess
from tempfile import NamedTemporaryFile

from nemo.common.utils.config import load_config
from nemo.common.utils.loggerutils import logger
from nemo.common.utils.parseservice import ParsePortService

from .taskbase import TaskBase


class Masscan(TaskBase):
    '''调用masscan的扫描任务
    通过masscan执行扫描任务
    参数:options  
            {   
                'target':   [ip1,ip2,ip3...],ip列表（nmap格式）
                'port':     '1-65535'/'--top-ports 1000',nmap能识别的端口格式
                'org_id':   id,target关联的组织机构ID
                'rate':     3000,扫描速率
                'ping':     True/False，是否PING
            }
    任务结果:
        保存为ip资产格式的列表：
        [{'ip':'192.168.1.1','status':'alive','port':[{'port':80,'service':'http','banner':'ngix'},...]},...]
    '''

    def __init__(self):
        super().__init__()

        # 任务名称
        self.task_name = 'masscan'
        # 任务描述
        self.task_description = '调用masscan进行端口扫描'
        # 参数
        self.org_id = None
        self.source = 'portscan'
        # 默认的参数
        self.target = []
        config_datajson = load_config()
        self.port = config_datajson['nmap']['port']
        self.rate = config_datajson['nmap']['rate']
        self.ping = config_datajson['nmap']['ping']
        self.masscan_bin = config_datajson['nmap']['masscan_bin']

    def __parse_masscan_output_file(self, output_results):
        '''解析masscan的扫描结果
        '''
        results = []
        port_service = ParsePortService()
        try:
            for line in output_results.split(os.linesep):
                if line.strip() == '':
                    continue
                if line.startswith('#'):
                    continue
                data = line.strip().split(' ')
                if data[0] == 'open' and data[1] == 'tcp':
                    ip = data[3].strip()
                    port = data[2].strip()
                    results.append({'ip': ip, 'status': 'alive', 'port': [
                                   {'port': port, 'status': 'open', 'service': port_service.get_service(port)}]})
        except Exception as e:
            logger.error(traceback.format_exc())

        return results

    def __get_top_ports_by_nmap(self, top_number):
        '''调用nmap获得--top-ports的定义
        '''
        config_datajson = load_config()
        with NamedTemporaryFile('w+t') as f:
            nmap_bin = [config_datajson['nmap']['nmap_bin'], '-v', '-oG', f.name,
                        '--top-ports', str(top_number)]
            # 调用nmap
            child = subprocess.Popen(nmap_bin, stdout=subprocess.PIPE)
            child.wait()
            # 读取结果
            p_re = r'TCP\('+str(top_number)+r';(.+?)\)'
            m = re.findall(p_re, ''.join(f.read()))
            if m:
                return m[0]

        # top 100 port:
        return '7,9,13,21-23,25-26,37,53,79-81,88,106,110-111,113,119,135,139,143-144,179,199,389,427,443-445,465,513-515,543-544,548,554,587,631,646,873,990,993,995,1025-1029,1110,1433,1720,1723,1755,1900,2000-2001,2049,2121,2717,3000,3128,3306,3389,3986,4899,5000,5009,5051,5060,5101,5190,5357,5432,5631,5666,5800,5900,6000-6001,6646,7070,8000,8008-8009,8080-8081,8443,8888,9100,9999-10000,32768,49152-49157'

    def __masscan_scan(self, target, port):
        '''调用masscan对指定IP和端口进行扫描
        '''
        with NamedTemporaryFile('w+t') as tfile_ip, NamedTemporaryFile('w+t') as tfile_output:
            # 将所有目标一次性写入文件中
            tfile_ip.write('\n'.join(target))
            tfile_ip.seek(0)
            masscan_bin = [self.masscan_bin, '-oL',
                           tfile_output.name, '--open', '--rate', str(self.rate)]
            if self.ping:
                masscan_bin.append('--ping')
            # 两种方式：指定端口（包括全端口）和常用top端口（--top-ports 1000）
            # 如果是--top-ports模式，则调用nmap获取top-ports
            masscan_bin.append('-p')
            if port.startswith('--top'):
                masscan_bin.append(self.__get_top_ports_by_nmap(
                    port.split(' ')[1].strip()))
            else:
                masscan_bin.append(port)
            masscan_bin.append('-iL')
            masscan_bin.append(tfile_ip.name)
            # 调用masscan进行扫描
            child = subprocess.Popen(masscan_bin, stdout=subprocess.PIPE)
            child.wait()
            # 解析masscan扫描结果
            result = self.__parse_masscan_output_file(tfile_output.read())

        return result

    def prepare(self, options):
        '''解析参数
        '''
        self.target = options['target']
        self.port = self.get_option('port', options, self.port)
        if not self.port:
            self.port = '--top-ports 1000'
        self.rate = self.get_option('rate', options, self.rate)
        self.ping = self.get_option('ping', options, self.ping)
        self.org_id = self.get_option('org_id', options, self.org_id)

    def execute(self):
        '''调用masscan执行扫描任务
        '''
        ip_ports = []
        try:
            ip_ports = self.__masscan_scan(self.target, self.port)
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error('masscan target:{},port:{}'.format(self.target,self.port))

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
