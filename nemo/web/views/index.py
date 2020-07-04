#!/usr/bin/env python3
#coding:utf-8

from flask import Blueprint, redirect, url_for

from .authenticate import login_check

index = Blueprint('index', __name__)

@index.route('/index', methods = ['GET'])
@login_check
def view_index():
    return redirect(url_for('dashboard.view_dashboard'))

@index.route('/', methods = ['GET'])
@login_check
def view_base():
    return redirect(url_for('dashboard.view_dashboard'))
