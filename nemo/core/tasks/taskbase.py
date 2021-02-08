#!/usr/bin/env python3
# coding:utf-8
import traceback

from nemo.common.utils.loggerutils import logger
from nemo.core.database.attr import DomainAttr
from nemo.core.database.attr import PortAttr
from nemo.core.database.domain import Domain
from nemo.core.database.ip import Ip
from nemo.core.database.port import Port


class TaskBase():
    def __init__(self):
        # 任务名称
        self.task_name = 'taskbase'
        # 任务描述
        self.task_description = 'taskbase'
        # 默认参数
        self.result_attr_keys = ()  # 要保存的属性字段
        self.org_id = None  # org_id
        self.source = 'taskbase'  # 属性来源
        self.target = []  # 任务目标

    def get_option(self, key, options, default_option):
        '''从options中获取参数值
        '''
        if key not in options:
            return default_option

        return options[key]

    def save_ip(self, data):
        '''保存ip资产相关的结果
        '''
        ip_app = Ip()
        port_app = Port()
        port_attr_app = PortAttr()
        result = {'ip': len(data), 'port': 0}

        for ip in data:
            # 保存IP
            if 'ip' not in ip:
                continue
            if self.org_id:
                ip['org_id'] = self.org_id
            ip_id = ip_app.save_and_update(ip)
            if ip_id > 0:
                # 保存每个端口数据
                if 'port' not in ip:
                    continue
                result['port'] += len(ip['port'])
                for port in ip['port']:
                    port['ip_id'] = ip_id
                    try:
                        port_id = port_app.save_and_update(port)
                        if port_id > 0:
                            # 保存端口的属性
                            for attr_key in self.result_attr_keys:
                                if attr_key in port and port[attr_key]:
                                    data_port_attr = {
                                        'r_id': port_id, 'source': self.source, 'tag': attr_key,
                                        'content': port[attr_key][:800]}
                                    try:
                                        port_attr_app.save_and_update(data_port_attr)
                                    except Exception as e:
                                        logger.error(traceback.format_exc())
                                        logger.error('save port port attr:{}-{}-{}-{}'.format(ip['port'], port['port'],
                                                                                            data_port_attr['tag'],
                                                                                            data_port_attr['content']))
                    except Exception as ex:
                        logger.error(traceback.format_exc())
                        logger.error('save ip port:{}-{}'.format(ip['port'], port['port']))
        return result

    def save_domain(self, data):
        '''保存domain资产的相关结果
        '''
        domain_app = Domain()
        doamin_attr_app = DomainAttr()
        result = {'domain': len(data)}
        for domain in data:
            if 'domain' not in domain:
                continue
            if self.org_id:
                domain['org_id'] = self.org_id
            # 保存到domain
            domain_id = domain_app.save_and_update(domain)
            if domain_id > 0:
                # 保存domain的属性
                for attr_key in ('CNAME', 'A', 'title', 'whatweb', 'server', 'httpx'):
                    if attr_key in domain:
                        for attr_value in domain[attr_key]:
                            domain_attr = {'r_id': domain_id, 'source': self.source,
                                           'tag': attr_key, 'content': attr_value[0:800]}
                            try:
                                doamin_attr_app.save_and_update(domain_attr)
                            except Exception as e:
                                logger.error(traceback.format_exc())
                                logger.error('save domain attr:{}-{}-{}'.format(domain['domain'], domain_attr['tag'],
                                                                                domain_attr['content']))

        return result
