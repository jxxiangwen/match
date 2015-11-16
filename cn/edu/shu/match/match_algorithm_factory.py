#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cn.edu.shu.match.lsi_algorithm import LsiMatchAlgorithm
from cn.edu.shu.match.lda_algorithm import LdaMatchAlgorithm
from cn.edu.shu.match.cos_algorithm import CosMatchAlgorithm

__author__ = 'jxxia'
"""
匹配算法工厂类
"""


class MatchAlgorithmFactory(object):
    """
    创建匹配算法对象
    """

    def __init__(self):
        """
        初始化类包含的算法类型
        :return:
        """
        self.algorithm = dict()
        self.algorithm_type = ['lsi', 'lda', 'cos']

    def create_match_algorithm(self, algorithm_name, train=True, read_file=True, match_need=dict()):
        """
        通过algorithm_name创建匹配算法对象
        :param algorithm_name: 需要创建的算法对象类型
        :param train: 为True使用训练数据，否则使用测试数据
        :param read_file: 是否从文件中读取conclude和weight数据
        :param match_need: 如果read_file为False，此处必填
        :return: 创建的算法对象，如果不存在则抛出TypeError异常
        """
        self.algorithm['lsi'] = LsiMatchAlgorithm(train, read_file, match_need)
        self.algorithm['lda'] = LdaMatchAlgorithm(train, read_file, match_need)
        self.algorithm['cos'] = CosMatchAlgorithm(train, read_file, match_need)
        if algorithm_name in self.algorithm_type:
            return self.algorithm[algorithm_name]
        raise TypeError("不存在{}算法".format(algorithm_name))
