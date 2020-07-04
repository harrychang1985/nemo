#!/usr/bin/env python3
# coding:utf-8

from flask import request
from flask import render_template
from flask import Blueprint
from flask import jsonify

from nemo.core.database.organization import Organization

from .authenticate import login_check

org_manager = Blueprint("org_manager", __name__)


@org_manager.route('/org-add', methods=['GET', 'POST'])
@login_check
def org_add_view():
    '''添加组织机构
    '''
    if request.method == 'GET':
        return render_template('org-add.html')

    org_table = Organization()
    org_name = request.form['org_name'].encode('utf-8')
    sort_order = request.form['sort_order']
    data = {
        'org_name': org_name,
        'status': request.form['status'],
        'sort_order': sort_order
    }
    row_id = org_table.add(data)

    return jsonify({'status': 'success', 'msg': row_id})


@org_manager.route('/org-update/<int:org_id>', methods=['POST'])
@login_check
def org_update_view(org_id):
    '''修改组织机构
    '''
    org_table = Organization()
    org_name = request.form['org_name'].encode('utf-8')
    sort_order = request.form['sort_order']
    data = {
        'org_name': org_name,
        'status': request.form['status'],
        'sort_order': sort_order
    }
    row_id = org_table.update(org_id, data)

    return jsonify({'status': 'success', 'msg': row_id})


@org_manager.route('/org-delete/<int:org_id>', methods=['POST'])
@login_check
def org_delete_view(org_id):
    '''删除组织机构
    '''
    org_table = Organization()
    del_rows = org_table.delete(org_id)

    return jsonify({'status': 'success', 'msg': str(del_rows)})


@org_manager.route('/org-get/<int:org_id>', methods=['POST'])
@login_check
def org_get_view(org_id):
    '''根据ID获取一个组织机构
    '''
    org_table = Organization()
    org_row = org_table.get(org_id)

    return jsonify(org_row)


@org_manager.route('/org-list', methods=['GET', 'POST'])
@login_check
def org_list_view():
    '''组织机构列表展示
    '''
    if request.method == 'GET':
        return render_template('org-list.html')

    org_table = Organization()
    org_list = []
    json_data = {}
    index = 1

    try:
        draw = int(request.form.get('draw'))
        start = int(request.form.get('start'))
        length = int(request.form.get('length'))
        for org in org_table.gets(page=(start//length) + 1, rows_per_page=length):
            org_list.append({
                "id": org['id'],
                'index': index+start,
                'org_name': org['org_name'],
                'status': org['status'],
                'sort_order': org['sort_order'],
                'create_time': str(org['create_datetime']),
                'update_time': str(org['update_datetime'])
            })
            index += 1
        count = org_table.count()
        json_data = {
            'draw': draw,
            'recordsTotal': count,
            'recordsFiltered': count,
            'data': org_list,
        }
    except Exception as e:
        print(e)

    return jsonify(json_data)
