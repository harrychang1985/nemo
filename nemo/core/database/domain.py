#!/usr/bin/env python3
# coding:utf-8
from . import dbutils
from . import daobase


class Domain(daobase.DAOBase):
    def __init__(self):
        super().__init__()
        self.table_name = 'domain'
        self.order_by = 'domain'

    def save_and_update(self, data):
        '''保存数据
        新增或更新一条数据
        返回值：id
        '''
        # 查询obj是否已存在
        obj = self.gets({'domain': data['domain']})
        # 如果已存在，则更新记录
        if obj and len(obj) > 0:
            data_update = {}
            self.copy_exist(data_update, data, 'org_id')
            self.update(obj[0]['id'], data_update)
            return obj[0]['id']
        # 如果不存在，则生成新记录
        else:
            data_new = {'domain': data['domain']}
            self.copy_key(data_new, data, 'org_id')

            return self.add(data_new)

    def __fill_where_by_search(self, org_id, domain, ip, color_tag, memo_content):
        '''根据指定的字段，生成查询SQL语句和参数
        '''
        sql = []
        param = []
        link_word = ' where '
        if org_id:
            sql.append(link_word)
            sql.append(' org_id=%s ')
            param.append(org_id)
            link_word = ' and '
        if domain:
            sql.append(link_word)
            sql.append(' domain like %s')
            param.append('%'+domain+'%')
            link_word = ' and '
        if ip:
            sql.append(link_word)
            sql.append(
                ' id in (select distinct r_id from domain_attr where tag="A" and content=%s)')
            param.append(ip)
            link_word = ' and '
        if color_tag:
            sql.append(link_word)
            sql.append(
                ' id in (select r_id from domain_color_tag where color=%s)')
            param.append(color_tag)
            link_word = ' and '
        if memo_content:
            sql.append(link_word)
            sql.append(
                ' id in (select r_id from domain_memo where content like %s)')
            param.append('%' + memo_content+'%')
            link_word = ' and '

        return sql, param

    def count_by_search(self, org_id=None, domain=None, ip=None, color_tag=None, memo_content=None):
        '''统计记录总条数
        org_id:     组织的ID
        domain:     单个域名
        ip:         单个ip地址(192.168.1.5）
        color_tag:  标记的颜色
        memo_content:备忘录信息
        '''
        sql = []
        param = []
        sql.append('select count(id) from {} '.format(self.table_name))
        # 查询条件
        where_sql, where_param = self.__fill_where_by_search(
            org_id, domain, ip, color_tag, memo_content)
        sql.extend(where_sql)
        param.extend(where_param)

        return dbutils.queryone(''.join(sql), param)

    def gets_by_search(self, org_id=None, domain=None, ip=None, color_tag=None, memo_content=None,
                       fields=None, page=1, rows_per_page=None, order_by=None):
        '''根据组织机构、IP地址（包括范围）及端口的综合查询
        org_id:     组织的ID
        domain:     单个域名
        ip:         单个ip地址(192.168.1.5）
        color_tag:  标记的颜色
        memo_content:备忘录信息
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
        where_sql, where_param = self.__fill_where_by_search(
            org_id, domain, ip, color_tag, memo_content)
        sql.extend(where_sql)
        param.extend(where_param)
        # 排序、分页
        sql.append(self.fill_order_by_and_limit(
            param, order_by, page, rows_per_page))

        return dbutils.queryall(''.join(sql), param)
