#!/usr/bin/env python3
# coding:utf-8
import traceback
from flask import render_template
from flask import Blueprint
from flask import request
from flask import jsonify
from flask import session
from flask import Response

from nemo.common.utils.assertexport import export_ips
from nemo.common.utils.assertinfoparser import AssertInfoParser
from nemo.common.utils.loggerutils import logger
from nemo.core.database.attr import PortAttr
from nemo.core.database.ip import Ip
from nemo.core.database.organization import Organization

from .authenticate import login_check

ip_manager = Blueprint('ip_manager', __name__)


@ip_manager.route('/ip-list', methods=['GET', 'POST'])
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
                    'id': ip_row['id'],  
                    "index": index+start,  
                    "org_name": org_table.get(int(ip_row['org_id']))['org_name'] if ip_row['org_id'] else '',
                    "ip": ip_row['ip'],
                    "status": ip_row['status'],
                    "location": ip_row['location'].split(',')[0] if ip_row['location'] else '',
                    "create_time": str(ip_row['create_datetime']),
                    "update_time": str(ip_row['update_datetime']),
                    "port": port_list,
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
        logger.error(traceback.format_exc())
        print(e)

    return jsonify(json_data)


@ip_manager.route('/ip-info', methods=['GET'])
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


@ip_manager.route('/port-attr-delete/<int:port_attr_id>', methods=['POST'])
@login_check
def delete_port_attr_view(port_attr_id):
    '''删除一个端口的属性记录
    '''
    rows = PortAttr().delete(port_attr_id)

    return jsonify({'status': 'success', 'msg': rows})


@ip_manager.route('/ip-delete/<int:ip_id>', methods=['POST'])
@login_check
def delete_ip_view(ip_id):
    '''删除一个IP
    '''
    rows = Ip().delete(ip_id)

    return jsonify({'status': 'success', 'msg': rows})


@ip_manager.route('/ip-export', methods=['GET'])
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


@ip_manager.route('/ip-statistics', methods=['GET'])
@login_check
def ip_statistics_view():
    '''统计IP数据
    '''
    org_id = request.args.get('org_id')
    domain_address = request.args.get('domain_address')
    ip_address = request.args.get('ip_address')
    port = request.args.get('port')

    ip_list, ip_c_set, port_set = AssertInfoParser().statistics_ip(
        org_id, domain_address, ip_address, port)
    data = []
    data.append('Port:')
    data.append(','.join([str(x) for x in sorted(port_set)]))
    data.append('\nNetwork:')
    data.extend(sorted(ip_c_set))
    data.append('\nIP:')
    data.extend(ip_list)
    response = Response(
        '\n'.join(data), content_type='application/octet-stream')
    response.headers["Content-disposition"] = 'attachment; filename={}'.format(
        "ip-statistics.txt")

    return response
