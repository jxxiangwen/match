#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.preprocess import pre_process_cn
from cn.edu.shu.match.tool import str_list_to_dict
import json
import logging
from time import strftime, localtime

__author__ = 'jxxia'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('log/get_data_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='a')


def get_datas_from_text(require_id, provide_id, algorithm_config, doc_type, algorithm_type, read_file=True,
                        match_need={}, num=10):
    """
    从数据库去除需求或服务数据并预处理
    :param require_id: 全局需求id
    :param provide_id: 全局服务id
    :param algorithm_config: 算法配置文件地址
    :param doc_type: 取出数据的类型
    :param algorithm_type: 匹配时所用算法类型
    :param read_file:通过文件读取匹配所需还是通过match_need读取True为通过文件读取
    :param match_need：匹配所需信息
    :param num: 取出数据的个数
    :return: 预处理后数据
    """
    data, data_index, weight_dict = product_conclude_weight(algorithm_config, doc_type, algorithm_type, read_file,
                                                            match_need)

    return_data = []  # 返回数据
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
        for conclude_index, subscript in enumerate(data_index):
            int_sub = int(subscript)
            if document[int(subscript)]:
                # text += document[int_sub] + ","
                if type(weight_dict) == type({}):
                    text += (document[int_sub] + ",") * int(weight_dict[subscript])
                else:
                    text += (document[int_sub] + ",") * int(weight_dict[conclude_index])
        # logging.warning("第%s篇%s文档文章ID为：%s" % (index, doc_type, document[0]))
        temp_list = list()
        temp_list.append(text)
        return_data.append(pre_process_cn(temp_list)[0])
        # logging.warning("return_data: %s" %return_data)
    return return_data


def get_one_from_text(require_id, provide_id, algorithm_config, doc_type, algorithm_type, read_file=True,
                      match_need={}):
    """
    从数据库去除需求或服务数据并预处理
    :param require_id: 全局需求id
    :param provide_id: 全局服务id
    :param algorithm_config: 算法配置文件地址
    :param doc_type: 取出数据的类型
    :param algorithm_type: 匹配时所用算法类型
    :param read_file:通过文件读取匹配所需还是通过match_need读取True为通过文件读取
    :param match_need：匹配所需信息
    :return: 预处理后数据
    """
    data, data_index, weight_dict = product_conclude_weight(algorithm_config, doc_type, algorithm_type, read_file,
                                                            match_need)
    # logging.debug("data : %s" % data)
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
        for conclude_index, subscript in enumerate(data_index):
            int_sub = int(subscript)
            if document[int_sub]:
                # text += document[int(subscript)] + ","
                if type(weight_dict) == type({}):
                    text += (document[int_sub] + ",") * int(weight_dict[subscript])
                else:
                    text += (document[int_sub] + ",") * int(weight_dict[conclude_index])
        # logging.warning("第%s篇%s文档文章为：%s" % (index, doc_type, document[0]))
        temp_list = list()
        temp_list.append(text)
        yield pre_process_cn(temp_list)[0]


def get_datas_from_keys(doc_type, require_id, provide_id, read_file=True, match_need={}, num=10):
    """

    :param doc_type:取出数据的类型
    :param require_id:全局需求id
    :param provide_id:全局服务id
    :param read_file:通过文件读取匹配所需还是通过match_need读取True为通过文件读取
    :param match_need：匹配所需信息
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
        logging.warning("第%s篇%s文档词为：%s" % (index, doc_type, document[0]))
        return_data.append(document_word)

    return return_data


def get_one_from_keys(doc_type, require_id, provide_id, read_file=True, match_need={}, num=10):
    """

    :param doc_type: 取出数据的类型
    :param require_id: 全局需求id
    :param provide_id: 全局服务id
    :param read_file:通过文件读取匹配所需还是通过match_need读取True为通过文件读取
    :param match_need：匹配所需信息
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
        logging.warning("第%s篇%s文档词为：%s" % (index, doc_type, document[0]))
        document_word = []
        # 提取文档匹配所需信息
        for i in range(2, num * 2, 2):
            #  logging.info("i的值为：%d" % i)
            document_word.append(document[i])
        yield document_word


def product_conclude_weight(algorithm_config, doc_type, algorithm_type, read_file=True, match_need={}):
    """
    产生获取数据函数所需的索引和权重
    :param algorithm_config: 算法配置文件地址
    :param doc_type: 取出数据的类型
    :param algorithm_type: 匹配时所用算法类型
    :param read_file:通过文件读取匹配所需还是通过match_need读取True为通过文件读取
    :param match_need：匹配所需信息
    :return:3元组
    """
    sql = MsSql()
    data = []
    # 读取数据库中表名
    with open('./config/table.json', encoding='utf-8') as table_file:
        table_json = json.load(table_file)
        # 读取算法配置
        with open(algorithm_config, encoding='utf-8') as algorithm_file:
            algorithm_json = json.load(algorithm_file)
            if 'require' == doc_type:
                data = sql.exec_search("select * from %s" % table_json['require'])
                if read_file:
                    # 获得需求表匹配时字段索引
                    require_conclude = algorithm_json[algorithm_type + '_require_conclude'].strip().split(',')
                    logging.warning("require_conclude:%s" % require_conclude)
                    # 获得需求表匹配时字段索引的权重
                    require_weight = algorithm_json[algorithm_type + '_require_weight'].strip().split(',')
                    weight_dict = str_list_to_dict(require_weight)
                    data_index = list(require_conclude)
                else:
                    data_index = match_need['require_conclude']
                    weight_dict = match_need['require_weight']
            elif 'provide' == doc_type:
                data = sql.exec_search("select * from %s" % table_json['provide'])
                if read_file:
                    # 获得服务表匹配时字段索引
                    provide_conclude = algorithm_json[algorithm_type + '_provide_conclude'].strip().split(',')
                    logging.warning("provide_conclude:%s" % provide_conclude)
                    # 获得服务表匹配时字段索引的权重
                    provide_weight = algorithm_json[algorithm_type + '_provide_weight'].strip().split(',')
                    weight_dict = str_list_to_dict(provide_weight)
                    data_index = list(provide_conclude)
                else:
                    data_index = match_need['provide_conclude']
                    weight_dict = match_need['provide_weight']
            else:
                raise ValueError("类型'%s'不存在!" % doc_type)
    return tuple((data, data_index, weight_dict))
