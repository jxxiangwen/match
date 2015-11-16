#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'jxxia'

"""
匹配算法接口类
"""


class MatchAlgorithm(object):
    """
    定义匹配算法通用接口
    """

    def __init__(self, train=True, read_file=True, match_need=dict()):
        """
        初始化函数
        :param train: 为True使用训练数据，否则使用测试数据
        :param read_file: 是否从配置文件中读取语料库
        :param match_need: 如果read_file为False，此处必填
        :return: None
        """
        self._read_file = read_file  # 是否从文件中读取conclude和weight数据
        self._match_need = match_need  # 如果read_file为False，此处必填
        self._train = train  # 为True使用训练数据，否则使用测试数据
        self._require_model = None  # 获取需求模型
        self._provide_model = None  # 获取服务模型
        self._require_id = list()  # 获取需求号
        self._provide_id = list()  # 获取服务号
        self._require_text = list()  # 获取需求文本
        self._provide_text = list()  # 获取服务文本
        self._result_matrix = None  # 初始化匹配结果矩阵

    def get_result(self, re_train=True, num_topics=5):
        """
        得到算法匹配结果
        :param re_train: 是否重新训练模型
        :param num_topics: 模型的主题数目
        :return: 返回匹配结果
        """
        for resource_id, resource_text in enumerate(self._require_text):
            (index, dictionary, model) = self._provide_model.get_model()
            # 词袋处理
            ml_bow = dictionary.doc2bow(resource_text)
            # 放入模型中，计算其他数据与其的相似度
            ml_model = model[ml_bow]  # ml_lsi 形式如 (topic_id, topic_value)
            sims = index[ml_model]  # sims 是最终结果了， index[xxx] 调用内置方法 __getitem__() 来计算ml_lsi

            # 排序，为输出方便
            sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])
            for destination_id, score in sort_sims:
                self._result_matrix[resource_id][destination_id] = score

        return self._result_matrix

    def get_require_id(self):
        """
        返回需求id
        :return: 需求id
        """
        return self._require_id

    def get_provide_id(self):
        """
        返回服务id
        :return: 服务id
        """
        return self._provide_id

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
