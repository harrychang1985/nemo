#!/usr/bin/env python3
# coding:utf-8
import traceback
from nemo.common.utils.loggerutils import logger
from nemo.common.utils.iputils import check_ip_or_domain


class IPLocationCustom():
    '''
    自定义IP与位置对应关系
    '''

    def __init__(self):
        self.iplocation_custome_file = 'nemo/common/utils/iplocation-custom.txt'
        self.ip_location_dict = {}
        # 加载IP地址定义
        self.__load_iplocation()

    def __load_iplocation(self):
        '''读取自定义的映射关系
        '''
        try:
            with open(self.iplocation_custome_file) as f:
                for line in f:
                    txt = line.strip()
                    if not txt:
                        continue
                    if txt.startswith('#'):
                        continue
                    datas = txt.split(' ')
                    if datas and len(datas) >= 2:
                        ip = datas[0].strip()
                        location = datas[1].strip()
                        self.ip_location_dict[ip] = location
        except FileNotFoundError:
            logger.error('iplocation-custom file not found')
        except:
            logger.error(traceback.format_exc())

    def get_iplocation(self, ip):
        '''获取IP地址
        先查C段，如果没有C段则查B段
        '''
        if not check_ip_or_domain:
            logger.error('check ip fail:{}'.format(ip))
            return ''
        datas = ip.split('.')
        c_data = '{}.0/24'.format('.'.join(datas[0:3]))
        location = self.ip_location_dict.get(c_data)
        if not location:
            b_data = '{}.0.0/16'.format('.'.join(datas[0:2]))
            location = self.ip_location_dict.get(b_data)

        return location if location else ''
