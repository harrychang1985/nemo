#!/usr/bin/env python3
# coding:utf-8
import hashlib

from . import daobase


class AttrBase(daobase.DAOBase):
    def __init__(self):
        super().__init__()
        self.order_by = 'tag,update_datetime desc'

    def attr_hash(self, data):
        '''根据属性值计算hash
        '''
        hash_format = []
        hash_format.append(str(data['r_id']))
        hash_format.append(data['source'])
        hash_format.append(data['tag'])
        hash_format.append(data['content'])

        md5 = hashlib.new('md5', (''.join(hash_format)
                                  ).encode('utf-8')).hexdigest()
        return md5

    def add(self, data):
        '''增加一条记录：计算hash'''
        data['hash'] = self.attr_hash(data)
        return super().add(data)

    def update(self, Id, data):
        '''更新一条记录：如果hash需要更新，重新计算
        '''
        if 'hash' in data:
            data['hash'] = self.attr_hash(data)
        return super().update(Id, data)

    def save_and_update(self, data):
        '''保存数据
        新增或更新一条数据
        返回值：id
        '''
        # 查询obj是否已存在
        obj = self.gets({'hash': self.attr_hash(data)})
        # 如果该已存在，则更新记录
        if obj and len(obj) > 0:
            data_update = {}
            # 只更新update_datetime
            self.update(obj[0]['id'], data_update)
            return obj[0]['id']
        # 如果不存在，则生成新记录
        else:
            data_new = {'r_id': data['r_id'], 'tag': data['tag'],
                        'source': data['source'], 'content': data['content']}
            return self.add(data_new)


class IpAttr(AttrBase):
    def __init__(self):
        super().__init__()
        self.table_name = 'ip_attr'


class PortAttr(AttrBase):
    def __init__(self):
        super().__init__()
        self.table_name = 'port_attr'
        self.order_by = 'tag,source'


class DomainAttr(AttrBase):
    def __init__(self):
        super().__init__()
        self.table_name = 'domain_attr'
