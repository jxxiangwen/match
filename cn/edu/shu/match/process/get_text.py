#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.process.preprocess import pre_process_cn
from cn.edu.shu.match.tool import str_list_to_dict
from time import strftime, localtime
import logging,json

__author__ = 'jxxia'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('log/get_data_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='a')


def get_data_from_text(doc_id, algorithm_config, doc_type, algorithm_type, read_file=True,
                       match_need=dict()):
    """
    从数据库去除需求或服务数据并预处理
    :param doc_id: 文档id
    :param algorithm_config: 算法配置文件地址
    :param doc_type: 取出数据的类型
    :param algorithm_type: 匹配时所用算法类型
    :param read_file: 通过文件读取匹配所需还是通过match_need读取True为通过文件读取
    :param match_need：匹配所需信息
    :return: 预处理后数据
    """
    data, data_index, weight_dict = product_conclude_weight(algorithm_config, doc_type, algorithm_type, read_file,
                                                            match_need)

    return_data = list()  # 返回数据
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
                # text += document[int_sub] + ","
                if isinstance(weight_dict, dict):
                    text += (document[int_sub] + ",") * int(weight_dict[subscript])
                else:
                    text += (document[int_sub] + ",") * int(weight_dict[conclude_index])
        # logging.warning("第%s篇%s文档文章ID为：%s" % (index, doc_type, document[0]))
        text_list = list()
        text_list.append(text)
        return_data.append(pre_process_cn(text_list)[0])
        # logging.warning("return_data: %s" %return_data)
    return return_data


def get_one_from_text(doc_id, algorithm_config, doc_type, algorithm_type, read_file=True,
                      match_need=dict()):
    """
    从数据库去除需求或服务数据并预处理
    :param doc_id: 文档id
    :param algorithm_config: 算法配置文件地址
    :param doc_type: 取出数据的类型
    :param algorithm_type: 匹配时所用算法类型
    :param read_file: 通过文件读取匹配所需还是通过match_need读取True为通过文件读取
    :param match_need：匹配所需信息
    :return: 预处理后数据
    """
    data, data_index, weight_dict = product_conclude_weight(algorithm_config, doc_type, algorithm_type, read_file,
                                                            match_need)

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
                # text += document[int_sub] + ","
                if isinstance(weight_dict, dict):
                    text += (document[int_sub] + ",") * int(weight_dict[subscript])
                else:
                    text += (document[int_sub] + ",") * int(weight_dict[conclude_index])
        # logging.warning("第%s篇%s文档文章ID为：%s" % (index, doc_type, document[0]))
        yield pre_process_cn(list(text))


def product_conclude_weight(algorithm_config_path, doc_type, algorithm_type, read_file=True, match_need=dict()):
    """
    产生获取数据函数所需的索引和权重
    :param algorithm_config_path: 算法配置文件地址
    :param doc_type: 取出数据的类型
    :param algorithm_type: 匹配时所用算法类型
    :param read_file: 通过文件读取匹配所需还是通过match_need读取True为通过文件读取
    :param match_need：匹配所需信息
    :return: 3元组
    """
    sql = MsSql()
    data = list()  # 保存数据
    data_index = list()  # 保存文档匹配所需数据在表中索引号
    weight_dict = dict()  # 保存文档匹配所需数据相应权重
    # 读取数据库中表名
    with open('./config/table.json', encoding='utf-8') as table_file:
        table_json = json.load(table_file)
        # 读取算法配置
        with open(algorithm_config_path, encoding='utf-8') as algorithm_file:
            algorithm_json = json.load(algorithm_file)
            if not ('require' == doc_type or 'provide' == doc_type):
                raise ValueError("类型{}不存在!".format(doc_type))
            data = sql.exec_search('select * from {}'.format(table_json[doc_type]))
            if read_file:
                # 获得需求表匹配时字段索引
                conclude = algorithm_json['{}_{}_conclude'.format(algorithm_type, doc_type)].strip().split(',')
                logging.warning('{}_conclude:%s'.format(conclude))
                # 获得需求表匹配时字段索引的权重
                weight = algorithm_json['{}_{}_weight'.format(algorithm_type, doc_type)].strip().split(',')
                weight_dict = str_list_to_dict(weight)
                data_index = list(conclude)
            else:
                assert len(match_need) > 0, "匹配所需数据不能为空"
                data_index = match_need['{}_conclude'.format(doc_type)]
                weight_dict = match_need['{}_weight'.format(doc_type)]
                # weight_dict = str_list_to_dict(','.join(match_need['{}_weight'.format(doc_type)]))
    return tuple((data, data_index, weight_dict))
