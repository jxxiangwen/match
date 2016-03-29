#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, json

module_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir, os.pardir, os.pardir))
sys.path.append(module_path)
for a_path in sys.path:
    if os.path.exists(os.path.join(a_path, 'cn', 'edu', 'shu', 'match')):
        os.chdir(os.path.join(a_path, 'cn', 'edu', 'shu', 'match'))
        break

__author__ = 'jxxia'


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


__author__ = 'jxxia'

if __name__ == '__main__':
    with open('./tt.properties', encoding='utf-8') as property_file:
        lines = property_file.readlines()  # 读取全部内容
        algorithm_dict = dict()
        print(len(algorithm_dict))
        remove_line = slice(0, -1)
        for line in lines:
            split_str = line.split('=')
            if len(split_str) == 1:
                pass
            else:
                split_str[1] = split_str[1][remove_line]
                if 'true' == split_str[1]:
                    algorithm_dict[split_str[0]] = True
                elif 'false' == split_str[1]:
                    algorithm_dict[split_str[0]] = False
                else:
                    algorithm_dict[split_str[0]] = float(split_str[1])
        if 0 < len(algorithm_dict):
            change_json_file('./config/algorithm.json', **algorithm_dict)
