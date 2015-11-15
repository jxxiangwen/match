#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import reduce
from cn.edu.shu.match.lsi import get_result_from_lsi
from cn.edu.shu.match.lda import get_result_from_lda
from cn.edu.shu.match.lsi_algorithm import LsiMatchAlgorithm
from cn.edu.shu.match.lda_algorithm import LdaMatchAlgorithm
from cn.edu.shu.match.cosine import *
from cn.edu.shu.match.build_json import BuildJson
from cn.edu.shu.match.tool import str_value_to_int_list
import random, time
import json
import logging
from time import strftime, localtime

__author__ = 'jxxia'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('log/GeneticalAgorithm_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='a')

# 全局变量，存储需求和服务编号顺序
require_id = []
provide_id = []


class GeneticAlgorithm:
    """
    遗传算法
    """

    def cost(self, require_conclude, require_weight, provide_conclude, provide_weight, algorithm_type='lsi'):
        """
        遗传算法成本计算函数
        :param require_conclude:需求匹配所包含索引
        :param require_weight:需求权重
        :param provide_conclude:服务匹配所包含索引
        :param provide_weight:服务权重
        :param algorithm_type:算法类型
        :return:所需成本
        """
        match_file = dict()
        match_file['require_conclude'] = require_conclude
        match_file['require_weight'] = list(map(lambda x: str(x), require_weight))
        match_file['provide_conclude'] = provide_conclude
        match_file['provide_weight'] = list(map(lambda x: str(x), provide_weight))
        print(match_file)
        match_algorithm = None
        if "lsi" == algorithm_type:
            match_algorithm = LsiMatchAlgorithm()
            # result = match_algorithm.get_result(re_train=True, num_topics=5)  # 重新训练
            result = match_algorithm.get_result(False)  # 不重新训练
        elif "lda" == algorithm_type:
            match_algorithm = LdaMatchAlgorithm()
            # result = match_algorithm.get_result(re_train=True, num_topics=5)  # 重新训练
            result = match_algorithm.get_result(False)  # 不重新训练
        elif "cos" == algorithm_type:
            pass
        elif "all" == algorithm_type:
            pass
        else:
            raise ValueError
        # rusult 形式为len(require_id) * len(provide_id)的矩阵
        result_require_id = match_algorithm.get_require_id()
        result_provide_id = match_algorithm.get_provide_id()
        with open('./config/match.json', encoding='utf-8') as match_file:
            match_json = json.load(match_file)
            result_real_require_id = match_json['require_id']  # 用来训练的需求id
            result_real_provide_id = match_json['provide_id']  # 用来训练的服务id
            # 转化为int型list
            result_real_require_id == str_value_to_int_list(result_real_require_id)
            result_real_provide_id == str_value_to_int_list(result_real_provide_id)
            for train_require_id in result_real_require_id:
                if result_require_id.count(train_require_id) == 0:
                    raise IndexError("数据库中不存在id为{}的需求文档".format(train_require_id))
            for train_provide_id in result_real_provide_id:
                if result_provide_id.count(train_provide_id) == 0:
                    raise IndexError("数据库中不存在id为{}的服务文档".format(train_provide_id))
        match_degree = result[2]  # 存储匹配结果
        src = result[3]
        score = 0.0
        with open('./config/match.json', encoding='utf-8') as match_file:
            match_json = json.load(match_file)
            if 'require' == src:
                raise AttributeError('src为require暂时还未开始')
            elif 'provide' == src:
                for src_id in result_provide_id:
                    match_real_degree = match_json['match_degree_' + str(src_id)].strip().split(',')  # 获取配置表中真实匹配状况
                    match_result = match_degree[src_id - 1]  # 获取某一文档匹配结果
                    for index, virtual_degree in match_result:
                        score += (virtual_degree - float(match_real_degree[index])) ** 2  # 将真实结果和算法所求结果差值的平方作文损失函数
                print("score: %s" % score)
            else:
                raise ValueError
        return score

    def genetic_optimize(self, algorithm_type='lsi'):
        """
        遗传算法
        :param algorithm_type:算法类型
        :return:需求权重和服务权重
        """

        # 变异操作
        def mutate(weight_vector):
            print("变异前数据：%s" % weight_vector)
            i = random.randint(0, len(weight_vector) - 1)
            if random.random() < 0.5 and weight_vector[i] > min:
                print("变异返回：%s" % (weight_vector[0:i] + [weight_vector[i] - step] + weight_vector[i + 1:]))
                return weight_vector[0:i] + [weight_vector[i] - step] + weight_vector[i + 1:]
            elif weight_vector[i] < max_value:
                print("变异返回：%s" % (weight_vector[0:i] + [weight_vector[i] + step] + weight_vector[i + 1:]))
                return weight_vector[0:i] + [weight_vector[i] + step] + weight_vector[i + 1:]
            else:
                print("没有变异")
                return weight_vector

        # 交叉操作
        def crossover(a_cross1, a_cross2):
            print("交叉前数据：%s 和 %s" % (a_cross1, a_cross2))
            i = random.randint(1, len(a_cross1) - 2)
            print("交叉返回：%s" % (a_cross1[0:i] + a_cross2[i:]))
            return a_cross1[0:i] + a_cross2[i:]

        with open('./config/genetic.json', encoding='utf-8') as genetic_file:
            genetic_json = json.load(genetic_file)
            with open('./config/algorithm.json', encoding='utf-8') as algorithm_file:
                min_value = int(genetic_json['min_value'])
                max_value = int(genetic_json['max_value'])
                pop_size = int(genetic_json['pop_size'])
                step = int(genetic_json['step'])
                mutate_prob = float(genetic_json['mutate_prob'])
                elite = float(genetic_json['elite'])
                max_iter = int(genetic_json['max_iter'])
                algorithm_json = json.load(algorithm_file)
                require_conclude = algorithm_json[algorithm_type + '_require_conclude'].strip().split(',')
                # require_weight = algorithm_json[algorithm_type + '_require_weight'].strip().split(',')
                provide_conclude = algorithm_json[algorithm_type + '_provide_conclude'].strip().split(',')
                # provide_weight = algorithm_json[algorithm_type + '_provide_weight'].strip().split(',')

                # 构造初始总群
                require_weight_pop = []
                provide_weight_pop = []
                for i in range(pop_size):
                    require_weight = [random.randint(min_value, max_value) for i in range(len(require_conclude))]
                    require_weight_pop.append(require_weight)
                    provide_weight = [random.randint(min_value, max_value) for i in range(len(provide_conclude))]
                    provide_weight_pop.append(provide_weight)

                print("require_weight_pop :{}".format(require_weight_pop))
                print("provide_weight_pop :{}".format(provide_weight_pop))
            # 每一代中有多少胜出者
            top_elite = int(elite * pop_size)
            with open('./result/score.txt', encoding='utf-8', mode='a+') as score_file:
                score_file.write('\n')
                score_file.write(str(0.320819880065) + ',')

                # 主循环
                for i in range(max_iter):
                    print("开始循环")
                    print("第 %i 代需求数据：%s" % (i, require_weight_pop))
                    print("第 %i 代服务数据：%s" % (i, provide_weight_pop))
                    start = time.clock()  # 开始时间
                    scores = [(self.cost(require_conclude, require_weight, provide_conclude, provide_weight,
                                         algorithm_type), require_weight, provide_weight)
                              for require_weight in require_weight_pop
                              for provide_weight in provide_weight_pop]
                    scores.sort()
                    print("scores:%s" % scores)
                    score_file.writelines(str(scores[0][0]) + ',')
                    require_weight_ranked = [require_weight for (score, require_weight, provide_weight) in scores]
                    provide_weight_ranked = [provide_weight for (score, require_weight, provide_weight) in scores]
                    # 打印当前最优值
                    print("第 %d 代损失函数为%s" % (i, scores))
                    print("需求权重为%s" % (
                        list(map(lambda key, value: str(key) + '-' + str(value), require_conclude, scores[0][1]))))
                    print("服务权重为%s" % (
                        list(map(lambda key, value: str(key) + '-' + str(value), provide_conclude, scores[0][2]))))
                    end = time.clock()
                    print("第 %d 代需要: %f 秒" % (i, end - start))
                    score_file.flush()
                    # 从纯粹的胜出者开始
                    print("需求权重排序去重前数据：%s" % require_weight_ranked)
                    print("服务权重排序去重前数据：%s" % provide_weight_ranked)
                    move_repeat = lambda x, y: x if y in x else x + [y]  # 去除列表重复，防止权重
                    require_weight_ranked = reduce(move_repeat, [[], ] + require_weight_ranked)
                    provide_weight_ranked = reduce(move_repeat, [[], ] + provide_weight_ranked)
                    print("需求权重排序数据：%s" % require_weight_ranked)
                    print("服务权重排序数据：%s" % provide_weight_ranked)
                    require_weight_pop = require_weight_ranked[0:top_elite]
                    provide_weight_pop = provide_weight_ranked[0:top_elite]
                    # 添加变异和配对后的胜出者
                    while len(require_weight_pop) < pop_size:
                        print("需求开始变异和交叉")
                        if random.random() < mutate_prob:
                            # 变异
                            index = random.randint(0, len(require_weight_ranked) - 1)
                            require_weight_pop.append(mutate(require_weight_ranked[index]))
                        else:
                            # 交叉
                            c1 = random.randint(0, len(require_weight_ranked) - 1)
                            c2 = random.randint(0, len(require_weight_ranked) - 1)
                            require_weight_pop.append(crossover(require_weight_ranked[c1], require_weight_ranked[c2]))
                    while len(provide_weight_pop) < pop_size:
                        print("服务开始变异和交叉")
                        if random.random() < mutate_prob:
                            # 变异
                            index = random.randint(0, len(provide_weight_ranked) - 1)
                            provide_weight_pop.append(mutate(provide_weight_ranked[index]))
                        else:
                            # 交叉
                            cross1 = random.randint(0, len(provide_weight_ranked) - 1)
                            cross2 = random.randint(0, len(provide_weight_ranked) - 1)
                            provide_weight_pop.append(
                                crossover(provide_weight_ranked[cross1], provide_weight_ranked[cross2]))

                return tuple((scores[0][1], scores[0][2]))

    def show_data(self, line):
        """
        显示匹配度数据
        :param line: 行数
        :return:
        """
        with open('./result/score.txt', encoding='utf-8') as score_file:
            if line <= 0:
                return
            for i in range(line):
                result = score_file.readline().strip().split(',')
            import matplotlib.pyplot as plt
            import pylab as pl
            import numpy as np
            # degrees: 匹配度
            # labels: 代数
            generations = []
            degrees = []

            result = result[:-1]
            for index, degree in enumerate(result):
                generations.append(index)
                degrees.append(float(degree.strip()))

            pl.plot(generations, degrees)  # use pylab to plot x and y
            pl.show()  # show the plot on the screen


if __name__ == '__main__':
    ga = GeneticAlgorithm()
    # print(ga.cost([2,4,8,11,18],[5,5,5,5,5],[2,4,8,9,12,16,17,18,20,25],[5,5,5,5,5,5,5,5,5,5]))
    ga.genetic_optimize()
    # ga.show_data(4)
    # ga.show_data(3)
