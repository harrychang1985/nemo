#!/usr/bin/env python3
# coding:utf-8
import traceback
import os
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse
from pocsuite3.api import init_pocsuite
from pocsuite3.api import start_pocsuite
from pocsuite3.api import get_results

from nemo.common.utils.loggerutils import logger
from nemo.core.database.vulnerability import Vulnerability

from .taskbase import TaskBase


class Pocsuite3(TaskBase):
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
        self.task_name = 'pocsuite3_verify'
        # 任务描述
        self.task_description = '调用Pocsuit3进行漏洞验证'
        # 参数
        self.source = 'pocsuite3'
        self.POC_PATH = 'nemo/common/thirdparty/some_pocsuite'
        self.THREADS = 5
        # 默认的参数
        self.target = []
        self.poc_file = ''

    def __pocsuite3_scanner(self,_poc_config):
        '''Pocsuite3 API调用
        '''
        init_pocsuite(_poc_config)
        start_pocsuite()
        result = get_results()
        return result

    def __pocsuite3_verify(self):
        '''调用pocsuite3进行漏洞验证
        '''
        with  NamedTemporaryFile('w+t') as tfile_ip:
            # 将所有目标一次性写入文件中
            tfile_ip.write(os.linesep.join(self.target))
            tfile_ip.seek(0)
            _poc_config = {
                'url_file': tfile_ip.name,
                'poc': os.path.join(self.POC_PATH,self.poc_file),
                'threads': self.THREADS,
                'quiet': False,
                'random_agent': True,
            }
            results = self.__pocsuite3_scanner(_poc_config)

            vul_results = []
            for data in results:
                if data.status == 'success':
                    pr = urlparse(data.url)
                    r = {'source': self.source,'target': pr.hostname, 'poc_file': self.poc_file}
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


    def prepare(self, options):
        '''解析参数
        '''
        self.target = options['target']
        self.poc_file = options['poc_file']

    def execute(self):
        '''执行任务
        '''
        vul_results = []
        try:
            vul_results.extend(self.__pocsuite3_verify())
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error('pocsuite3 verify target:{}'.format(self.target))

        return vul_results

    def check_poc_exist(self, poc_file):
        '''检查POC文件存在
        '''
        full_path_poc_file = os.path.join(self.POC_PATH, poc_file)
        if os.path.exists(full_path_poc_file) and os.path.isfile(full_path_poc_file):
            return True

        return False

    def run(self, options):
        '''执行任务
        '''
        try:
            self.prepare(options)
            vul_results = self.execute()
            result ={'status': 'success', 'vulnerability': 0}
            vul_app = Vulnerability()
            for v in vul_results:
                if vul_app.save_and_update(v):
                    result['vulnerability'] += 1

            return result
        except Exception as e:
            logger.error(traceback.format_exc())
            return {'status': 'fail', 'msg': str(e)}

    def load_poc_files(self):
        '''获取poc文件列表
        '''
        poc_files = []
        for name in os.listdir(self.POC_PATH):
            if os.path.isfile(os.path.join(self.POC_PATH, name)) and os.path.splitext(name)[-1] == ".py":
                poc_files.append(name)

        return sorted(poc_files)