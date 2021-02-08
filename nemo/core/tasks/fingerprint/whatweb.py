#!/usr/bin/env python3
# coding:utf-8
import re
import subprocess
import traceback
from tempfile import NamedTemporaryFile

from nemo.common.utils.config import load_config
from nemo.common.utils.loggerutils import logger
from .fingerprintbase import PortFingerBase


class WhatWeb(PortFingerBase):
    '''调用WhatWeb的获取CMS的指纹
    参数:options  
            {   
                'target':   [url1,url2,ur3...],url列表可是以doamin或IP:PORT，如www.google.com 或 8.8.8.8:80
                'org_id':   id,target关联的组织机构ID
            }
    任务结果:
        保存为ip或domain资产格式的列表：
        [{'port':'192.168.1.1','port':[{'port':80,'whatweb':'xxx,yyy,zzz','source':'whatweb'},...]},...]
        [{'domain':'www.google.com,'whatweb':['xxx',]},...]
    '''

    def __init__(self):
        super().__init__()

        # 任务名称
        self.task_name = 'whatweb'
        # 任务描述
        self.task_description = '调用whatweb获取CMS指纹'
        # 参数
        self.source = 'whatweb'
        self.result_attr_keys = ('whatweb', 'title', 'server')
        self.threads = 5
        self.whatweb_threads = 5
        # 默认的参数
        config_jsondata = load_config()
        self.whatweb_bin = config_jsondata['whatweb']['bin']

    def fetch_title(self, url):
        '''调用whatweb获取标题
        '''
        with NamedTemporaryFile('w+t') as tfile_url, NamedTemporaryFile('w+t') as tfile_output:
            # 将目标写入文件中
            tfile_url.write(url)
            tfile_url.seek(0)
            whatweb_bin = [self.whatweb_bin, '-q', '--color=never', '--log-brief', tfile_output.name, '--max-threads',
                           str(self.whatweb_threads), '--open-timeout', str(5), '--read-timeout', str(10),
                           '-U=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063',
                           '--input-file', tfile_url.name]
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

    def parse_result(self, content):
        '''从whatweb的返回中提取title和banner
        '''
        keys = {'Title': 'title', 'HTTPServer': 'server'}
        p_title = r'{}\[(.*?)\]'
        result = {}
        for k, v in keys.items():
            m = re.findall(p_title.format(k), content)
            if m:
                result[v] = ','.join(list(set(m)))

        status_code = r'\[(\d{3}) .+?\]'
        m = re.findall(status_code, content)
        if m:
            result['status'] = m[0]

        result.update(whatweb=content)
        return result

class TestClass():
    def test_whatweb(self):
        options = {'target': ['www.baidu.com']}
        app = WhatWeb()
        app.run(options)
        print(app.target)
        assert len(app.target[0]['title']) > 0
