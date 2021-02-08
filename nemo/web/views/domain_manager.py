#!/usr/bin/env python3
# coding:utf-8
import traceback

from flask import Blueprint
from flask import Response
from flask import jsonify
from flask import render_template
from flask import request
from flask import session

from nemo.common.utils.assertexport import export_domains
from nemo.common.utils.assertinfoparser import AssertInfoParser
from nemo.common.utils.loggerutils import logger
from nemo.core.database.attr import DomainAttr
from nemo.core.database.colortag import DomainColorTag
from nemo.core.database.domain import Domain
from nemo.core.database.memo import DomainMemo
from nemo.core.database.organization import Organization
from nemo.core.database.vulnerability import Vulnerability
from nemo.core.tasks.poc.pocsuite3 import Pocsuite3
from nemo.core.tasks.poc.xray import XRay
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
        org_list.insert(0, {'id': '', 'org_name': '--全部--'})

        data = {'org_list': org_list, 'domain_address': session.get('domain_address', default=''),
                'ip_address_domain': session.get('ip_address_domain', default=''),
                'session_org_id': session.get('session_org_id', default=''),
                'pocsuite3_poc_files': Pocsuite3().load_poc_files(), 'xray_poc_files': XRay().load_poc_files()
                }

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
        color_tag = request.form.get('color_tag')
        memo_content = request.form.get('memo_content')
        date_delta = request.form.get('date_delta')

        session['ip_address_domain'] = ip_address
        session['domain_address'] = domain_address
        session['session_org_id'] = org_id

        count = 0
        domains = domain_table.gets_by_search(org_id, domain_address, ip_address, color_tag, memo_content, date_delta,
                                              page=start // length + 1, rows_per_page=length)
        if domains:
            for domain_row in domains:
                ips = domain_attr_table.gets(
                    query={'tag': 'A', 'r_id': domain_row['id']})
                domain_info = api.get_domain_info(domain_row['id'])
                # 获取关联的漏洞信息：
                vul_info = []
                vul_results = Vulnerability().gets({'target': domain_row['domain']})
                if vul_results and len(vul_results) > 0:
                    for v in vul_results:
                        vul_info.append('{}/{}'.format(v['poc_file'], v['source']))
                domain_list.append({
                    "id": domain_row['id'],
                    "index": index + start,
                    "color_tag": domain_info['color_tag'],
                    "memo_content": domain_info['memo'],
                    "domain": domain_row['domain'],
                    "ip": ', '.join(set(
                        ['<a href="/ip-info?ip={0}" target="_blank">{0}</a>'.format(ip_row['content']) for ip_row in
                         ips])),
                    "org_name": org_table.get(int(domain_row['org_id']))['org_name'] if domain_row['org_id'] else '',
                    "create_time": str(domain_row['create_datetime']),
                    "update_time": str(domain_row['update_datetime']),
                    'port': domain_info['port'],
                    'title': ', '.join(domain_info['title']),
                    'banner': ', '.join(domain_info['banner']),
                    'vulnerability': '\r\n'.join(vul_info)
                })
                index += 1
            count = domain_table.count_by_search(
                org_id, domain_address, ip_address, color_tag, memo_content, date_delta)
        json_data = {
            'draw': draw,
            'recordsTotal': count,
            'recordsFiltered': count,
            'data': domain_list
        }
    except Exception as e:
        logger.error(traceback.format_exc())
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
    color_tag = request.args.get('color_tag')
    memo_content = request.args.get('memo_content')
    date_delta = request.args.get('date_delta')

    data = export_domains(org_id, domain_address,
                          ip_address, color_tag, memo_content, date_delta)
    response = Response(data, content_type='application/octet-stream')
    response.headers["Content-disposition"] = 'attachment; filename={}'.format(
        "domain-export.xlsx")

    return response


@domain_manager.route('/domain-color-tag/<int:r_id>', methods=['POST'])
@login_check
def mark_ip_tag_color(r_id):
    '''对IP进行颜色标记
    '''
    color_tag_app = DomainColorTag()
    color = request.form.get('color')
    # 清除标记
    if color == 'DELETE':
        color_tag_app.delete(r_id)
        return jsonify({'status': 'success'})
    # 标记颜色
    data = {'r_id': r_id, 'color': color}
    obj_id = color_tag_app.save_and_update(data)
    ret_status = {'status': 'success' if obj_id else 'fail'}

    return jsonify(ret_status)


@domain_manager.route('/domain-memo/<int:r_id>', methods=['GET', 'POST'])
@login_check
def ip_memo(r_id):
    '''读取和保存IP的备忘录信息
    '''
    memo_app = DomainMemo()
    # 读取备忘录信息
    if request.method == 'GET':
        meno_obj = memo_app.get(r_id)
        memo_content = meno_obj['content'] if meno_obj else ''

        return {'status': 'success', 'content': memo_content}
    # 保存更新备忘录信息
    memo = request.form.get('memo')
    obj_id = memo_app.save_and_update({'r_id': r_id, 'content': memo})
    ret_status = {'status': 'success' if obj_id else 'fail'}

    return jsonify(ret_status)


@domain_manager.route('/domain-memo-export', methods=['GET'])
@login_check
def domain_memo_export_view():
    '''导出域名的备忘录信息
    '''
    org_id = request.args.get('org_id')
    ip_address = request.args.get('ip_address')
    domain_address = request.args.get('domain_address')
    color_tag = request.args.get('color_tag')
    memo_content = request.args.get('memo_content')
    date_delta = request.args.get('date_delta')

    memo_list = AssertInfoParser().export_domain_memo(
        org_id, domain_address, ip_address, color_tag, memo_content, date_delta)
    response = Response(
        '\n'.join(memo_list), content_type='application/octet-stream')
    response.headers["Content-disposition"] = 'attachment; filename={}'.format(
        "domain-memo.txt")

    return response
