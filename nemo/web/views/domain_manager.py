#!/usr/bin/env python3
# coding:utf-8

from flask import render_template
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import session
from flask import Response

from nemo.common.utils.assertexport import export_domains
from nemo.common.utils.assertinfoparser import AssertInfoParser
from nemo.core.database.attr import DomainAttr
from nemo.core.database.domain import Domain
from nemo.core.database.organization import Organization

from .authenticate import login_check

domain_manager = Blueprint('domain_manager', __name__)


@domain_manager.route('/domain-list', methods=['GET', 'POST'])
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
    org_table = Organization()
    domain_table = Domain()
    domain_attr_table = DomainAttr()
    api = AssertInfoParser()
    index = 1
    json_data = {}

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


@domain_manager.route('/domain-info', methods=['GET'])
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


@domain_manager.route('/domain-delete/<int:domain_id>', methods=['POST'])
@login_check
def delete_domain_view(domain_id):
    '''删除一个DOMAIN
    '''
    rows = Domain().delete(domain_id)

    return jsonify({'status': 'success', 'msg': rows})


@domain_manager.route('/domain-export', methods=['GET'])
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
