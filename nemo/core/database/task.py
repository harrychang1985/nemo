#!/usr/bin/env python3
# coding:utf-8
import traceback
from datetime import datetime
from datetime import timedelta

from . import dbutils
from . import daobase

from nemo.common.utils.loggerutils import logger


class Task(daobase.DAOBase):
    def __init__(self):
        super().__init__()
        self.table_name = 'task'
        self.order_by = 'create_datetime desc'

    def save_and_update(self, data):
        '''保存数据
        新增或更新一条数据
        返回值：id
        '''
        # 查询obj是否已存在
        obj = self.gets({'task_id': data['task_id']})
        # 如果已存在，则更新记录
        if obj and len(obj) > 0:
            data_update = {}
            self.copy_exist(data_update, data, 'state')
            self.copy_exist(data_update, data, 'result')
            self.copy_exist(data_update, data, 'received')
            self.copy_exist(data_update, data, 'retried')
            self.copy_exist(data_update, data, 'revoked')
            self.copy_exist(data_update, data, 'started')
            self.copy_exist(data_update, data, 'succeeded')
            self.copy_exist(data_update, data, 'failed')
            self.copy_exist(data_update, data, 'progress_message')

            self.update(obj[0]['id'], data_update)
            return obj[0]['id']
        # 如果不存在，则生成新记录
        else:
            data_new = {'task_id': data['task_id']}
            self.copy_key(data_new, data, 'task_name')
            self.copy_key(data_new, data, 'args')
            self.copy_key(data_new, data, 'kwargs')
            self.copy_key(data_new, data, 'worker')
            self.copy_key(data_new, data, 'state')
            self.copy_key(data_new, data, 'result')
            self.copy_key(data_new, data, 'received')
            self.copy_key(data_new, data, 'retried')
            self.copy_key(data_new, data, 'revoked')
            self.copy_key(data_new, data, 'started')
            self.copy_key(data_new, data, 'succeeded')
            self.copy_key(data_new, data, 'failed')
            self.copy_key(data_new, data, 'progress_message')

            return self.add(data_new)

    def __fill_search_where(self, task_name=None, task_args=None, worker=None, state=None, result=None,
                            date_delta=None):
        '''根据指定的字段，生成查询SQL语句和参数
        '''
        sql = []
        param = []
        link_word = ' where '
        if task_name:
            sql.append(link_word)
            sql.append(' task_name like %s ')
            param.append('%' + task_name + '%')
            link_word = ' and '
        if task_args:
            sql.append(link_word)
            sql.append(' kwargs like %s ')
            param.append('%' + task_args + '%')
            link_word = ' and '
        if worker:
            sql.append(link_word)
            sql.append(' worker like %s ')
            param.append('%' + worker + '%')
            link_word = ' and '
        if result:
            sql.append(link_word)
            sql.append(' result like %s ')
            param.append('%' + result + '%')
            link_word = ' and '
        if state:
            sql.append(link_word)
            sql.append(' state=%s ')
            param.append(state)
            link_word = ' and '
        if date_delta:
            try:
                days_span = int(date_delta)
                if days_span > 0:
                    sql.append(link_word)
                    sql.append(' update_datetime between %s and %s ')
                    param.append(datetime.now() - timedelta(days=days_span))
                    param.append(datetime.now())
                    link_word = ' and '
            except:
                logger.error(traceback.format_exc())
                logger.error('date delta error:{}'.format(date_delta))

        return sql, param

    def count_by_search(self, task_name=None, task_args=None, worker=None, state=None, result=None, date_delta=None):
        '''统计记录总条数
        '''
        sql = []
        param = []
        sql.append('select count(id) from {} '.format(self.table_name))
        # 查询条件
        where_sql, where_param = self.__fill_search_where(
            task_name, task_args, worker, state, result, date_delta)
        sql.extend(where_sql)
        param.extend(where_param)

        return dbutils.queryone(''.join(sql), param)

    def gets_by_search(self, task_name=None, task_args=None, worker=None, state=None, result=None, date_delta=None,
                       fields=None, page=1, rows_per_page=None, order_by=None):
        '''根据组织机构、IP地址（包括范围）及端口的综合查询
        fields:     要返回的字段，列表格式('id','name','port')
        page:       分页位置，从1开始
        rows_per_page:  每页的记录数
        order_by     :  排序字段
        '''
        sql = []
        param = []
        sql.append('select {} from {} '.format(
            self.fill_fields(fields), self.table_name))
        # 查询条件
        where_sql, where_param = self.__fill_search_where(
            task_name, task_args, worker, state, result, date_delta)
        sql.extend(where_sql)
        param.extend(where_param)
        # 排序、分页
        sql.append(self.fill_order_by_and_limit(
            param, order_by, page, rows_per_page))

        return dbutils.queryall(''.join(sql), param)
