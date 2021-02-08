#!/usr/bin/env python3
# coding:utf-8
import json
import os
import platform
import subprocess
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

from .pocbase import PocBase


class XRay(PocBase):
    '''调用xray执行验漏洞验证任务
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
        self.task_name = 'xray'
        # 任务描述
        self.task_description = '调用Xray进行漏洞验证'
        # 参数
        self.source = 'xray'
        self.POC_FILE_EXT = '.yml'
        self.BIN_PATH = 'nemo/common/thirdparty/xray'
        self.POC_PATH = 'nemo/common/thirdparty/xray/xray/pocs'
        self.BIN_FILE = 'xray_darwin_amd64'
        if platform.system == 'Linux':
            self.BIN_FILE = 'xray_linux_amd64'

    def __parse_xray_json_file(self, json_data):
        '''解析XRay的验证结果
        '''
        if not json_data:
            return []

        vul_results = []
        for data in json.loads(json_data):
            vul = {'poc_file': self.poc_file,
                   'source': 'xray', 'url': data['target']['url']}
            pr = urlparse(vul['url'])
            vul.update(target=pr.hostname)
            if 'detail' in data and 'snapshot' in data['detail']:
                if len(str(data['detail']['snapshot'])) > 2000:
                    vul['extra'] = str(data['detail']['snapshot'])[:2000] + '...'
                else:
                    vul['extra'] = str(data['detail']['snapshot'])

            vul_results.append(vul)

        return vul_results

    def execute_verify(self):
        '''调用xray验证漏洞
        '''
        with NamedTemporaryFile('w+t') as tfile_ip, NamedTemporaryFile('w+t') as tfile_output:
            # 生成临时文件名称
            json_output_tmp_name = tfile_output.name + ".xray.json"
            tfile_output.close()
            # 将所有目标一次性写入文件中
            tfile_ip.write(os.linesep.join(self.target))
            tfile_ip.seek(0)
            xray_bin = [os.path.join(self.BIN_PATH, self.BIN_FILE), '--log-level', 'error', 'webscan', '--plugins',
                        'phantasm', '--poc', os.path.join(self.POC_PATH, self.poc_file), '--url-file', tfile_ip.name,
                        '--json-output', json_output_tmp_name]
            # 调用xray进行扫描
            child = subprocess.Popen(xray_bin)  # ,stdout=subprocess.PIPE)
            child.wait()
            # 读取结果、删除临时文件
            try:
                with open(json_output_tmp_name) as f:
                    json_output_data = f.read()
                os.remove(json_output_tmp_name)
            except FileNotFoundError:
                json_output_data = ''
            # 解析xray扫描结果
            return self.__parse_xray_json_file(json_output_data)
