#!/usr/bin/env python3
# coding:utf-8
from . import daobase


class Organization(daobase.DAOBase):
    def __init__(self):
        super().__init__()
        self.table_name = 'organization'
        self.order_by = 'sort_order desc,org_name'
