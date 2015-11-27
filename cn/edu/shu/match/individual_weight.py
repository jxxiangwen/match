#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.build_mongodb import Mongo
import json

__author__ = 'jxxia'


class IndividualWeight(object):
    """
    产生用户个性化权重
    """

    def __init__(self):
        self._sql = MsSql()  # 连接MSsql数据库
        self._mongo = Mongo()  # 连接MongoDB数据库
        self._lsi_weight = None  # 保存lsi算法最佳权重
        self._lda_weight = None  # 保存lda算法最佳权重
        self._lsi_require_conclude = None  # lsi算法需求包含索引号
        self._lsi_provide_conclude = None  # lsi算法服务包含索引号
        self._lda_require_conclude = None  # lda算法需求包含索引号
        self._lda_provide_conclude = None  # lda算法服务包含索引号
        self._lsi_require_weight = None  # lsi算法需求索引号相应权重
        self._lsi_provide_weight = None  # lsi算法服务索引号相应权重
        self._lda_require_weight = None  # lda算法需求索引号相应权重
        self._lda_provide_weight = None  # lda算法服务索引号相应权重
        self._user_info = None
        # 读取数据库中表名
        with open('./config/table.json', encoding='utf-8') as table_file:
            table_json = json.load(table_file)
            # 读取算法配置
            self._user_info = self._sql.exec_search("select * from %s" % table_json['user'])
        # 读取MongoDB中表名
        with open('./config/mongodb.json', encoding='utf-8') as mongodb_file:
            mongodb_json = json.load(mongodb_file)
            self._mongo.set_collection(mongodb_json['weight'])
            self._lsi_weight = list(self._mongo.get_collection().find({'algorithm_type': 'lsi'}).sort('score').limit(1))[0]
            self._lda_weight = list(self._mongo.get_collection().find({'algorithm_type': 'lda'}).sort('score').limit(1))[0]
        with open('./config/algorithm.json', encoding='utf-8') as algorithm_file:
            algorithm_json = json.load(algorithm_file)
            self._lsi_require_conclude = algorithm_json['lsi_require_conclude']  # lsi算法需求包含索引号
            self._lsi_provide_conclude = algorithm_json['lsi_provide_conclude']  # lsi算法服务包含索引号
            self._lda_require_conclude = algorithm_json['lda_require_conclude']  # lda算法需求包含索引号
            self._lda_provide_conclude = algorithm_json['lda_provide_conclude']  # lda算法服务包含索引号
        self._lsi_require_weight = self.__weight_tool(self._lsi_require_conclude,
                                                      self._lsi_weight['require_weight'])  # lsi算法需求索引号相应权重
        self._lsi_provide_weight = self.__weight_tool(self._lsi_provide_conclude,
                                                      self._lsi_weight['provide_weight'])  # lsi算法服务索引号相应权重
        self._lda_require_weight = self.__weight_tool(self._lda_require_conclude,
                                                      self._lda_weight['require_weight'])  # lda算法需求索引号相应权重
        self._lda_provide_weight = self.__weight_tool(self._lda_provide_conclude,
                                                      self._lda_weight['provide_weight'])  # lda算法服务索引号相应权重

    def __weight_tool(self, conclude_list, weight_list):
        """
        将conclude和weight两个list转化为如"2-5,4-5,8-5,11-5,18-5"字符串
        :param conclude_list: 索引列表
        :param weight_list: 权重列表
        :return:
        """
        string = ''
        for index, weiight in zip(conclude_list, weight_list):
            string += str(index) + '-' + str(weiight) + ','
        return string[:-1]

    def save_individual(self):
        """
        保存个性化权重到MongoDB
        :return:
        """
        with open('./config/mongodb.json', encoding='utf-8') as mongodb_file:
            mongodb_json = json.load(mongodb_file)
            self._mongo.set_collection(mongodb_json['individual'])
        if len(self._user_info) == 0:
            return
        for user in self._user_info:
            with open('./config/algorithm.json', encoding='utf-8') as algorithm_file:
                algorithm_json = json.load(algorithm_file)
                id = self._mongo.get_collection().save(algorithm_json)
                weight_data = list(self._mongo.get_collection().find({'_id': id}))[0]
                weight_data['user_id'] = user[0]
                weight_data['lsi_require_weight'] = self._lsi_require_weight
                weight_data['lsi_provide_weight'] = self._lsi_provide_weight
                weight_data['lda_require_weight'] = self._lda_require_weight
                weight_data['lda_provide_weight'] = self._lda_provide_weight
                self._mongo.get_collection().save(weight_data)
                print(id)
                print(list(self._mongo.get_collection().find({'_id': id})))


if __name__ == '__main__':
    individual = IndividualWeight()
    individual.save_individual()
