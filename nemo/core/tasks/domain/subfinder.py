#!/usr/bin/env python3
# coding:utf-8
import os
import platform
import subprocess
import traceback
from tempfile import NamedTemporaryFile

from nemo.common.utils.loggerutils import logger
from .domainbase import DomainBase


class Subfinder(DomainBase):
    '''子域名信息收集，使用subfinder
    参数：options
            {
                'target':   ['domain',...],domain列表
                'org_id':   域名所属的组织
            }
    任务结果：
        保存为domain资产的格式
        {'domain': 'www.google.com', 'CNAME': [], 'A': ['8.8.8.8']}, 
        {'domain': 'dns.google.com', 'CNAME': [], 'A': ['9.9.9.9']}]
    '''

    def __init__(self):
        super().__init__()
        self.task_name = 'subfinder'
        self.task_description = 'subfinder子域名信息收集'
        self.source = 'subfinder'
        #
        self.BIN_PATH = 'nemo/common/thirdparty/subfinder'
        self.BIN_FILE = 'subfinder_darwin_amd64'
        if platform.system() == 'Linux':
            self.BIN_FILE = 'subfinder_linux_amd64'
        self.CONFIG_FILE = 'config.yaml'

    def __parse_subfinder_result(self, datas):
        '''解析结果
        '''
        results = []
        if datas and len(datas) > 0:
            lines = datas.split(os.linesep)
            for line in lines:
                domain = line.strip()
                if domain:
                    results.append(domain)

        return results

    def fetch_domain(self, domain):
        '''调用subfinder收集子域名信息
        '''
        with NamedTemporaryFile('w+t') as tfile_url, NamedTemporaryFile('w+t') as tfile_output:
            # 将目标写入文件中
            tfile_url.write(domain)
            tfile_url.seek(0)
            subfinder_bin = [os.path.join(self.BIN_PATH, self.BIN_FILE), '-dL', tfile_url.name,
                             '-silent', '-nC', '-nW', '-config', os.path.join(self.BIN_PATH, self.CONFIG_FILE),
                             '-o', tfile_output.name]
            # 调用subfinder进行扫描
            try:
                child = subprocess.Popen(subfinder_bin)  # , stdout=subprocess.PIPE)
                child.wait()
                return self.__parse_subfinder_result(tfile_output.read())
            except Exception as e2:
                logger.error(traceback.format_exc())
                logger.error('subfinder domain:{}'.format(domain))
                result = None
                print(e2)

            return result
