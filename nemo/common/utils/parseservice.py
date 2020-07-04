#!/usr/bin/env python3
# coding:utf-8


class ParsePortService():
    '''默认端口号的Service名称
    '''

    def __init__(self):
        '''默认参数
        '''
        # 使用的是nmap的Port与Service的对应关系文件
        self.nmap_services_file = 'nemo/common/utils/nmap-services'
        self.port_service = {}
        # 读取全部映射关系
        with open(self.nmap_services_file) as f:
            for line in f:
                if line.startswith('#'):
                    continue
                '''ms-wbt-server\t3389/tcp\t0.083904\t# Microsoft Remote Display Protocol (aka ms-term-serv, microsoft-rdp) | MS WBT Server'''
                datas = line.split('\t')
                if datas and len(datas) >= 3:
                    service = datas[0]
                    port = datas[1]
                    self.port_service[port] = service

    def get_service(self, port, type='tcp'):
        '''根据端口号查找Service名称
        '''
        return self.port_service.get('{}/{}'.format(port, type), 'unknown')
