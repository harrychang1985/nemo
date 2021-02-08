#!/usr/bin/env python3
# coding:utf-8
import os
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

from pocsuite3.api import get_results
from pocsuite3.api import init_pocsuite
from pocsuite3.api import start_pocsuite

from .pocbase import PocBase


class Pocsuite3(PocBase):
    '''调用pocsuite3执行验漏洞验证任务
    参数:options
            {   
                'target':   [ip1,ip2,ip3...],ip或domain列表）
                'poc_file': 调用的poc文件
            }
    任务结果:
        保存为vulnerability格式的列表：
        [{'target':1.2.3.4,'url':'127.0.0.1:7001','poc_file':'weblogic_console_all.py','source':'pocsuit3','extra':'xxx'},...]
    '''

    def __init__(self):
        super().__init__()

        # 任务名称
        self.task_name = 'pocsuite3'
        # 任务描述
        self.task_description = '调用Pocsuit3进行漏洞验证'
        # 参数
        self.source = 'pocsuite3'
        self.POC_PATH = 'nemo/common/thirdparty/some_pocsuite'
        self.POC_FILE_EXT = '.py'
        self.THREADS = 5

    def __pocsuite3_scanner(self, _poc_config):
        '''Pocsuite3 API调用
        '''
        init_pocsuite(_poc_config)
        start_pocsuite()
        result = get_results()

        return result

    def __parse_pocsuite3_result(self, results):
        vul_results = []
        for data in results:
            if data.status == 'success':
                pr = urlparse(data.url)
                r = {'source': self.source, 'target': pr.hostname, 'poc_file': self.poc_file}
                if 'VerifyInfo' in data.result and 'URL' in data.result['VerifyInfo']:
                    r['url'] = data.result['VerifyInfo']['URL']
                else:
                    r['url'] = data.url
                r['extra'] = ''
                if 'extra' in data.result:
                    if len(str(data.result['extra'])) > 2000:
                        r['extra'] = str(data.result['extra'])[:2000] + '...'
                    else:
                        r['extra'] = str(data.result['extra'])

                vul_results.append(r)

        return vul_results

    def execute_verify(self):
        '''调用pocsuite3进行漏洞验证
        '''
        with  NamedTemporaryFile('w+t') as tfile_ip:
            # 将所有目标一次性写入文件中
            tfile_ip.write(os.linesep.join(self.target))
            tfile_ip.seek(0)
            _poc_config = {
                'url_file': tfile_ip.name,
                'poc': os.path.join(self.POC_PATH, self.poc_file),
                'threads': self.THREADS,
                'quiet': False,
                'random_agent': True,
            }
            results = self.__pocsuite3_scanner(_poc_config)

            return self.__parse_pocsuite3_result(results)
