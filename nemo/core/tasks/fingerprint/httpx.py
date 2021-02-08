#!/usr/bin/env python3
# coding:utf-8
import json
import os
import platform
import subprocess
import traceback
from tempfile import NamedTemporaryFile

from nemo.common.utils.loggerutils import logger
from .fingerprintbase import PortFingerBase


class Httpx(PortFingerBase):
    '''调用Httpx的获取CMS的指纹
    参数:options  
            {   
                'target':   [url1,url2,ur3...],url列表可是以doamin或IP:PORT，如www.google.com 或 8.8.8.8:80
                'org_id':   id,target关联的组织机构ID
            }
    任务结果:
        保存为ip或domain资产格式的列表：
        [{'port':'192.168.1.1','port':[{'port':80,'httpx':'xxx,yyy,zzz','source':'httpx'},...]},...]
        [{'domain':'www.google.com,'httpx':['xxx',]},...]
    '''

    def __init__(self):
        super().__init__()

        # 任务名称
        self.task_name = 'httpx'
        # 任务描述
        self.task_description = '调用httpx获取CMS指纹'
        # 参数
        self.source = 'httpx'
        self.result_attr_keys = ('httpx', 'title', 'server')
        self.threads = 5
        # 默认的参数
        self.BIN_PATH = 'nemo/common/thirdparty/httpx'
        self.BIN_FILE = 'httpx_darwin_amd64'
        if platform.system == 'Linux':
            self.BIN_FILE = 'httpx_linux_amd64'

    def fetch_title(self, url):
        '''调用httpx进行探测
        '''
        with NamedTemporaryFile('w+t') as tfile_url, NamedTemporaryFile('w+t') as tfile_output:
            # 将目标写入文件中
            tfile_url.write(url)
            tfile_url.seek(0)
            httpx_bin = [os.path.join(self.BIN_PATH, self.BIN_FILE), '-l', tfile_url.name,
                         '-H', '\'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063\'',
                         '-status-code', '-title', '-web-server','-follow-redirects', '-no-color', '-content-length',
                         '-content-type', '-silent', '-json', '-o', tfile_output.name]
            # 调用httpx进行扫描
            try:
                child = subprocess.Popen(httpx_bin, stdout=subprocess.PIPE)
                child.wait()
                result = tfile_output.read()
            except Exception as e2:
                logger.error(traceback.format_exc())
                logger.error('{} url:{}'.format(self.source, url))
                result = None
                print(e2)

            return result

    def parse_result(self, content):
        '''从httpx的返回中提取title和banner
        '''
        result = {}
        if content and len(content) > 0:
            try:
                json_data = json.loads(content)
                if 'title' in json_data and json_data['title']:
                    result.update(title=json_data['title'])
                if 'webserver' in json_data and json_data['webserver']:
                    result.update(server=json_data['webserver'])
                if 'status-code' in json_data and json_data['status-code']:
                    result.update(status=json_data['status-code'])

                result.update(httpx=str(content))
            except Exception as e:
                logger.error(traceback.format_exc())
                logger.error('{} content:{}'.format(self.source, content))
                print(e)

        return result
