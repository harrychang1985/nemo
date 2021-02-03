#!/usr/bin/env python3
# coding:utf-8
import traceback
import os
import json
import platform
import subprocess
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

from nemo.common.utils.loggerutils import logger
from nemo.core.database.vulnerability import Vulnerability

from .taskbase import TaskBase


class XRay(TaskBase):
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
        self.task_name = 'xray_verify'
        # 任务描述
        self.task_description = '调用Xray进行漏洞验证'
        # 参数
        self.source = 'xray'
        self.BIN_PATH  = 'nemo/common/thirdparty/xray'
        self.POC_PATH = 'nemo/common/thirdparty/xray/xray/pocs'
        self.BIN_FILE = 'xray_darwin_amd64'
        if platform.system == 'Linux':
            self.BIN_FILE = 'xray_linux_amd64'
        # 默认的参数
        self.target = []
        self.poc_file = ''


    def __parse_xray_json_file(self, json_data):
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

    def __xray_verify(self):
        '''调用xray验证漏洞
        '''
        with NamedTemporaryFile('w+t') as tfile_ip, NamedTemporaryFile('w+t') as tfile_output:
            # 生成临时文件名称
            json_output_tmp_name = tfile_output.name + ".xray.json"
            tfile_output.close()
            # 将所有目标一次性写入文件中
            tfile_ip.write(os.linesep.join(self.target))
            tfile_ip.seek(0)
            xray_bin = [os.path.join(self.BIN_PATH, self.BIN_FILE), '--log-level', 'error', 'webscan', '--plugins', 'phantasm',
                        '--poc', os.path.join(self.POC_PATH, self.poc_file), '--url-file', tfile_ip.name,
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


    def prepare(self, options):
        '''解析参数
        '''
        self.target = options['target']
        self.poc_file = options['poc_file']

    def check_poc_exist(self, poc_file):
        '''检查POC文件存在
        '''
        full_path_poc_file = os.path.join(self.POC_PATH, poc_file)
        if os.path.exists(full_path_poc_file) and os.path.isfile(full_path_poc_file):
            return True

        return False


    def execute(self):
        '''执行任务
        '''
        vul_results = []
        try:
            vul_results.extend(self.__xray_verify())
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error('xray verify target:{}'.format(self.target))

        return vul_results

    def run(self, options):
        '''执行任务
        '''
        try:
            self.prepare(options)
            vul_results = self.execute()
            result ={'status':'success','vulnerability':0}
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
            if os.path.isfile(os.path.join(self.POC_PATH, name)) and os.path.splitext(name)[-1] == ".yml":
                poc_files.append(name)

        return sorted(poc_files)