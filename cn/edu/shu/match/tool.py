#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
