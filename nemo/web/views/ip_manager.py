#!/usr/bin/env python3
# coding:utf-8
import re
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
        org_list.insert(0, {'id': '', 'org_name': '--组织机构--'})

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
        content = request.form.get('content')
        iplocation = request.form.get('iplocation')
        port_status = request.form.get('port_status')

        session['ip_address_ip'] = ip_address
        session['domain_address'] = domain_address
        session['port'] = port
        session['session_org_id'] = org_id

        count = 0
        ips = ip_table.gets_by_search(org_id=org_id, domain=domain_address, ip=ip_address,port=port, content=content,
                                    iplocation=iplocation, port_status=port_status, page=(start//length)+1, rows_per_page=length)
        if ips:
            for ip_row in ips:
                port_list, title_set, banner_set, _, port_status_dict = aip.get_ip_port_info(
                    ip_row['ip'], ip_row['id'])
                port_with_status_list = []
                for p in port_list:
                    if str(p) in port_status_dict and re.match(r'^\d{3}$',port_status_dict[str(p)]):
                        port_with_status_list.append("{}[{}]".format(p,port_status_dict[str(p)]))
                    else:
                        port_with_status_list.append(str(p))

                ip_list.append({
                    'id': ip_row['id'],
                    "index": index+start,
                    "org_name": org_table.get(int(ip_row['org_id']))['org_name'] if ip_row['org_id'] else '',
                    "ip": ip_row['ip'],
                    "status": ip_row['status'],
                    "location": ip_row['location'].split(',')[0] if ip_row['location'] else '',
                    "create_time": str(ip_row['create_datetime']),
                    "update_time": str(ip_row['update_datetime']),
                    "port": port_with_status_list,
                    "title": ', '.join(list(title_set)),
                    "banner": ', '.join(list(banner_set))
                })
                index += 1

            count = ip_table.count_by_search(org_id=org_id, domain=domain_address,
                                             ip=ip_address, port=port, content=content, iplocation=iplocation,port_status=port_status)
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
    content = request.args.get('content')
    iplocation = request.args.get('iplocation')
    port_status = request.args.get('port_status')

    data = export_ips(org_id, domain_address, ip_address,
                      port, content, iplocation, port_status)
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
    content = request.args.get('content')
    iplocation = request.args.get('iplocation')
    port_status = request.args.get('port_status')

    ip_list, ip_c_set, port_set, port_count_dict,ip_port_list = AssertInfoParser().statistics_ip(
        org_id, domain_address, ip_address, port, content, iplocation, port_status)
    data = []
    data.append('Port: ({})'.format(len(port_set)))
    data.append(','.join([str(x) for x in sorted(port_set)]))

    port_count_list = sorted(port_count_dict.items(),
                             key=lambda x: x[1], reverse=True)
    data.append('\nPort Count:')
    for pc in port_count_list:
        data.append('{:<6}:{}'.format(pc[0], pc[1]))

    data.append('\nNetwork: ({})'.format(len(ip_c_set)))
    data.extend(sorted(ip_c_set))
    data.append('\nIP: ({})'.format(len(ip_list)))
    data.extend(ip_list)
    data.append('\nTarget: ({})'.format(len(ip_port_list)))
    data.extend(ip_port_list)

    response = Response(
        '\n'.join(data), content_type='application/octet-stream')
    response.headers["Content-disposition"] = 'attachment; filename={}'.format(
        "ip-statistics.txt")

    return response
