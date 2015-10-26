#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'jxxia'

import json
import logging
from time import strftime, localtime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('log/build_json_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='a')


class BuildJson:
    """
    生成config文件夹下的json配置文件
    """

    def build_algorithm(self, require_conclude, require_weight, provide_conclude, provide_weight, algorithm_type,
                        path='./config/algorithm.json', individual=False):
        """
        生成算法配置文件
        :param require_conclude: 匹配所需需求索引
        :param require_weight: 匹配所需需求索引权重
        :param provide_conclude: 匹配所需服务索引
        :param provide_weight: 匹配所需服务索引权重
        :param algorithm_type: 所用算法类型
        :param path: 配置文件地址
        :param individual: 是否每个人使用一个配置文件
        :return:
        """
        read_algorithm = open('./config/algorithm.json', encoding='utf-8', mode='r')
        json_data = json.load(read_algorithm)  # 加载Json文件
        write_algorithm = open('./config/algorithm.json', encoding='utf-8', mode='w')
        json_data[algorithm_type+'_require_conclude'] = require_conclude
        json_data[algorithm_type+'_require_weight'] = require_weight
        json_data[algorithm_type+'_provide_conclude'] = provide_conclude
        json_data[algorithm_type+'_provide_weight'] = provide_weight
        json.dump(json_data, write_algorithm, ensure_ascii=False, indent=4, sort_keys=True)

    def build_degree(self, path='./config/degree.json'):
        """
        生成匹配度配置文件
        :param path: 配置文件地址
        :return:
        """
        None

    def build_match(self, path='./config/match.json'):
        """
        生成匹配度映射配置文件
        :param path: 配置文件地址
        :return:
        """
        None
