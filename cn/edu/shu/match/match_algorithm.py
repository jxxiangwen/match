#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.build_mongodb import Mongo
from time import strftime, localtime
import numpy as np
import json, sys, json

__author__ = 'jxxia'

"""
匹配算法接口类
"""

sql = MsSql()
match_table_name = None
require_id_name = None
provide_id_name = None
with open('./config/match_table.json', encoding='utf-8') as table_file:
    table_json = json.load(table_file)
    match_table_name = table_json['match']
    require_id_name = table_json['match_require_id']
    provide_id_name = table_json['match_provide_id']
    degree_name = table_json['match_degree']
    match_algorithm_type = table_json['match_algorithm_type']


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
        if isinstance(self._require_text, type(None)):
            return
        for resource_id, resource_text in enumerate(self._require_text):
            (index, dictionary, model) = self._provide_model.get_model()
            # 词袋处理
            ml_bow = dictionary.doc2bow(resource_text)
            # 放入模型中，计算其他数据与其的相似度
            ml_model = model[ml_bow]  # ml_lsi 形式如 (topic_id, topic_value)
            try:
                sims = index[ml_model]  # sims 是最终结果了， index[xxx] 调用内置方法 __getitem__() 来计算ml_lsi
                # 排序，为输出方便
                sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])
                for destination_id, score in sort_sims:
                    self._result_matrix[resource_id][destination_id] = score
            except IndexError as e:
                print("计算匹配度出错")
                return

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

    def get_loss_func(self):
        """
        得到损失函数值
        :return: 损失函数值
        """
        collection = None
        with open('./config/mongodb.json', encoding='utf-8') as mongodb_file:
            mongodb_json = json.load(mongodb_file)
            if 'train' == self._train:
                collection = mongodb_json['train']  # 训练配置文件集合名
            elif 'test' == self._train:
                collection = mongodb_json['test']  # 测试配置文件地址
            else:
                raise ValueError("非训练或测试没有损失函数")
        mongo = Mongo()
        mongo.set_collection(collection)
        match_degree = None
        try:
            match_degree = np.array(mongo.find()['match_degree'])  # 人工设置的匹配度
        except KeyError as e:
            print("集合{}文件中不存在{}字段".format(mongo.get_collection(), 'match_degree'))
            sys.exit()
        difference = self.get_result() - match_degree  # 匹配度差值矩阵
        score = 0.0
        score = np.sum(np.square(difference))  # 损失函数
        return score

    @staticmethod
    def degree_transform(degree):
        """
        将余弦相似度转化为匹配度
        :param degree: 余弦相似度
        :return:匹配度
        """
        with open('./config/degree.json', encoding='utf-8') as degree_file:
            degree_json = json.load(degree_file)
            return degree_json[str(int(abs(degree) * 100))]

    @staticmethod
    def save(require_id, provide_id, result, algorithm_type):
        """
        将匹配结果存入数据库
        :param require_id: 需求id
        :param provide_id: 服务id
        :param result: 要存入的结果
        :param algorithm_type: 算法类型
        :return: 是否成功存入数据库
        """
        search_str = "select * from {} WHERE {}={} AND {}={}".format(match_table_name, require_id_name, require_id,
                                                                     provide_id_name, provide_id)
        results = sql.exec_search(search_str)
        if 0 == len(results):
            print("INSERT INTO %s VALUES ('%s', '%s', '%s', '0', '%s', '0', '0',%s)" % (
                match_table_name, require_id, provide_id, MatchAlgorithm.degree_transform(result),
                strftime('%Y-%m-%d %H:%M:%S', localtime()), algorithm_type))
            # 保存记录UPDATE Person SET FirstName = 'Fred' WHERE LastName = 'Wilson'
            sql.exec_non_search("INSERT INTO %s VALUES ('%s', '%s', '%s', '0', '%s', '0', '0','%s')" % (
                match_table_name, require_id, provide_id, MatchAlgorithm.degree_transform(result),
                strftime('%Y-%m-%d %H:%M:%S', localtime()), algorithm_type))
        else:
            print("UPDATE %s SET %s = %s,%s = '%s' WHERE %s = %d AND %s = %d" % (
                match_table_name, degree_name, MatchAlgorithm.degree_transform(result), match_algorithm_type,
                algorithm_type, require_id_name, require_id, provide_id_name, provide_id))
            # 更新记录
            sql.exec_non_search("UPDATE %s SET %s = %s,%s = '%s' WHERE %s = %d AND %s = %d" % (
                match_table_name, degree_name, MatchAlgorithm.degree_transform(result), match_algorithm_type,
                algorithm_type, require_id_name, require_id, provide_id_name, provide_id))

    @staticmethod
    def save_to_database(require_ids, provide_ids, algorithm_type, min_threshold, *results):
        """
        将匹配结果存入数据库
        :param require_ids: 需求id
        :param provide_ids: 服务id
        :param algorithm_type: 算法类型
        :param min_threshold: 阈值
        :param results: 要存入的结果矩阵
        :return: 是否成功存入数据库
        """
        if 0 == len(require_ids) or 0 == len(provide_ids):
            return
        for require_index, require_id in enumerate(require_ids):
            for provide_index, provide_id in enumerate(provide_ids):
                similarity = min([result[require_index][provide_index] for result in results])
                # 大于阈值存入数据库
                if similarity > min_threshold:
                    MatchAlgorithm.save(require_id, provide_id, similarity, algorithm_type)

    def compute_match_result(self, first_doc, second_doc):
        """
        计算传入数据的算法匹配结果
        :param first_doc:
        :param second_doc:
        :return: 返回匹配结果
        """
        pass


if __name__ == '__main__':
    MatchAlgorithm.save(6, 5, 0.98, 'lsi')
