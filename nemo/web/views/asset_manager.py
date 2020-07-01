#!/usr/bin/env python3
# coding:utf-8

from flask import render_template
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import session
from flask import Response

from .authenticate import login_check
from nemo.core.database.ip import Ip
from nemo.core.database.port import Port
from nemo.core.database.domain import Domain
from nemo.core.database.organization import Organization
from nemo.core.database.attr import IpAttr, PortAttr, DomainAttr
from nemo.common.utils.assertinfoparser import AssertInfoParser
from nemo.common.utils.assertexport import export_domains, export_ips

asset_manager = Blueprint('asset_manager', __name__)


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
        org_list.insert(0, {'id': '', 'org_name': '--选择组织机构--'})

        data = {'org_list': org_list, 'ip_address_ip': session.get('ip_address_ip', default=''), 'domain_address': session.get('domain_address', default=''),
                'port': session.get('port', default=''), 'session_org_id': session.get('session_org_id', default='')}

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
        domain_address = request.form.get('domain_address')
        port = request.form.get('port')

        session['ip_address_ip'] = ip_address
        session['domain_address'] = domain_address
        session['port'] = port
        session['session_org_id'] = org_id

        count = 0
        ips = ip_table.gets_by_org_domain_ip_port(org_id, domain_address,
                                                  ip_address, port, page=(start//length)+1, rows_per_page=length)
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
                    "location": ip_row['location'].split(',')[0] if ip_row['location'] else '',
                    "create_time": str(ip_row['create_datetime']),
                    "update_time": str(ip_row['update_datetime']),
                    "port": ', '.join([str(x) for x in port_list]),
                    "title": ', '.join(list(title_set)),
                    "banner": ', '.join(list(banner_set))
                })
                index += 1

            count = ip_table.count_by_org_domain_ip_port(
                org_id, domain_address, ip_address, port)
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


@asset_manager.route('/ip-export', methods=['GET'])
@login_check
def ip_export_view():
    '''导出IP数据
    '''
    org_id = request.args.get('org_id')
    domain_address = request.args.get('domain_address')
    ip_address = request.args.get('ip_address')
    port = request.args.get('port')
    
    data = export_ips(org_id, domain_address, ip_address, port)
    response = Response(data, content_type='application/octet-stream')
    response.headers["Content-disposition"] = 'attachment; filename={}'.format(
        "ip-export.xlsx")

    return response


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
        org_list.insert(0, {'id': '', 'org_name': '--选择组织机构--'})

        data = {'org_list': org_list, 'domain_address': session.get(
            'domain_address', default=''), 'ip_address_domain': session.get('ip_address_domain', default=''), 'session_org_id': session.get('session_org_id', default='')}

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
        session['session_org_id'] = org_id

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
                    "ip": ', '.join(set(['<a href="/ip-info?ip={0}" target="_blank">{0}</a>'.format(ip_row['content']) for ip_row in ips])),
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


@asset_manager.route('/domain-export', methods=['GET'])
@login_check
def domain_export_view():
    '''导出域名数据
    '''

    org_id = request.args.get('org_id')
    ip_address = request.args.get('ip_address')
    domain_address = request.args.get('domain_address')

    data = export_domains(org_id, domain_address, ip_address)
    response = Response(data, content_type='application/octet-stream')
    response.headers["Content-disposition"] = 'attachment; filename={}'.format(
        "domain-export.xlsx")

    return response
