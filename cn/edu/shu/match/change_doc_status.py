#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
            "SELECT {},{},{},{} FROM {} WHERE {} < getdate()".format(require_table_json['require_id'],
                                                                     require_table_json['require_start_time'],
                                                                     require_table_json['require_finish_time'],
                                                                     require_table_json['require_status'],
                                                                     require_table_json['require'],
                                                                     require_table_json['require_start_time']))
        status = 0
        for result in results:
            if get_date(result[1]) < datetime.datetime.now():
                status = 2
                if get_date(result[2]) < datetime.datetime.now():
                    status = 3
                if status != result[3]:
                    print("UPDATE {} SET {} = {} WHERE {} = {}".format(require_table_json['require'],
                                                                      require_table_json['require_status'],
                                                                      status,
                                                                      require_table_json['require_id'],
                                                                      result[0]))
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
            "SELECT {},{},{} FROM {} WHERE {} < getdate()".format(provide_table_json['provide_id'],
                                                                  provide_table_json['provide_start_time'],
                                                                  provide_table_json['provide_status'],
                                                                  provide_table_json['provide'],
                                                                  provide_table_json['provide_start_time']))
        status = 0
        for result in results:
            if get_date(result[1]) < datetime.datetime.now():
                status = 2
                if status != result[2]:
                    print("UPDATE {} SET {} = {} WHERE {} = {}".format(provide_table_json['provide'],
                                                                      provide_table_json['provide_status'],
                                                                      status,
                                                                      provide_table_json['provide_id'],
                                                                      result[0]))
                    ms_sql.exec_non_search(
                        "UPDATE {} SET {} = {} WHERE {} = {}".format(provide_table_json['provide'],
                                                                    provide_table_json['provide_status'],
                                                                    status,
                                                                    provide_table_json['provide_id'],
                                                                    result[0]))


if __name__ == '__main__':
    change_require_status()
    change_provide_status()
