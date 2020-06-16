#!/usr/bin/env python3
# coding:utf-8
from . import dbutils
from . import daobase
import re
import ipaddress


class Ip(daobase.DAOBase):
    def __init__(self):
        super().__init__()
        self.table_name = 'ip'
        self.order_by = 'ip_int'

    def ip2int(self, ip):
        '''将点分的字符串IP转换为整数值
        '''
        ips = ip.strip().split('.')
        x = int(ips[0]) << 24 | int(ips[1]) << 16 | int(
            ips[2]) << 8 | int(ips[3])
        return x

    def add(self, data):
        '''增加一条IP记录：计算IP的整数值
        '''
        data['ip_int'] = self.ip2int(data['ip'])
        return super().add(data)

    def update(self, Id, data):
        '''更新一条IP记录：如果IP地址需要更新，重新计算整数值
        '''
        if 'ip' in data:
            data['ip_int'] = self.ip2int(data['ip'])
        return super().update(Id, data)

    def save_and_update(self, data):
        '''保存数据
        新增或更新一条数据
        返回值：id
        '''
        # 查询obj是否已存在
        obj = self.gets({'ip': data['ip']})
        # 如果已存在，则更新记录
        if obj and len(obj) > 0:
            data_update = {}
            self.copy_exist(data_update, data, 'status')
            self.copy_exist(data_update, data, 'org_id')
            self.copy_exist(data_update, data, 'location')
            self.update(obj[0]['id'], data_update)
            # if self.update(obj[0]['id'], data_update) else 0
            return obj[0]['id']
        # 如果不存在，则生成新记录
        else:
            data_new = {'ip': data['ip']}
            self.copy_key(data_new, data, 'status', 'alive')
            self.copy_key(data_new, data, 'org_id')
            self.copy_key(data_new, data, 'location')
            return self.add(data_new)

    def __fill_org_ip_port_where(self, org_id, ip, port):
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
        if ip:
            # IP范围范围：是否是IP/掩码
            ip_mask = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}$'
            try:
                if re.match(ip_mask, ip):
                    ip_network = ipaddress.ip_network(ip, strict=False)
                    param.append(int(ip_network[0]))
                    param.append(int(ip_network[-1]))
                    sql.append(link_word)
                    sql.append(' ip_int between %s and %s ')
                else:
                    param.append(ip)
                    sql.append(link_word)
                    sql.append(' ip=%s ')
                link_word = ' and '
            except Exception as e:
                print(e)
                pass
        if port:
            sql.append(link_word)
            sql.append(' id in (select distinct ip_id from port where ')
            port_link_word = ''
            for p in port.split(','):
                try:
                    p_int = int(p)
                    sql.append(port_link_word)
                    sql.append(' port=%s')
                    param.append(p_int)
                    port_link_word = ' or '
                except Exception as e:
                    print(e)
                    pass
            sql.append(')')

        return sql, param

    def count_by_org_ip_port(self, org_id=None, ip=None, port=None):
        '''统计记录总条数
        org_id:     组织的ID
        ip:         ip地址或ip/掩码,(192.168.1.5或172.16.0.0/16）
        port:       端口号，多个端口号以,分隔('21,22,80,8080')
        '''
        sql = []
        param = []
        sql.append('select count(id) from {} '.format(self.table_name))
        # 查询条件
        where_sql, where_param = self.__fill_org_ip_port_where(
            org_id, ip, port)
        sql.extend(where_sql)
        param.extend(where_param)

        return dbutils.queryone(''.join(sql), param)

    def gets_by_org_ip_port(self, org_id=None, ip=None, port=None, fields=None, page=1, rows_per_page=None, order_by=None):
        '''根据组织机构、IP地址（包括范围）及端口的综合查询
        org_id:     组织的ID
        ip:         ip地址或ip/掩码,(192.168.1.5或172.16.0.0/16）
        port:       端口号，多个端口号以,分隔('21,22,80,8080')
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
        where_sql, where_param = self.__fill_org_ip_port_where(
            org_id, ip, port)
        sql.extend(where_sql)
        param.extend(where_param)
        # 排序、分页
        sql.append(self.fill_order_by_and_limit(
            param, order_by, page, rows_per_page))

        return dbutils.queryall(''.join(sql), param)
