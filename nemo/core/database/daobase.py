#!/usr/bin/env python3
# coding:utf-8
import copy
from datetime import datetime
from . import dbutils


class DAOBase():
    def __init__(self):
        # 默认每页记录数
        self.rows_per_page = 20
        # 默认排序字段
        self.order_by = None
        # 表名，由各子类指定
        self.table_name = ''

    def set_default_datetime(self, data):
        '''设置默认时间
        '''
        data['create_datetime'] = datetime.now()
        data['update_datetime'] = datetime.now()

    def update_datetime(self, data):
        '''设置更新时间
        '''
        data['update_datetime'] = datetime.now()

    def fill_fields(self, fields):
        '''处理返回结果的字段
        '''
        return '*' if not fields else ','.join(fields)

    def fill_where(self, query, param, pre_word='where'):
        '''处理查询条件
        '''
        sql = []
        sql.append(' {} '.format(pre_word))
        sql.append('=%s and '.join(query.keys()))
        sql.append('=%s')
        for k, v in query.items():
            param.append(v)

        return ''.join(sql)

    def fill_order_by_and_limit(self, param, order_by, page, rows_per_page):
        '''多记录查询时的排序、分页
        注意：order by是SQL语句拼接，有注入的风险，考虑进行参数过滤
        '''
        # 排序
        sql = []
        if not order_by:
            order_by = self.order_by
        if order_by:
            sql.append(' order by {}'.format(order_by))
        if not rows_per_page:
            rows_per_page = self.rows_per_page
        # 指定分页
        sql.append(' limit %s,%s')
        param.append((page-1)*rows_per_page)
        param.append(rows_per_page)

        return ''.join(sql)

    def add(self, data):
        '''增加一条记录
        data:   增加的字段和值，字典格式如{'name':'sgcc','sort_order':300}
        '''
        self.set_default_datetime(data)
        # sql语句
        sql = 'insert into {}('.format(self.table_name)
        sql += ','.join(data.keys())
        sql += ') values({})'.format(','.join(['%s']*len(data)))
        # sql预编译参数
        param = []
        for k, v in data.items():
            param.append(v)

        return dbutils.insertone(sql=sql, param=param)

    def update(self, Id, data):
        '''更新一条记录
        Id:     记录的id
        data:   要更新的字段和值，字典格式如{'name':'sgcc','sort_order':300}
        '''
        self.update_datetime(data)
        # sql语句
        sql = 'update {} set '.format(self.table_name)
        sql += '=%s,'.join(data.keys())
        sql += '=%s  where id=%s'
        # sql预编译参数
        param = []
        for k, v in data.items():
            param.append(v)
        param.append(Id)

        return dbutils.execute(sql, param)

    def delete(self, Id):
        '''删除一条记录
        '''
        sql = 'delete from {} where id=%s'.format(self.table_name)

        return dbutils.execute(sql, (Id,))

    def get(self, Id):
        '''根据ID查询一条记录
        '''
        sql = 'select * from {} where id = %s'.format(self.table_name)

        return dbutils.queryone(sql, (Id,))

    def gets(self, query=None, fields=None, page=1, rows_per_page=None, order_by=None):
        '''查询多条记录
        query:  查询条件，字典格式如{'name':'hello','port':80}，多个条件默认是and
        fields: 要返回的字段，列表格式('id','name','port')
        page:   分页位置，从1开始
        rows_per_page:  每页的记录数
        order_by     :  排序字段
        '''
        sql = []
        param = []
        sql.append('select {} from {} '.format(
            self.fill_fields(fields), self.table_name))
        # 查询条件
        if query and len(query) > 0:
            sql.append(self.fill_where(query, param))
        # 排序、分页
        sql.append(self.fill_order_by_and_limit(
            param, order_by, page, rows_per_page))

        return dbutils.queryall(''.join(sql), param)

    def count(self, query=None):
        '''统计记录总条数
        query:  查询条件，字典格式如{'name':'hello','port':80}，多个条件默认是and
        '''
        sql = []
        param = []
        sql.append('select count(id) from {} '.format(self.table_name))
        # 查询条件
        if query and len(query) > 0:
            sql.append(self.fill_where(query, param))

        return dbutils.queryone(''.join(sql), param)

    def copy_key(self, data_to, data_from, key, default=None):
        '''复制dict的值
        如果key不存在，则default的值
        '''
        if key in data_from:
            data_to[key] = copy.copy(data_from[key])
        else:
            data_to[key] = default

    def copy_exist(self, data_to, data_from, key):
        '''复制dict中key存在的值，如果该key不存在，则不会复制
        '''
        if key in data_from:
            data_to[key] = copy.copy(data_from[key])
