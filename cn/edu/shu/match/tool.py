#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import datetime, json

__author__ = 'jxxia'


def str_list_to_dict(str_list):
    """
    将key-value类型的字符串列表转化为词典
    :param str_list:字符串的列表
    :return:转化后的词典
    """
    return_dict = {}
    for item in str_list:
        temp_list = item.strip().split('-')
        return_dict[temp_list[0]] = temp_list[1]
    return return_dict


def dict_to_str(concludes, weights):
    """
    将词典转化为key-value类型的字符串
    :param conclude:包含的索引
    :param weight:权重
    :return:转化后的词典
    """
    if 0 == len(concludes) or 0 == len(weights) or len(concludes) != len(weights):
        raise ValueError("传入内容不能为空")
    return_str = str()
    remove_last_comma = slice(0, -1)
    for index, conclude in enumerate(concludes):
        return_str += str(conclude) + '-' + str(weights[index]) + ','
    return return_str[remove_last_comma]


def str_value_to_int_list(str_value):
    """
    将形如"1,2,3,4"类型的字符串转化[1,2,3,4]的列表
    :param str_value:字符串
    :return:转化后的词典
    """
    if not isinstance(str_value, str):
        raise TypeError("{}不是字符串类型".format(str_value))
    temp_list = str_value.strip().split(',')
    temp_list = [int(value) for value in temp_list]
    return temp_list


def get_mssql_time(a_time):
    """
    将a_time转化为可用于MSsql的时间
    :param a_time: 要转化的时间
    :return:转化后的时间
    """
    if isinstance(a_time, type(datetime.datetime.now())):
        cut_redundant_millisecond = slice(0, -3)  # 去掉多余的3位毫秒
        return str(a_time)[cut_redundant_millisecond]
    else:
        raise TypeError("{}不是{}类型".format(a_time, type(datetime.datetime.now())))


def change_json_file(file_path, **kw):
    """
    改变json文件内容
    :param file_path: 文件地址
    :param kw: 关键字参数
    :return:
    """
    if len(kw) == 0:
        return
    try:
        with open(file_path, encoding='utf-8', mode='r+') as read_file:
            read_json = json.load(read_file)
        for key, value in kw.items():
            read_json[key] = value
        data = json.dumps(read_json, ensure_ascii=False, indent=4, sort_keys=True)
        with open(file_path, encoding='utf-8', mode='w') as write_file:
            write_file.write(data)
    except FileNotFoundError as e:
        raise FileNotFoundError("文件{}不存在".format(file_path))


def change_algorithm_json(file_path, **kw):
    """
    通过kw修改algorithm文件内容
    :param file_path: 文件地址
    :param kw:关键字参数
    :return:
    """
    require_weight = dict_to_str(kw['require_conclude'], kw['require_weight'])
    provide_weight = dict_to_str(kw['provide_conclude'], kw['provide_weight'])
    temp_dict = dict()
    temp_dict['{}_require_weight'.format(kw['algorithm_type'])] = require_weight
    temp_dict['{}_provide_weight'.format(kw['algorithm_type'])] = provide_weight
    change_json_file(file_path, **temp_dict)


def result_merge(require_ids, provide_ids, *results):
    """
    合并运算结果
    :param require_ids: 需求id
    :param provide_ids: 服务id
    :param results: 运算结果
    :return:
    """
    result_matrix = np.zeros((len(require_ids), len(provide_ids)))
    if 0 == len(require_ids) or 0 == len(provide_ids):
        return
    for require_index, require_id in enumerate(require_ids):
        for provide_index, provide_id in enumerate(provide_ids):
            result_matrix[require_index][provide_index] = min([result[require_index][provide_index] for result in results])

    print(result_matrix)


if __name__ == '__main__':
    # a_dict = {'provide_conclude': ['2', '4', '8', '9', '12', '16', '17', '18', '20', '25'],
    #           'score': 0.08683506435346335,
    #           'require_weight': ['3', '1', '2', '1', '3'], 'require_conclude': ['2', '4', '8', '11', '18'],
    #           'provide_weight': ['3', '3', '1', '1', '0', '0', '1', '5', '5', '4'], 'algorithm_type': 'lsi', 'used': 0}
    # print(type(a_dict))
    # change_algorithm_json('./config/algorithm.json', **a_dict)
    # print(dict_to_str(['1', '2', '3'], ['1', '2', '3']))
    # value = {'default': False}
    # change_json_file('./config/testdata.json', **value)
    # assert str_value_to_int_list('1,2,3,4') == [1, 2, 3, 4]
    # print(get_mssql_time(datetime.datetime.now()))
    print(str_list_to_dict("2-5,4-5,8-5,11-5,18-5".strip().split(',')))
