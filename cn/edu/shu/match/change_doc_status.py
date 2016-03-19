#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os

module_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir, os.pardir, os.pardir))
sys.path.append(module_path)

from cn.edu.shu.match.build_sql import MsSql
import json, datetime, time

__author__ = 'jxxia'

ms_sql = MsSql()


def get_date(date_str):
    """
    通过日期字符串返回日期元组
    :param date_str: 日期字符串
    :return:
    """
    t = time.strptime(date_str, "%Y-%m-%d")  # struct_time类型
    return datetime.datetime(t[0], t[1], t[2])


def change_require_status():
    """
    更新需求状态
    :return:
    """
    with open('./config/require_table.json', encoding='utf-8') as require_table_file:
        require_table_json = json.load(require_table_file)
        results = ms_sql.exec_search(
            "SELECT {},{},{},{} FROM {} WHERE {} BETWEEN 1 AND 3 AND {} < getdate() ".format(
                require_table_json['require_id'],
                require_table_json['require_start_time'],
                require_table_json['require_finish_time'],
                require_table_json['require_status'],
                require_table_json['require'],
                require_table_json['require_status'],
                require_table_json['require_start_time']
            ))
        print("SELECT {},{},{},{} FROM {} WHERE {} BETWEEN 1 AND 3 AND {} < getdate() ".format(
            require_table_json['require_id'],
            require_table_json['require_start_time'],
            require_table_json['require_finish_time'],
            require_table_json['require_status'],
            require_table_json['require'],
            require_table_json['require_status'],
            require_table_json['require_start_time']))
        status = 0
        for result in results:
            # 暂存文档不修改状态
            if 3 < result[3] or 4 > len(result):
                continue
            # 文档是否开始，2为已开始
            if datetime.datetime.now() > get_date(result[1]):
                status = 2
                # 文档是否结束，3为已结束
                if datetime.datetime.now() > get_date(result[2]):
                    status = 3
                if status > result[3] and status != 0:
                    print("UPDATE {} SET {} = {} WHERE {} = {}".format(require_table_json['require'],
                                                                       require_table_json['require_status'],
                                                                       status,
                                                                       require_table_json['require_id'],
                                                                       result[0]))
                    print("原状态%s", result[3])
                    ms_sql.exec_non_search(
                        "UPDATE {} SET {} = {} WHERE {} = {}".format(require_table_json['require'],
                                                                     require_table_json['require_status'],
                                                                     status,
                                                                     require_table_json['require_id'],
                                                                     result[0]))


def change_provide_status():
    """
    更新服务状态
    :return:
    """
    with open('./config/provide_table.json', encoding='utf-8') as provide_table_file:
        provide_table_json = json.load(provide_table_file)
        results = ms_sql.exec_search(
            "SELECT {},{},{} FROM {} WHERE {} BETWEEN 1 AND 3 AND {} < getdate()".format(
                provide_table_json['provide_id'],
                provide_table_json['provide_start_time'],
                provide_table_json['provide_status'],
                provide_table_json['provide'],
                provide_table_json['provide_status'],
                provide_table_json['provide_start_time']
            ))
        print("SELECT {},{},{} FROM {} WHERE {} BETWEEN 1 AND 3 AND {} < getdate()".format(
            provide_table_json['provide_id'],
            provide_table_json['provide_start_time'],
            provide_table_json['provide_status'],
            provide_table_json['provide'],
            provide_table_json['provide_status'],
            provide_table_json['provide_start_time']
        ))
        status = 0
        for result in results:
            # 暂存文档不修改状态
            if 4 < result[2]:
                continue
            # 文档是否开始，2为已开始
            if datetime.datetime.now() > get_date(result[1]):
                status = 2
                if status > result[2] and status != 0:
                    print("UPDATE {} SET {} = {} WHERE {} = {}".format(provide_table_json['provide'],
                                                                       provide_table_json['provide_status'],
                                                                       status,
                                                                       provide_table_json['provide_id'],
                                                                       result[0]))
                    print("原状态%s", result[2])
                    ms_sql.exec_non_search(
                        "UPDATE {} SET {} = {} WHERE {} = {}".format(provide_table_json['provide'],
                                                                     provide_table_json['provide_status'],
                                                                     status,
                                                                     provide_table_json['provide_id'],
                                                                     result[0]))


if __name__ == '__main__':
    while True:
        start = time.clock()
        change_require_status()
        change_provide_status()
        end = time.clock()
        time_sleep = 3600 * 24 - (end - start)
        if 0 < time_sleep:
            time.sleep(time_sleep)
