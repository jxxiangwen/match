#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import reduce
from cn.edu.shu.match.match_algorithm_factory import MatchAlgorithmFactory
from cn.edu.shu.match.build_mongodb import Mongo
from time import strftime, localtime
import numpy as np
import random, time, json, sys, logging

__author__ = 'jxxia'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('log/genetic_algorithm_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='a')


class GeneticAlgorithm:
    """
    遗传算法
    """

    def __init__(self, algorithm_type='lsi', train='train'):
        """
        初始化函数
        :param algorithm_type: 算法类型
        :param train: 为'train'使用训练数据，为'test'使用测试数据,'all'使用所有数据
        :return: None
        """
        self._algorithm_type = algorithm_type  # 匹配算法类型
        self.re_train = True  # 重新训练还是直接读取训练结果
        self._train = train  # 为True使用训练数据，否则使用测试数据
        self._mongo = Mongo()  # 连接MongoDB数据库
        self._match_algorithm = None  # 算法类型
        self._weight_min = 0  # 训练数据最终得分小于weight_min时保存到MongoDB的weight集合中
        with open('./config/mongodb.json', encoding='utf-8') as mongodb_file:
            mongodb_json = json.load(mongodb_file)
            if 'train' == self._train:
                self._mongo.set_collection(mongodb_json['train'])  # 训练配置文件集合名
            elif 'test' == self._train:
                self._mongo.set_collection(mongodb_json['test'])  # 测试配置文件地址
            else:
                raise ValueError("遗传算法train必须为'train'或'test'，不能是{}".format(self._train))
            self._weight_min = mongodb_json['{}_weight_min'.format(self._algorithm_type)]
        self._match_degree = None  # 算法计算的匹配度
        try:
            self._match_real_degree = np.array(self._mongo.find()['match_degree'])  # 人工设置的匹配度
            self._result_require_id = self._mongo.find()['require_id']
            self._result_provide_id = self._mongo.find()['provide_id']
        except KeyError as e:
            print("集合{}文件中不存在{}字段".format(self._mongo.get_collection(), 'require_id or provide_id or match_degree'))
            sys.exit()
        self._weight = dict()  # 保存训练的权重数据，用来保存到MongDB
        self._weight['algorithm_type'] = self._algorithm_type

    def cost(self, require_conclude, require_weight, provide_conclude, provide_weight, algorithm_type='lsi',
             re_train=True, num_topics=5):
        """
        遗传算法成本计算函数
        :param require_conclude:需求匹配所包含索引
        :param require_weight:需求权重
        :param provide_conclude:服务匹配所包含索引
        :param provide_weight:服务权重
        :param algorithm_type:算法类型
        :param re_train:是否重新训练
        :param num_topics:主题数
        :return:所需成本
        """
        self._weight['require_conclude'] = require_conclude
        self._weight['require_weight'] = list(map(lambda x: str(x), require_weight))
        self._weight['provide_conclude'] = provide_conclude
        self._weight['provide_weight'] = list(map(lambda x: str(x), provide_weight))
        print('self._weight:{}'.format(self._weight))
        self._match_algorithm = MatchAlgorithmFactory().create_match_algorithm(self._algorithm_type, self._train,
                                                                               read_file=False,
                                                                               match_need=self._weight)  # 算法类型
        if self.re_train:
            self._match_degree = self._match_algorithm.get_result(re_train, num_topics)  # 重新训练
            while isinstance(self._match_degree, type(None)):
                # 防止lda超出索引错误
                self._match_degree = self._match_algorithm.get_result(re_train, num_topics)  # 重新训练
            assert self._result_require_id == self._match_algorithm.get_require_id()
            assert self._result_provide_id == self._match_algorithm.get_provide_id()
            self.re_train = False
        else:
            self._match_degree = self._match_algorithm.get_result(False)  # 不重新训练
            while isinstance(self._match_degree, type(None)):
                # 防止lda超出索引错误
                self._match_degree = self._match_algorithm.get_result(False)  # 不重新训练

        # rusult 形式为len(require_id) * len(provide_id)的矩阵
        difference = self._match_real_degree - self._match_degree
        score = 0.0
        score = np.sum(np.square(difference))
        self._weight['score'] = score
        self._weight['used'] = 0
        if score < self._weight_min:
            print("准备保存得分")
            self.insert(self._weight.copy())
        return score

    def insert(self, data):
        """
        保存效果好的权重数据
        :param data: 要保存的数据
        :return:
        """
        with open('./config/mongodb.json', encoding='utf-8') as mongodb_file:
            mongodb_json = json.load(mongodb_file)
            self._mongo.set_collection(mongodb_json['weight'])  # 保存权重的集合名
            result = self._mongo.get_collection().find(
                {'require_weight': data['require_weight'], 'provide_weight': data['provide_weight']})
            if 0 == result.count():
                print("数据已保存")
                self._mongo.insert(data)
            else:
                print("数据已存在")
            if self._train:
                self._mongo.set_collection(mongodb_json['train'])  # 训练配置文件集合名
            else:
                self._mongo.set_collection(mongodb_json['test'])  # 测试配置文件地址

    def genetic_optimize(self, good_require_weight_pop=[], good_provide_weight_pop=[], re_train=True, num_topics=5):
        """
        遗传算法
        :param good_require_weight_pop:用户满意的需求权重
        :param good_provide_weight_pop:用户满意的服务权重
        :param re_train:是否重新训练
        :param num_topics:主题数
        :return:需求权重和服务权重
        """

        # 变异操作
        def mutate(weight_vector):
            print("变异前数据：%s" % weight_vector)
            i = random.randint(0, len(weight_vector) - 1)
            if random.random() < 0.5 and weight_vector[i] > min_value:
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
                require_conclude = algorithm_json[self._algorithm_type + '_require_conclude'].strip().split(',')
                # require_weight = algorithm_json[self._algorithm_type + '_require_weight'].strip().split(',')
                provide_conclude = algorithm_json[self._algorithm_type + '_provide_conclude'].strip().split(',')
                # provide_weight = algorithm_json[self._algorithm_type + '_provide_weight'].strip().split(',')

                # 构造初始总群
                require_weight_pop = []
                provide_weight_pop = []
                if 0 != len(good_require_weight_pop) and 0 != len(good_require_weight_pop):
                    require_weight_pop = good_require_weight_pop
                    provide_weight_pop = good_provide_weight_pop
                else:
                    for i in range(pop_size):
                        require_weight = [random.randint(min_value, max_value) for i in range(len(require_conclude))]
                        require_weight_pop.append(require_weight)
                        provide_weight = [random.randint(min_value, max_value) for i in range(len(provide_conclude))]
                        provide_weight_pop.append(provide_weight)

                print("require_weight_pop :{}".format(require_weight_pop))
                print("provide_weight_pop :{}".format(provide_weight_pop))
            # 每一代中有多少胜出者
            top_elite = int(elite * pop_size)
            with open('./result/{}_score.txt'.format(self._algorithm_type), encoding='utf-8', mode='a+') as score_file:
                score_file.write('\n')
                score_file.write(str(0.320819880065) + ',')

                # 主循环
                for i in range(max_iter):
                    print("开始循环")
                    print("第 %i 代需求数据：%s" % (i, require_weight_pop))
                    print("第 %i 代服务数据：%s" % (i, provide_weight_pop))
                    start = time.clock()  # 开始时间
                    scores = [(self.cost(require_conclude, require_weight, provide_conclude, provide_weight,
                                         self._algorithm_type, re_train, num_topics), require_weight, provide_weight)
                              for require_weight in require_weight_pop
                              for provide_weight in provide_weight_pop]
                    scores.sort()
                    print("scores:%s" % scores)
                    score_file.writelines(str(scores[0][0]) + ',')
                    require_weight_ranked = [require_weight for (score, require_weight, provide_weight) in scores]
                    provide_weight_ranked = [provide_weight for (score, require_weight, provide_weight) in scores]
                    # 打印当前最优值
                    print("第 %d 代最小损失函数为%s" % (i, scores[0][0]))
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
                    print("剩下的优秀需求种群：{}".format(require_weight_pop))
                    print("剩下的优秀服务种群：{}".format(provide_weight_pop))
                    # 添加变异和配对后的胜出者
                    while len(require_weight_pop) < pop_size:
                        print("需求开始变异和交叉")
                        if random.random() < mutate_prob:
                            # 变异
                            index = random.randint(0, len(require_weight_pop) - 1)
                            require_weight_pop.append(mutate(require_weight_pop[index]))
                        else:
                            # 交叉
                            cross1 = random.randint(0, len(require_weight_pop) - 1)
                            cross2 = random.randint(0, len(require_weight_pop) - 1)
                            require_weight_pop.append(crossover(require_weight_pop[cross1], require_weight_pop[cross2]))
                    while len(provide_weight_pop) < pop_size:
                        print("服务开始变异和交叉")
                        if random.random() < mutate_prob:
                            # 变异
                            index = random.randint(0, len(provide_weight_pop) - 1)
                            provide_weight_pop.append(mutate(provide_weight_pop[index]))
                        else:
                            # 交叉
                            cross1 = random.randint(0, len(provide_weight_pop) - 1)
                            cross2 = random.randint(0, len(provide_weight_pop) - 1)
                            provide_weight_pop.append(crossover(provide_weight_pop[cross1], provide_weight_pop[cross2]))

                return tuple((scores[0][1], scores[0][2]))

    def show_plot_data(self, line):
        """
        显示匹配度数据
        :param line: 行数
        :return:
        """
        with open('./result/{}_score.txt'.format(self._algorithm_type), encoding='utf-8') as score_file:
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

    def show_bar_data(self):
        """
        显示匹配度数据
        :return:
        """
        with open('./result/show.txt', encoding='utf-8') as score_file:
            title = score_file.readline().strip().split()
            data = score_file.readline().strip().split()
            data = [float(value) for value in data]
            import matplotlib.pyplot as plt
            import numpy as np
            print(title)
            print(data)
            width = 0.4
            ind = np.linspace(0.5, 10.5, 4)
            # make a square figure
            fig = plt.figure(1)
            ax = fig.add_subplot(111)
            # Bar Plot
            ax.bar(ind - width / 2, data, width, color='coral')
            # Set the ticks on x-axis
            ax.set_xticks(ind)
            ax.set_xticklabels(title)
            # labels
            ax.set_xlabel('Title')
            ax.set_ylabel('Loss function value')
            plt.show()  # show the plot on the screen


if __name__ == '__main__':
    ga = GeneticAlgorithm()
    # ga.show_bar_data()
    ga.genetic_optimize()
    # ga = GeneticAlgorithm('lda')
    # ga.genetic_optimize()
    # print(ga.cost([2,4,8,11,18],[5,5,5,5,5],[2,4,8,9,12,16,17,18,20,25],[5,5,5,5,5,5,5,5,5,5]))
    # ga.show_plot_data(4)
    # ga.show_plot_data(3)
