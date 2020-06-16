#!/usr/bin/env python3
# coding: utf-8
# author: xu3352<xu3352@gmail.com>

"""
Python Mysql 工具包
注意事项:
1. %s 为 mysql 占位符; 能用 %s 的地方就不要自己拼接 sql 了
2. sql 里有一个占位符可使用 string 或 number; 有多个占位符可使用 tuple|list
3. insertmany 的时候所有字段使用占位符 %s (预编译), 参数使用 tuple|list
4. queryall 结果集只有一列的情况, 会自动转换为简单的列表 参考:simple_list()
5. queryone 结果集只有一行一列的情况, 自动转为结果数据 参考:simple_value()
6. insertone 插入一条数据, 返回数据ID
7. *_process 重构方法, 方便支持批量数据处理
"""

import pymysql
from DBUtils.PooledDB import PooledDB
# 数据库连接的配置文件保存位置
from instance.config import ProductionConfig
# 日志
import traceback
from nemo.common.utils.loggerutils import logger

#DBUtils连接池
pool = PooledDB(creator=pymysql,
                mincached=1,
                maxcached=20,
                host=ProductionConfig.DB_HOST,
                port=ProductionConfig.DB_PORT,
                user=ProductionConfig.DB_USERNAME,
                password=ProductionConfig.DB_PASSWORD,
                db=ProductionConfig.DB_NAME,
                cursorclass=pymysql.cursors.DictCursor,
                charset='utf8')


def get_connect_cursor():
    """ get connect and cursor 
    """
    try:
        con = connect_mysql()
        cur = con.cursor()
        return con, cur
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("cannot create mysql connect")


def close_cursor_connect(cur, con):
    """ close cursor and connect 
    """
    try:
        cur.close()
        con.close()
        return True
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("cannot close mysql connect or cusor")
    return False


def connect_mysql():
    try:
        return pool.connection()
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("cannot create mysql connect")


def queryone(sql, param=None):
    """返回结果集的第一条数据
    :param sql: sql语句
    :param param: string|tuple|list
    :return: 字典列表 [{}]
    """
    con = connect_mysql()
    cur = con.cursor()
    row = queryone_process(con, cur, sql, param)
    cur.close()
    con.close()
    return row


def queryone_process(con, cur, sql, param=None):
    """" queryone:内部调用 
    """
    row = None
    try:
        cur.execute(sql, param)
        row = cur.fetchone()
    except Exception as e:
        con.rollback()
        logger.error(traceback.format_exc())
        logger.error("[sql]:{} [param]:{}".format(sql, param))
    return simple_value(row)


def queryall(sql, param=None):
    """返回所有查询到的内容 (分页要在sql里写好)
    :param sql: sql语句
    :param param: tuple|list
    :return: 字典列表 [{},{},{}...] or [,,,]
    """
    con = connect_mysql()
    cur = con.cursor()
    rows = queryall_process(con, cur, sql, param)
    cur.close()
    con.close()
    return rows


def queryall_process(con, cur, sql, param=None):
    """" queryall:内部调用 
    """
    rows = None
    try:
        cur.execute(sql, param)
        rows = cur.fetchall()
    except Exception as e:
        con.rollback()
        logger.error(traceback.format_exc())
        logger.error("[sql]:{} [param]:{}".format(sql, param))
    return simple_list(rows)


def insertmany(sql, arrays=None, batch_size=10000):
    """批量插入数据
    :param sql: sql语句
    :param arrays: list|tuple [(),(),()...]
    :param batch_size: 每批入库数量, 超过自动多批入库
    :return: 入库数量
    """
    con = connect_mysql()
    cur = con.cursor()
    cnt = insertmany_process(con, cur, sql, arrays, batch_size)
    cur.close()
    con.close()
    return cnt


def insertmany_process(con, cur, sql, arrays=None, batch_size=10000):
    """ 批量执行 
    """
    return executemany_process(con, cur, sql, arrays, batch_size)


def insertone(sql, param=None):
    """插入一条数据
    :param sql: sql语句
    :param param: string|tuple
    :return: id
    """
    con = connect_mysql()
    cur = con.cursor()
    lastrowid = insertone_process(con, cur, sql, param)
    cur.close()
    con.close()
    return lastrowid


def insertone_process(con, cur, sql, param):
    """ insertone:内部调用 
    """
    lastrowid = 0
    try:
        cur.execute(sql, param)
        con.commit()
        lastrowid = cur.lastrowid
    except Exception as e:
        con.rollback()
        logger.error(traceback.format_exc())
        logger.error("[sql]:{} [param]:{}".format(sql, param))
    return lastrowid


def execute(sql, param=None):
    """
    执行sql语句:修改或删除
    :param sql: sql语句
    :param param: string|list
    :return: 影响数量
    """
    con = connect_mysql()
    cur = con.cursor()
    cnt = execute_process(con, cur, sql, param)
    cur.close()
    con.close()
    return cnt


def execute_process(con, cur, sql, param=None):
    """ execute:内部调用 
    """
    cnt = 0
    try:
        cnt = cur.execute(sql, param)
        con.commit()
    except Exception as e:
        con.rollback()
        logger.error(traceback.format_exc())
        logger.error("[sql]:{} [param]:{}".format(sql, param))
    return cnt


def executemany_process(con, cur, sql, arrays=None, batch_size=10000):
    """ execute批量:内部调用 
    """
    cnt = 0
    try:
        batch_cnt = int(len(arrays) / batch_size) + 1
        for i in range(batch_cnt):
            sub_array = arrays[i * batch_size:(i + 1) * batch_size]
            if sub_array:
                cnt += cur.executemany(sql, sub_array)
                con.commit()
    except Exception as e:
        con.rollback()
        logger.error(traceback.format_exc())
        logger.error("[sql]:{} [param]:{}".format(sql, arrays))
    return cnt


def simple_list(rows):
    """结果集只有一列的情况, 直接使用数据返回
    :param rows: [{'id': 1}, {'id': 2}, {'id': 3}]
    :return: [1, 2, 3]
    """
    if not rows:
        return rows
    if len(rows[0].keys()) == 1:
        simple_list = []
        # print(rows[0].keys())
        key = list(rows[0].keys())[0]
        for row in rows:
            simple_list.append(row[key])
        return simple_list
    return rows


def simple_value(row):
    """结果集只有一行, 一列的情况, 直接返回数据
    :param row: {'count(*)': 3}
    :return: 3
    """
    if not row:
        return None
    if len(row.keys()) == 1:
        # print(row.keys())
        key = list(row.keys())[0]
        return row[key]
    return row


def run_test():
    print("删表:", execute('drop table test_users'))
    sql = '''
            CREATE TABLE `test_users` (
              `id` int(11) NOT NULL AUTO_INCREMENT,
              `email` varchar(255) NOT NULL,
              `password` varchar(255) NOT NULL,
              PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='测试用的, 可以直接删除';
            '''
    print("建表:", execute(sql))

    # 批量插入
    sql_str = "insert into test_users(email, password) values (%s, %s)"
    arrays = [
        ("aaa@126.com", "111111"),
        ("bbb@126.com", "222222"),
        ("ccc@126.com", "333333"),
        ("ddd@126.com", "444444")
    ]
    print("插入数据:", insertmany(sql_str, arrays))

    # 查询
    # 尽量使用limit
    print("只取一行:", queryone("select * from test_users limit %s,%s", (0, 1)))
    print("查询全表:", queryall("select * from test_users"))

    # 条件查询
    print("一列:", queryall("select email from test_users where id <= %s", 2))
    print("多列:", queryall(
        "select * from test_users where email = %s and password = %s", ("bbb@126.com", "222222")))

    # 更新|删除
    print("更新:", execute(
        "update test_users set email = %s where id = %s", ('new@126.com', 1)))
    print("删除:", execute("delete from test_users where id = %s", 4))

    # 查询
    print("再次查询全表:", queryall("select * from test_users"))
    print("数据总数:", queryone("select count(*) from test_users"))
    print('run test complate ...')
