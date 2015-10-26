#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'jxxia'

from build_sql import MsSql
from preprocess import pre_process_cn
import json
import logging
from time import strftime, localtime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('log/get_data_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='a')


def get_datas_from_text(require_id, provide_id, algorithm_config, doc_type, algorithm_type, num=10):
    """
    从数据库去除需求或服务数据并预处理
    :param require_id: 全局需求id
    :param provide_id: 全局服务id
    :param doc_type: 取出数据的类型
    :param algorithm_config: 算法配置文件地址
    :param algorithm_type: 匹配时所用算法类型
    :param num: 取出数据的个数
    :return: 预处理后数据
    """
    sql = MsSql()
    # 读取数据库中表名
    with open('./config/table.json', encoding='utf-8') as table_file:
        table_json = json.load(table_file)
        # 读取算法配置
        with open(algorithm_config, encoding='utf-8') as algorithm_file:
            algorithm_json = json.load(algorithm_file)
            if 'require' == doc_type:
                data = sql.exec_search("select * from %s" % table_json['require'])
                # 获得需求表匹配时字段索引
                require_need = algorithm_json[algorithm_type + '_require'].strip().split(',')
                data_index = list(require_need)
            elif 'provide' == doc_type:
                data = sql.exec_search("select * from %s" % table_json['provide'])
                # 获得服务表匹配时字段索引
                provide_need = algorithm_json[algorithm_type + '_provide'].strip().split(',')
                data_index = list(provide_need)
            else:
                raise ValueError("类型'%s'不存在!" % doc_type)
            return_data = []

            for index, document in enumerate(data):
                # 存储文档序号顺序
                if 'require' == doc_type:
                    require_id.append(document[0])
                elif 'provide' == doc_type:
                    provide_id.append(document[0])
                else:
                    raise ValueError
                text = ""
                # 提取文档匹配所需信息
                for subscript in data_index:
                    subscript = int(subscript)
                    if document[subscript]:
                        text += document[subscript] + ","
                logging.warning("第%s篇%s文档文章ID为：%s" % (index, doc_type, document[0]))
                temp_list = []
                temp_list.append(text)
                return_data.append(pre_process_cn(temp_list)[0])
                logging.warning("return_data: %s" %return_data)
            return return_data


def get_one_from_text(require_id, provide_id, algorithm_config, doc_type, algorithm_type):
    """
    从数据库去除需求或服务数据并预处理
    :param require_id: 全局需求id
    :param provide_id: 全局服务id
    :param algorithm_config: 算法配置文件地址
    :param doc_type: 取出数据的类型
    :param algorithm_type: 匹配时所用算法类型
    :return: 预处理后数据
    """
    sql = MsSql()
    # 读取数据库中表名
    with open('./config/table.json', encoding='utf-8') as table_file:
        table_json = json.load(table_file)
        # 读取算法配置
        with open(algorithm_config, encoding='utf-8') as algorithm_file:
            algorithm_json = json.load(algorithm_file)
            if 'require' == doc_type:
                data = sql.exec_search("select * from %s" % table_json['require'])
                # 获得需求表匹配时字段索引
                require_need = algorithm_json[algorithm_type + '_require'].strip().split(',')
                logging.debug("require_need:%s"%require_need)
                data_index = list(require_need)
            elif 'provide' == doc_type:
                logging.debug("select * from %s" % table_json['provide'])
                data = sql.exec_search("select * from %s" % table_json['provide'])
                # 获得服务表匹配时字段索引
                provide_need = algorithm_json[algorithm_type + '_provide'].strip().split(',')
                logging.debug("provide_need:%s"%provide_need)
                data_index = list(provide_need)
            else:
                raise ValueError("类型'%s'不存在!" % doc_type)
            logging.debug("data : %s" % data)
            for index, document in enumerate(data):
                # 存储文档序号顺序
                if 'require' == doc_type:
                    require_id.append(document[0])
                elif 'provide' == doc_type:
                    provide_id.append(document[0])
                else:
                    raise ValueError
                text = ""
                # 提取文档匹配所需信息
                for subscript in data_index:
                    subscript = int(subscript)
                    if document[subscript]:
                        text += document[subscript] + ","
                logging.debug("第%s篇%s文档文章为：%s" % (index, doc_type, document[0]))
                temp_list = []
                temp_list.append(text)
                yield pre_process_cn(temp_list)[0]


def get_datas_from_keys(doc_type, require_id, provide_id, num=10):
    """

    :param doc_type:取出数据的类型
    :param require_id:全局需求id
    :param provide_id:全局服务id
    :param num:取出数据的个数
    :return:预处理后数据
    """
    sql = MsSql()
    if 'require' == doc_type:
        data = sql.exec_search("select * from RequireDocKeyWs")
    elif 'provide' == doc_type:
        data = sql.exec_search("select * from ProvideDocKeyWs")
    else:
        raise ValueError
    return_data = []
    for index, document in enumerate(data):
        # 存储文档序号顺序
        if 'require' == doc_type:
            require_id.append(document[0])
        elif 'provide' == doc_type:
            provide_id.append(document[0])
        else:
            raise ValueError
        document_word = []
        # 提取文档匹配所需信息
        for i in range(2, num * 2, 2):
            document_word.append(document[i])
        logging.debug("第%s篇%s文档词为：%s" % (index, doc_type, document[0]))
        return_data.append(document_word)

    return return_data


def get_one_from_keys(doc_type, require_id, provide_id, num=10):
    """

    :param doc_type: 取出数据的类型
    :param require_id: 全局需求id
    :param provide_id: 全局服务id
    :param num: 取出数据的个数
    :return:预处理后数据
    """
    sql = MsSql()
    if 'require' == doc_type:
        data = sql.exec_search("select * from RequireDocKeyWs")
    elif 'provide' == doc_type:
        data = sql.exec_search("select * from ProvideDocKeyWs")
    else:
        raise ValueError
    logging.info("data : %s" % data)
    for index, document in enumerate(data):
        # 存储文档序号顺序
        if 'require' == doc_type:
            require_id.append(document[0])
        elif 'provide' == doc_type:
            provide_id.append(document[0])
        else:
            raise ValueError
        logging.debug("第%s篇%s文档词为：%s" % (index, doc_type, document[0]))
        document_word = []
        # 提取文档匹配所需信息
        for i in range(2, num * 2, 2):
            #  logging.info("i的值为：%d" % i)
            document_word.append(document[i])
        yield document_word
