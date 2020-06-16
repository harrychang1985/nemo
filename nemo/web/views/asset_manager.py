#!/usr/bin/env python3
# coding:utf-8

from flask import render_template
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import session

from .authenticate import login_check
from nemo.core.database.ip import Ip
from nemo.core.database.port import Port
from nemo.core.database.domain import Domain
from nemo.core.database.organization import Organization
from nemo.core.database.attr import IpAttr, PortAttr, DomainAttr

asset_manager = Blueprint('asset_manager', __name__)


class AssertInfoParser():
    '''资产信息（IP、域名）聚合
    '''

    def __init__(self):
        super().__init__()

    def __get_ip_domain(self, ip):
        '''查询IP关联的域名
        '''
        domain_set = set()
        domain_attrs_obj = DomainAttr().gets(query={'tag': 'A', 'content': ip})
        for domain_attr_obj in domain_attrs_obj:
            domain_obj = Domain().get(domain_attr_obj['r_id'])
            if domain_attr_obj:
                domain_set.add(domain_obj['domain'])

        return domain_set

    def get_ip_port_info(self, ip, ip_id):
        '''获取IP端口属性，并生成port、title、banner聚合信息
        '''
        port_list = []
        title_set = set()
        banner_set = set()
        ports_attr_info = []

        ports_obj = Port().gets(query={'ip_id': ip_id})
        for port_obj in ports_obj:
            port_list.append(port_obj['port'])
            # 获取端口属性
            port_attrs_obj = PortAttr().gets(query={'r_id': port_obj['id']})
            FIRST_ROW = True
            # 每个端口的一个属性生成一行记录
            # 第一行记录显示IP和PORT，其它行保持为空（方便查看）
            for port_attr_obj in port_attrs_obj:
                pai = {}
                if FIRST_ROW:
                    pai.update(ip=ip, port=port_obj['port'])
                    FIRST_ROW = False
                else:
                    pai.update(ip='', port='')
                pai.update(id=port_attr_obj['id'], tag=port_attr_obj['tag'], content=port_attr_obj['content'], source=port_attr_obj['source'],
                           update_datetime=port_attr_obj['update_datetime'].strftime('%Y-%m-%d %H:%M'))
                # 更新集合
                if port_attr_obj['tag'] == 'title':
                    title_set.add(port_attr_obj['content'])
                elif port_attr_obj['tag'] in ('banner', 'tag', 'server'):
                    banner_set.add(port_attr_obj['content'])

                ports_attr_info.append(pai)

        return port_list, title_set, banner_set, ports_attr_info

    def get_ip_info(self, Id):
        '''聚合一个IP的详情
        '''
        ip_info = {}
        # 获取IP
        ip_obj = Ip().get(Id)
        if not ip_obj:
            return None
        ip_info.update(ip=ip_obj['ip'], location=ip_obj['location'], status=ip_obj['status'], create_datetime=ip_obj['create_datetime'].strftime(
            '%Y-%m-%d %H:%M'), update_datetime=ip_obj['update_datetime'].strftime('%Y-%m-%d %H:%M'))
        # 获取组织名称
        if ip_obj['org_id']:
            organziation__obj = Organization().get(ip_obj['org_id'])
            if organziation__obj:
                ip_info.update(organization=organziation__obj['org_name'])
        else:
            ip_info.update(Organization='')
        # 端口、标题、banner、端口详情
        port_list, title_set, banner_set, ports_attr_info = self.get_ip_port_info(
            ip_obj['ip'], ip_obj['id'])
        ip_info.update(port_attr=ports_attr_info)
        ip_info.update(title=list(title_set))
        ip_info.update(banner=list(banner_set))
        ip_info.update(port=port_list)
        # IP关联的域名
        domain_set = self.__get_ip_domain(ip_obj['ip'])
        ip_info.update(domain=list(domain_set))

        return ip_info

    def get_domain_info(self, Id):
        '''聚合一个DOMAIN的详情
        '''
        domain_info = {}
        # 获取DOMAIN
        domain_obj = Domain().get(Id)
        if not domain_obj:
            return None
        domain_info.update(
            domain=domain_obj['domain'], create_datetime=domain_obj['create_datetime'].strftime('%Y-%m-%d %H:%M'), update_datetime=domain_obj['update_datetime'].strftime('%Y-%m-%d %H:%M'))
        # 获取组织名称
        if domain_obj['org_id']:
            organziation__obj = Organization().get(domain_obj['org_id'])
            if organziation__obj:
                domain_info.update(organization=organziation__obj['org_name'])
        else:
            domain_info.update(organization='')
        domain_attrs_obj = DomainAttr().gets(query={'r_id': domain_obj['id']})
        # 获取域名的属性信息：title和ip,whatweb
        title_set = set()
        ip_set = set()
        whatweb_set = set()
        for domain_attr_obj in domain_attrs_obj:
            if domain_attr_obj['tag'] == 'title':
                title_set.add(domain_attr_obj['content'])
            elif domain_attr_obj['tag'] == 'A':
                ip_set.add(domain_attr_obj['content'])
            elif domain_attr_obj['tag'] == 'whatweb':
                whatweb_set.add(domain_attr_obj['content'])
        domain_info.update(title=list(title_set))
        # 获取域名关联的IP端口详情：
        port_set = set()
        title_set = set()
        banner_set = set()
        ip_port_list = []
        for domain_ip in ip_set:
            ip_obj = Ip().gets(query={'ip': domain_ip})
            if ip_obj and len(ip_obj) > 0:
                #port_list, title_set, banner_set, ports_attr_info
                p, t, b, pai = self.get_ip_port_info(
                    ip_obj[0]['ip'], ip_obj[0]['id'])
                port_set.update(p)
                title_set.update(t)
                banner_set.update(b)
                ip_port_list.extend(pai)
        domain_info.update(ip=list(ip_set))
        domain_info.update(port=list(port_set))
        domain_info.update(title=list(title_set))
        domain_info.update(whatweb=list(whatweb_set))
        domain_info.update(banner=list(banner_set))
        domain_info.update(port_attr=ip_port_list)

        return domain_info


@asset_manager.route('/ip-list', methods=['GET', 'POST'])
@login_check
def ip_asset_view():
    '''IP资产列表展示
    '''
    if request.method == 'GET':
        org_table = Organization()
        org_list = org_table.gets()
        if not org_list:
            org_list = []
        org_list.insert(0,{'id':'','org_name':'--选择组织机构--'})

        data = {'org_list': org_list, 'ip_address_ip': session.get(
            'ip_address_ip', default=''), 'port': session.get('port', '')}
        return render_template('ip-list.html', data=data)

    ip_table = Ip()
    port_table = Port()
    org_table = Organization()
    aip = AssertInfoParser()
    ip_list = []
    json_data = {}
    index = 1

    try:
        draw = int(request.form.get('draw'))
        start = int(request.form.get('start'))
        length = int(request.form.get('length'))
        org_id = request.form.get('org_id')
        ip_address = request.form.get('ip_address')
        port = request.form.get('port')

        session['ip_address_ip'] = ip_address
        session['port'] = port

        count = 0
        ips = ip_table.gets_by_org_ip_port(
            org_id, ip_address, port, page=(start//length)+1, rows_per_page=length)
        if ips:
            for ip_row in ips:
                port_list, title_set, banner_set, ports_attr_info = aip.get_ip_port_info(
                    ip_row['ip'], ip_row['id'])
                ip_list.append({
                    'id': ip_row['id'],  # 表内序号
                    "index": index+start,  # 显示序号
                    "org_name": org_table.get(int(ip_row['org_id']))['org_name'] if ip_row['org_id'] else '',
                    "ip": ip_row['ip'],
                    "status": ip_row['status'],
                    "location": ip_row['location'],
                    "create_time": str(ip_row['create_datetime']),
                    "update_time": str(ip_row['update_datetime']),
                    "port": ', '.join([str(x) for x in port_list]),
                    "title": list(title_set),
                    "banner": list(banner_set)
                })
                index += 1

            count = ip_table.count_by_org_ip_port(org_id, ip_address, port)
        json_data = {
            'draw': draw,
            'recordsTotal': count,
            'recordsFiltered': count,
            'data': ip_list
        }

    except Exception as e:
        print(e)

    return jsonify(json_data)


@asset_manager.route('/ip-info', methods=['GET'])
@login_check
def ip_asset_info_view():
    '''显示一个IP地址的详细信息
    '''
    ip = request.args.get('ip')
    ips = Ip().gets(query={'ip': ip})
    if ips and len(ips) > 0:
        ip_info = AssertInfoParser().get_ip_info(ips[0]['id'])
        if 'port_attr' in ip_info and ip_info['port_attr']:
            # 表格背景设置：
            table_backgroud_set = False           
            for p in ip_info['port_attr']:
                if p['ip'] and p['port']:
                    table_backgroud_set = not table_backgroud_set
                p['table_backgroud_set'] = table_backgroud_set
    else:
        ip_info = None  
   

 
    return render_template('ip-info.html', ip_info=ip_info)


@asset_manager.route('/port-attr-delete/<int:port_attr_id>', methods=['POST'])
@login_check
def delete_port_attr_view(port_attr_id):
    '''删除一个端口的属性记录
    '''
    rows = PortAttr().delete(port_attr_id)

    return jsonify({'status': 'success', 'msg': rows})


@asset_manager.route('/ip-delete/<int:ip_id>', methods=['POST'])
@login_check
def delete_ip_view(ip_id):
    '''删除一个IP
    '''
    rows = Ip().delete(ip_id)

    return jsonify({'status': 'success', 'msg': rows})


@asset_manager.route('/domain-list', methods=['GET', 'POST'])
@login_check
def domain_asset_view():
    '''页面上显示域名资产，datatable前端ajax请求进行分页
    '''
    if request.method == 'GET':
        org_table = Organization()
        org_list = org_table.gets()
        if not org_list:
            org_list = []
        org_list.insert(0,{'id':'','org_name':'--选择组织机构--'})

        data = {'org_list': org_list, 'domain_address': session.get(
            'domain_address', default=''), 'ip_address_domain': session.get('ip_address_domain', default='')}

        return render_template('domain-list.html', data=data)

    domain_list = []
    ip_table = Ip()
    org_table = Organization()
    domain_table = Domain()
    domain_attr_table = DomainAttr()
    api = AssertInfoParser()
    index = 1

    try:
        draw = int(request.form.get('draw'))
        start = int(request.form.get('start'))
        length = int(request.form.get('length'))
        org_id = request.form.get('org_id')
        ip_address = request.form.get('ip_address')
        domain_address = request.form.get('domain_address')

        session['ip_address_domain'] = ip_address
        session['domain_address'] = domain_address

        count = 0
        domains = domain_table.gets_by_org_domain_ip(
            org_id, domain_address, ip_address, page=start//length+1, rows_per_page=length)
        if domains:
            for domain_row in domains:
                ips = domain_attr_table.gets(
                    query={'tag': 'A', 'r_id': domain_row['id']})
                domain_info = api.get_domain_info(domain_row['id'])
                domain_list.append({
                    'id': domain_row['id'],
                    "index": index+start,
                    "domain": domain_row['domain'],
                    "ip": ', '.join(set(['<a href="/ip-info?ip={0}">{0}</a>'.format(ip_row['content']) for ip_row in ips])),
                    "org_name": org_table.get(int(domain_row['org_id']))['org_name'] if domain_row['org_id'] else '',
                    "create_time": str(domain_row['create_datetime']),
                    "update_time": str(domain_row['update_datetime']),
                    'port': domain_info['port'],
                    'title': domain_info['title'],
                    'banner': domain_info['banner']
                })
                index += 1
            count = domain_table.count_by_org_domain_ip(
                org_id, domain_address, ip_address)
        json_data = {
            'draw': draw,
            'recordsTotal': count,
            'recordsFiltered': count,
            'data': domain_list
        }
    except Exception as e:
        print(e)

    return jsonify(json_data)


@asset_manager.route('/domain-info', methods=['GET'])
@login_check
def domain_asset_info_view():
    '''显示一个DOMAIN的详细信息
    '''
    domain = request.args.get('domain')
    domains = Domain().gets(query={'domain': domain})
    if domains and len(domains) > 0:
        domain_info = AssertInfoParser().get_domain_info(domains[0]['id'])
        # 表格背景设置：
        table_backgroud_set = False   
        if 'port_attr' in domain_info and domain_info['port_attr']:    
            for p in domain_info['port_attr']:
                if p['ip'] and p['port']:
                    table_backgroud_set = not table_backgroud_set
                p['table_backgroud_set'] = table_backgroud_set
    else:
        domain_info = None
    

    return render_template('domain-info.html', domain_info=domain_info)


@asset_manager.route('/domain-delete/<int:domain_id>', methods=['POST'])
@login_check
def delete_domain_view(domain_id):
    '''删除一个DOMAIN
    '''
    rows = Domain().delete(domain_id)

    return jsonify({'status': 'success', 'msg': rows})
