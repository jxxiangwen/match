#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'jxxia'

from build_sql import MsSql
import json
import logging
from time import strftime, localtime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('log/save_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='a')


def save_to_database(require_id, provide_id, result, src):
    """
    保存匹配结果到数据库
    :param require_id: 全局需求id
    :param provide_id: 全局服务id
    :param result: 匹配结果数据
    :param src: 匹配源文档类型
    :return:保存结果
    """
    from time import strftime, localtime
    sql = MsSql()
    with open('./config/table.json', encoding='utf-8') as table_file:
        table_json = json.load(table_file)
        sql.exec_search("select * from %s" % table_json['match'])
        # print("require_id:",require_id)
        # print("provide_id:",provide_id)
        if 'require' == src:
            for index, data in enumerate(result):
                for doc_id, cosine in data:
                    # print("index : %s ,doc_id: %s" %(index,doc_id))
                    # 如果余弦距离大于0.97且数据库中此记录不存在，则插入数据库
                    if cosine > 0.97:
                        with open('./config/database.json', encoding='utf-8') as database_file:
                            database_json = json.load(database_file)
                            yours = database_json['yours'].lower()
                            logging.debug("yours : %s" % yours)
                            if 'ture' != yours:
                                with open('./config/table.json', encoding='utf-8') as table_file:
                                    table_json = json.load(table_file)
                                    require_data = sql.exec_search("select %s from %s where %s = %d" % (
                                        table_json['require_user_id'], table_json['require'],
                                        table_json['require_id'], require_id[doc_id]))
                                    logging.debug("select %s from %s where %s = %d" % (
                                        table_json['require_user_id'], table_json['require'],
                                        table_json['require_id'], require_id[doc_id]))
                                    if require_data:
                                        logging.debug("require_data : %s" % require_data)
                                        for (require_user_id) in require_data:
                                            provide_data = sql.exec_search("select %s from %s where %s = %d" % (
                                                table_json['provide_user_id'], table_json['provide'],
                                                table_json['provide_id'], provide_id[index]))
                                            if provide_data:
                                                for (provide_user_id) in provide_data:
                                                    if provide_user_id == require_user_id:
                                                        logging.debug("需求和服务是同一用户发布的，该用户id为 : %s" % require_user_id)
                                                        return
                        if not sql.exec_search(
                                        "select * from %s where %s = %d and %s = %d" % (
                                        table_json['match'], table_json['match_require_id'],
                                        require_id[doc_id], table_json['match_provide_id'], provide_id[index])):
                            # logging.debug("INSERT INTO DocMatchInfor ([DocMatchInfor_ReqID], [DocMatchInfor_ProID], [DocMatchInfor_Degree], [DocMatchInfor_Status], [DocMatchInfor_CreateDate], [DocMatchInfor_ReqRead], [DocMatchInfor_ProRead]) VALUES ('%s', '%s', '%s', '0', '%s', '0', '0')" %(require_id[doc_id], provide_id[index], degree[round(cosine * 100)], strftime('%Y-%m-%d %H:%M:%S', localtime())))
                            sql.exec_non_search(
                                "INSERT INTO %s (%s, %s, %s, %s, %s, %s, %s) VALUES ('%s', '%s', '%s', '0', '%s', '0', '0')" % (
                                    table_json['match'], table_json['match_require_id'],
                                    table_json['match_provide_id'],
                                    table_json['match_degree'],
                                    table_json['match_status'], table_json['match_create_time'],
                                    table_json['match_req_read'],
                                    table_json['match_pro_read'],
                                    require_id[doc_id], provide_id[index], degree_transform(round(cosine * 100)),
                                    strftime('%Y-%m-%d %H:%M:%S', localtime())))
        elif 'provide' == src:
            for index, data in enumerate(result):
                for doc_id, cosine in data:
                    # logging.debug("index : %s ,doc_id: %s" %(index,doc_id))
                    if cosine > 0.97:
                        with open('./config/database.json', encoding='utf-8') as database_file:
                            database_json = json.load(database_file)
                            yours = database_json['yours'].lower()
                            logging.debug("yours : %s" % yours)
                            if 'ture' != yours:
                                with open('./config/table.json', encoding='utf-8') as table_file:
                                    table_json = json.load(table_file)
                                    require_data = sql.exec_search("select %s from %s where %s = %d" % (
                                        table_json['require_user_id'], table_json['require'],
                                        table_json['require_id'], require_id[doc_id]))
                                    logging.debug("select %s from %s where %s = %d" % (
                                        table_json['require_user_id'], table_json['require'],
                                        table_json['require_id'], require_id[doc_id]))
                                    if require_data:
                                        logging.debug("require_data : %s" % require_data)
                                        for (require_user_id) in require_data:
                                            provide_data = sql.exec_search("select %s from %s where %s = %d" % (
                                                table_json['provide_user_id'], table_json['provide'],
                                                table_json['provide_id'], provide_id[index]))
                                            if provide_data:
                                                for (provide_user_id) in provide_data:
                                                    if provide_user_id == require_user_id:
                                                        logging.debug("需求和服务是同一用户发布的，该用户id为 : %s" % require_user_id)
                                                        return
                        if not sql.exec_search(
                                        "select * from %s where %s = %d and %s = %d" % (
                                        table_json['match'], table_json['match_require_id'],
                                        require_id[index], table_json['match_provide_id'], provide_id[doc_id])):
                            sql.exec_non_search(
                                "INSERT INTO %s (%s, %s, %s, %s, %s, %s, %s) VALUES ('%s', '%s', '%s', '0', '%s', '0', '0')" % (
                                    table_json['match'], table_json['match_require_id'],
                                    table_json['match_provide_id'],
                                    table_json['match_degree'],
                                    table_json['match_status'], table_json['match_create_time'],
                                    table_json['match_req_read'],
                                    table_json['match_pro_read'],
                                    require_id[index], provide_id[doc_id], degree_transform(round(cosine * 100)),
                                    strftime('%Y-%m-%d %H:%M:%S', localtime())))
        else:
            raise ValueError


def degree_transform(degree):
    """
    将余弦相似度转化为匹配度
    :param degree: 余弦相似度
    :return:匹配度
    """
    with open('./config/degree.json', encoding='utf-8') as degree_file:
        degree_json = json.load(degree_file)
        return degree_json[str(int(degree))]
