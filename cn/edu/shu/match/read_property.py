#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cn.edu.shu.match.tool import change_json_file

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
