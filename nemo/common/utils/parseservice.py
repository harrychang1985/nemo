#!/usr/bin/env python3
# coding:utf-8
import traceback
from nemo.common.utils.loggerutils import logger


class ParsePortService():
    '''
    解析端口的Service名称
    包括通用定义和自定义
    '''

    def __init__(self):
        '''默认参数
        '''
        # 使用的是nmap的Port与Service的对应关系文件
        self.nmap_services_file = 'nemo/common/utils/nmap-services'
        self.port_service = {}
        # 自定义端口
        self.custom_service_file = 'nemo/common/utils/custom-services.txt'
        self.custom_port_service = {}
        # 读取映射关系:nmap-services
        try:
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
        except FileNotFoundError:
            logger.error(traceback.format_exc())
            logger.error('nmap-services file not found')
        except:
            logger.error(traceback.format_exc())
        # 读取自定义的映射关系
        try:
            with open(self.custom_service_file) as f:
                for line in f:
                    txt = line.strip()
                    if not txt:
                        continue
                    datas = txt.split(' ')
                    if datas and len(datas) >= 2:
                        port = datas[0].strip()
                        service = datas[1].strip()
                        self.custom_port_service[port] = service
        except FileNotFoundError:
            logger.error(traceback.format_exc())
            logger.error('custom-services.txt file not found')
        except:
            logger.error(traceback.format_exc())

    def get_service(self, port, port_type='tcp'):
        '''根据端口号查找Service名称
        '''
        service = self.custom_port_service.get('{}/{}'.format(port, port_type), '')
        if not service:
            service = self.port_service.get(
                '{}/{}'.format(port, port_type), 'unknown')

        return service
