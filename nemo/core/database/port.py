#!/usr/bin/env python3
# coding:utf-8
from . import daobase


class Port(daobase.DAOBase):
    def __init__(self):
        super().__init__()
        self.table_name = 'port'
        self.order_by = 'port'

    def save_and_update(self, data):
        '''保存数据
        新增或更新一条数据
        返回值：id
        '''
        # 查询obj是否已存在
        obj = self.gets({'ip_id': data['ip_id'], 'port': data['port']})
        # 如果该obj已存在，则更新记录
        if obj and len(obj) > 0:
            data_update = {}
            self.copy_exist(data_update, data, 'status')
            self.update(obj[0]['id'], data_update)
            return obj[0]['id']
        # 如果obj不存在，则生成新记录
        else:
            data_new = {'ip_id': data['ip_id'], 'port': data['port']}
            self.copy_key(data_new, data, 'status', 'open')

            return self.add(data_new)
