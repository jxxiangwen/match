#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cn.edu.shu.match.match_algorithm import MatchAlgorithm
from cn.edu.shu.match.process.model_factory import ModelFactory
import numpy as np

__author__ = 'jxxia'
"""
lda匹配算法
"""


class LdaMatchAlgorithm(MatchAlgorithm):
    """
    通过lda主题模型计算匹配度
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
        self._require_model = ModelFactory().create_model('require', 'lda')  # 获取需求模型
        self._provide_model = ModelFactory().create_model('provide', 'lda')  # 获取服务模型
        self._require_model.set_text(train)
        self._provide_model.set_text(train)
        self._require_id = self._require_model.get_document_id()  # 获取需求号
        self._provide_id = self._provide_model.get_document_id()  # 获取服务号
        self._require_text = self._require_model.get_text()  # 获取需求文本
        self._provide_text = self._provide_model.get_text()  # 获取服务文本
        self._result_matrix = np.zeros((len(self._require_id), len(self._provide_id)))  # 初始化匹配结果矩阵

    def get_result(self, re_train=True, num_topics=5):
        """
        得到算法匹配结果
        :param re_train: 是否重新训练模型
        :param num_topics: 模型的主题数目
        :return: 返回匹配结果
        """
        self._provide_model.train('lda', 'provide', re_train, num_topics)
        return super().get_result(re_train, num_topics)

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


if __name__ == '__main__':
    match_algorithm = LdaMatchAlgorithm()
    print(match_algorithm.get_result())
