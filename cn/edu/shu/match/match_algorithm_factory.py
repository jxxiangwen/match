#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from plsa_algorithm import PlsaMatchAlgorithm
from lda_algorithm import LdaMatchAlgorithm
from cos_algorithm import CosMatchAlgorithm

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
        self.algorithm_type = ['plsa', 'lda', 'cos']

    def create_match_algorithm(self, algorithm_name):
        """
        通过algorithm_name创建匹配算法对象
        :param algorithm_name: 需要创建的算法对象类型
        :return: 创建的算法对象，如果不存在则抛出TypeError异常
        """
        self.algorithm['plsa'] = PlsaMatchAlgorithm()
        self.algorithm['lda'] = LdaMatchAlgorithm()
        self.algorithm['cos'] = CosMatchAlgorithm()
        if algorithm_name in self.algorithm_type:
            return self.algorithm[algorithm_name]
        raise TypeError("不存在{}算法".format(algorithm_name))
