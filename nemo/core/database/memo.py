#!/usr/bin/env python3
# coding:utf-8
from . import daobase
from . import dbutils


class Memo(daobase.DAOBase):
    def __init__(self):
        super().__init__()

    def get(self, Id):
        '''根据关联的ID查询一条记录
        '''
        sql = 'select * from {} where r_id = %s'.format(self.table_name)

        return dbutils.queryone(sql, (Id,))

    def delete(self, Id):
        '''根据关联的ID删除一条记录
        '''
        sql = 'delete from {} where r_id=%s'.format(self.table_name)

        return dbutils.execute(sql, (Id,))

    def save_and_update(self, data):
        '''保存数据
        新增或更新一条数据
        返回值：id
        '''
        # 查询obj是否已存在
        obj = self.get(data['r_id'])
        # 如果已存在，则更新记录
        if obj:
            data_update = {}
            self.copy_exist(data_update, data, 'r_id')
            self.copy_exist(data_update, data, 'content')
            self.update(obj['id'], data_update)
            return obj['id']
        # 如果不存在，则生成新记录
        else:
            data_new = {'r_id': data['r_id']}
            self.copy_key(data_new, data, 'content', '')
            return self.add(data_new)


class DomainMemo(Memo):
    def __init__(self):
        self.table_name = 'domain_memo'


class IpMemo(Memo):
    def __init__(self):
        self.table_name = 'ip_memo'
