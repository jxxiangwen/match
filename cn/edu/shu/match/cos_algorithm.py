#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cn.edu.shu.match.match_algorithm import MatchAlgorithm

__author__ = 'jxxia'

"""
余弦相似度匹配算法
"""


class CosMatchAlgorithm(MatchAlgorithm):
    """
    通过余弦相似度计算匹配度
    """

    def __init__(self, train=True, read_file=True, match_need=dict()):
        """
        初始化函数
        :param train: 为True使用训练数据，否则使用测试数据
        :param read_file: 是否从文件中读取conclude和weight数据
        :param match_need: 如果read_file为False，此处必填
        :return: None
        """
        super().__init__(train, read_file, match_need)

    def get_result(self, re_train=True, num_topics=5):
        """
        得到算法匹配结果
        :param re_train: 是否重新训练模型
        :param num_topics: 模型的主题数目
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
