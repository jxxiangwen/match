#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import namedtuple
from cn.edu.shu.match.tool import get_mssql_time, change_algorithm_json
from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.build_mongodb import Mongo
from cn.edu.shu.match.genetic_algorithm import GeneticAlgorithm
import json, datetime

__author__ = 'jxxia'


class GetComment(object):
    """
    获取用户对匹配的评价，可返回评价较好的需求和服务权重
    """

    def __init__(self, algorithm_type='lsi'):
        """
        初始化对象
        :param algorithm_type: 算法类型
        :return:
        """
        self._algorithm_type = algorithm_type  # 算法类型
        self._genetic_algorithm = GeneticAlgorithm(self._algorithm_type)  # 遗传算法
        self._record = dict()  # 保存记录
        self._record_id = 0  # 记录保存到MongoDB的id号
        self._good_weight = list()  # 保存好的权重
        self._mssql = MsSql()  # 连接MSSql数据库
        self._record_collection = None  # 保存record集合名称
        self._weight_collection = None  # 保存weight集合名称
        self._mongo = Mongo()  # 连接MongoDB数据库
        self._match_structure = list()  # 匹配评分表结构
        self._match_good = 0  # 匹配评分大于多少才算好
        self._match_comment_number = 0  # 要搜集多少好的评分
        self._match_weight_number = 0  # 要搜集多少好的权重
        self._require_weight = str()  # 所用需求权重
        self._provide_weight = str()  # 所用服务权重
        self._start_time = 0  # 权重开始时间
        with open('./config/mongodb.json', encoding='utf-8') as mongodb_file:
            mongodb_json = json.load(mongodb_file)
            self._record_collection = mongodb_json['record']
            self._weight_collection = mongodb_json['weight']
            self._mongo.set_collection(self._weight_collection)
        with open('./config/match_comment.json', encoding='utf-8') as match_comment_file:
            match_comment_json = json.load(match_comment_file)
            self._match_good = match_comment_json['match_good']
            self._match_comment_number = match_comment_json['match_comment_number']
            self._match_weight_number = match_comment_json['match_weight_number']
            self._match_structure = match_comment_json['match_structure']

    def init_record(self):
        """
        初始化一个记录一次记录，包括开始时间，好的权重数目
        :return:
        """
        with open('./config/algorithm.json', encoding='utf-8') as algorithm_file:
            algorithm_json = json.load(algorithm_file)
            self._require_weight = algorithm_json['{}_{}_weight'.format(self._algorithm_type, 'require')]
            self._provide_weight = algorithm_json['{}_{}_weight'.format(self._algorithm_type, 'provide')]
        self._start_time = get_mssql_time(datetime.datetime.now())
        self._record['start_time'] = list()
        self._record['end_time'] = list()
        self._record['good_weight_number'] = 0
        self._record['good_require_weight'] = list()
        self._record['good_provide_weight'] = list()
        self._record_id = self._mongo.get_collection().save(self._record)
        self._record['_id'] = self._record_id

    def change_weight(self):
        """
        得到一个未被使用的优秀权重
        :return:
        """
        result = list(
            self._mongo.get_collection().find({'used': 0, "algorithm_type": self._algorithm_type}).sort('score').limit(
                1))[0]
        change_algorithm_json('./config/algorithm.json', **result)
        self._mongo.get_collection().update({'_id': result['_id']}, {'$set': {'used': 1}})

    def _get_score(self, start_time=None, end_time=get_mssql_time(datetime.datetime.now())):
        """
        得到评论结果
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return:
        """
        # 得到查询范围
        if isinstance(start_time, type(None)):
            start_time = self._start_time
        data = (self._algorithm_type, start_time, end_time)
        search_str = "select * from DocMatchInfoComment where match_id  in (select DocMatchInfor_ID from DocMatchInfor where Algorithm_Type like '%{}%') and create_time between '{}' and '{}'".format(
            *data)
        results = self._mssql.exec_search(search_str)
        if self._match_comment_number > len(results):
            # 评论次数不足
            return
        else:
            # 评论次数足够
            DocMatchInfoComment = namedtuple('DocMatchInfoComment', self._match_structure)  # 命名元组
            sum_value = 0
            for result in results:
                match = DocMatchInfoComment(*result)
                sum_value += result[match.score]
            # 获得平均得分
            average_score = sum_value / len(results)
            if average_score > self._match_good:
                # 保存优秀的需求和服务权重
                self._record['start_time'].push(self._start_time)
                self._record['end_time'].push(end_time)
                self._start_time = end_time
                self._record['good_require_weight'].push(self._require_weight)
                self._record['good_provide_weight'].push(self._provide_weight)
                if len(self._record['good_require_weight']) >= self._match_weight_number:
                    self._mongo.set_collection(self._record_collection)
                    self._mongo.get_collection().save(self._record)
                    self._mongo.set_collection(self._weight_collection)
                    # 权重收集足够，使用遗传算法跑出更好权重
                    self._genetic_algorithm.genetic_optimize(self._record['good_require_weight'],
                                                             self._record['good_provide_weight'])
                # 改变权重重新跑
                self.change_weight()

    def do_better(self):
        """
        产生更好的权重
        :return:
        """
        self._get_score()


if __name__ == '__main__':
    get_comment = GetComment()
    get_comment.init_record()
    get_comment.do_better()