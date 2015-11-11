#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from match_algorithm import MatchAlgorithm

__author__ = 'jxxia'

"""
余弦相似度匹配算法
"""


class CosMatchAlgorithm(MatchAlgorithm):
    """
    通过余弦相似度计算匹配度
    """

    def get_result(self):
        """
        得到算法匹配结果
        :return: 返回匹配结果
        """
        pass

    def save_to_database(self, a_result):
        """
        是否将匹配结果存入数据库
        :param a_result: 要存入的结果
        :return: 是否成功存入数据库
        """
        pass

    def compute_match_result(self, first_doc, second_doc):
        """
        计算传入数据的算法匹配结果
        :param first_doc:
        :param second_doc:
        :return: 返回匹配结果
        """
        pass
