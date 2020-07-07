#!/usr/bin/env python3
# coding:utf-8
from multiprocessing.dummy import Pool
import re
import traceback
import subprocess
from tempfile import NamedTemporaryFile

from nemo.common.utils.config import load_config
from nemo.common.utils.iputils import check_ip_or_domain
from nemo.common.utils.loggerutils import logger
from .taskbase import TaskBase


class WhatWeb(TaskBase):
    '''调用WhatWeb的获取CMS的指纹
    参数:options  
            {   
                'target':   [url1,url2,ur3...],url列表可是以doamin或IP:PORT，如www.google.com 或 8.8.8.8:80
                'org_id':   id,target关联的组织机构ID
            }
    任务结果:
        保存为ip或domain资产格式的列表：
        [{'ip':'192.168.1.1','port':[{'port':80,'whatweb':'xxx,yyy,zzz','source':'whatweb'},...]},...]
        [{'domain':'www.google.com,'whatweb':['xxx',]},...]
    '''

    def __init__(self):
        super().__init__()

        # 任务名称
        self.task_name = 'whatweb'
        # 任务描述
        self.task_description = '调用whatweb获取CMS指纹'
        # 参数
        self.org_id = None
        self.source = 'whatweb'
        self.result_attr_keys = ('whatweb', 'title', 'server')
        self.threads = 5
        self.whatweb_threads = 5
        # 默认的参数
        self.target = []
        config_jsondata = load_config()
        self.whatweb_bin = config_jsondata['whatweb']['bin']

    def __exe_whatweb(self, url):
        '''调用nmap对指定IP和端口进行扫描
        '''
        with NamedTemporaryFile('w+t') as tfile_output:
            whatweb_bin = [self.whatweb_bin, '-q', '--color=never', '--log-brief', tfile_output.name, '--max-threads', str(self.whatweb_threads),
                           '--open-timeout', str(5), '--read-timeou', str(10),
                           '-U=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
                           url]
            # 调用whatweb进行扫描
            try:
                child = subprocess.Popen(whatweb_bin, stdout=subprocess.PIPE)
                child.wait()
                result = tfile_output.read()
                if result.startswith('ERROR'):
                    result = None
            except Exception as e2:
                logger.error(traceback.format_exc())
                logger.error('whatweb url:{}'.format(url))
                result = None
                print(e2)

            return result

    def prepare(self, options):
        '''解析参数
        '''
        # 将 [url1,url2,ur3...]格式处理为ip和domain表的格式
        target_list = []
        for t in options['target']:
            u = t.split(':')
            port = u[1] if len(u) == 2 else 80
            # IP地址
            if check_ip_or_domain(u[0]):
                for i in target_list:
                    if 'ip' in i and 'port' in i and i['ip'] == u[0]:
                        i['port'].append({'port': port})
                        break
                else:
                    target_list.append({'ip': u[0], 'port': [{'port': port}]})
            else:
                # 域名
                for d in target_list:
                    if 'domain' in d and d['domain'] == t:
                        break
                else:
                    target_list.append({'domain': t})

        self.target = target_list
        self.org_id = self.get_option('org_id', options, self.org_id)

    def __execute(self, target):
        '''ip参数执行线程
        '''
        # IP:PORT
        if 'ip' in target and 'port' in target:
            for port in target['port']:
                content = self.__exe_whatweb(
                    '{}:{}'.format(target['ip'], port['port']))
                if content:
                    port.update(self.__parse_whatweb(content))

        # DOMAIN
        elif 'domain' in target:
            content = self.__exe_whatweb(
                '{}'.format(target['domain']))
            if content:
                result = self.__parse_whatweb(content)
                if 'whatweb' not in target:
                    target['whatweb'] = []
                target['whatweb'].append(content)
                if 'title' in result:
                    if 'title' not in target:
                        target['title'] = []
                    target['title'].append(result['title'])
                if 'server' in result:
                    if 'server' not in target:
                        target['server'] = []
                    target['server'].append(result['server'])

    def __parse_whatweb(self, content):
        '''从whatweb的返回中提取title和bannr
        '''
        keys = {'Title': 'title', 'HTTPServer': 'server'}
        p_title = r'{}\[(.*?)\]'
        result = {}
        for k, v in keys.items():
            m = re.findall(p_title.format(k), content)
            if m:
                result[v] = ','.join(list(set(m)))

        result.update(whatweb=content)

        return result

    def execute(self, target_list):
        '''调用what执行扫描任务
        '''
        pool = Pool(self.threads)
        pool.map(self.__execute, target_list)
        pool.close()
        pool.join()

        return target_list

    def run(self, options):
        '''执行任务
        '''
        try:
            self.prepare(options)
            self.execute(self.target)
            result = self.save_ip(self.target)
            result.update(self.save_domain(self.target))
            result['status'] = 'success'

            return result
        except Exception as e:
            logger.error(traceback.format_exc())
            return {'status': 'fail', 'msg': str(e)}
