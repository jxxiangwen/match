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


if __name__ == '__main__':
    assert str_value_to_int_list('1,2,3,4') == [1, 2, 3, 4]
