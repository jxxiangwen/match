#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.process.preprocess import pre_process_cn
from cn.edu.shu.match.tool import str_list_to_dict
import cn.edu.shu.match.global_variable as gl
from time import strftime, localtime
import logging
import json
import os
import sys

for a_path in sys.path:
    if os.path.exists(os.path.join(a_path, 'cn', 'edu', 'shu', 'match')):
        os.chdir(os.path.join(a_path, 'cn', 'edu', 'shu', 'match'))
        break

__author__ = 'jxxia'

logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('log/get_data_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='a')


def get_data_from_text(doc_id, algorithm_config_path, doc_type):
    """
    从数据库去除需求或服务数据并预处理
    :param doc_id: 文档id
    :param algorithm_config_path: 算法配置文件地址
    :param doc_type: 取出数据的类型
    :return: 预处理后数据
    """
    data, data_index = product_conclude(doc_id, algorithm_config_path, doc_type)
    return_data = list()  # 返回数据
    for document in data:
        text = str()
        # 提取文档匹配所需信息
        for conclude_index, subscript in enumerate(data_index):
            int_sub = int(subscript)
            if document[int_sub]:
                if gl.default_industry_name != document[int_sub]:
                    text += document[int_sub] + ","
        # logging.warning("第%s篇%s文档文章ID为：%s" % (index, doc_type, document[0]))
        text_list = list()
        text_list.append(text)
        return_data.append(text_list)
        # print("return_data: %s" % return_data)
        # logging.warning("return_data: %s" % return_data)
    return return_data


def get_one_from_text(doc_id, algorithm_config, doc_type):
    """
    从数据库去除需求或服务数据并预处理
    :param doc_id: 文档id
    :param algorithm_config: 算法配置文件地址
    :param doc_type: 取出数据的类型
    :return: 预处理后数据
    """
    data, data_index = product_conclude(doc_id, algorithm_config, doc_type)

    # 去掉不在文档id中的数据
    for document in data:
        if document[0] not in doc_id:
            data.remove(document)
    for document in data:
        text = str()
        # 提取文档匹配所需信息
        for conclude_index, subscript in enumerate(data_index):
            int_sub = int(subscript)
            if document[int(subscript)]:
                text += document[int_sub] + ","
        # logging.warning("第%s篇%s文档文章ID为：%s" % (index, doc_type, document[0]))
        yield pre_process_cn(list(text))


def product_conclude(doc_id, algorithm_config_path, doc_type):
    """
    产生获取数据函数所需的索引和权重
    :param doc_id: 文档id
    :param algorithm_config_path: 算法配置文件地址
    :param doc_type: 取出数据的类型
    :return: 2元组
    """
    sql = MsSql()
    data = list()  # 保存数据
    data_index = list()  # 保存文档匹配所需数据在表中索引号
    # 读取数据库中表名
    with open('./config/table.json', encoding='utf-8') as table_file:
        table_json = json.load(table_file)
        # 读取算法配置
        with open(algorithm_config_path, encoding='utf-8') as algorithm_file:
            algorithm_json = json.load(algorithm_file)
            if not ('require' == doc_type or 'provide' == doc_type):
                raise ValueError("类型{}不存在!".format(doc_type))
            if 'require' == doc_type:
                if isinstance(doc_id, int):
                    data = sql.exec_search(
                        'SELECT * FROM {} WHERE {} = {}'.format(table_json[doc_type], table_json['require_id'], doc_id))
                else:
                    print('SELECT * FROM {} WHERE {} IN {}'.format(table_json[doc_type], table_json['require_id'],
                                                                   tuple(doc_id)))
                    data = sql.exec_search(
                        'SELECT * FROM {} WHERE {} IN {}'.format(table_json[doc_type], table_json['require_id'],
                                                                 tuple(doc_id)))
            else:
                if isinstance(doc_id, int):
                    data = sql.exec_search(
                        'SELECT * FROM {} WHERE {} == {}'.format(table_json[doc_type], table_json['provide_id'],
                                                                 doc_id))
                else:
                    print('SELECT * FROM {} WHERE {} IN {}'.format(table_json[doc_type], table_json['provide_id'],
                                                                   tuple(doc_id)))
                    data = sql.exec_search(
                        'SELECT * FROM {} WHERE {} IN {}'.format(table_json[doc_type], table_json['provide_id'],
                                                                 tuple(doc_id)))
            # 获得需求表匹配时字段索引
            conclude = algorithm_json['{}_conclude'.format(doc_type)].strip().split(',')
            # logging.warning('{}_conclude:%s'.format(conclude))
            data_index = list(conclude)
    return tuple((data, data_index))
