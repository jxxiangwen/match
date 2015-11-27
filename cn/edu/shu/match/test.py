#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cn.edu.shu.match.process.model_factory import ModelFactory
from cn.edu.shu.match.process.require_model import RequireModel
from cn.edu.shu.match.process.provide_model import ProvideModel
import json

__author__ = 'jxxia'

# read_algorithm = open('./config/table.json', encoding='utf-8', mode='r')
# json_data = json.load(read_algorithm)  # 加载Json文件
# write_algorithm = open('./config/table.json', encoding='utf-8', mode='w')
# json_data["provide"] = "provide我的"
# json.dump(json_data, write_algorithm, ensure_ascii=False, indent=4, sort_keys=True)
#


with open('./config/algorithm.json', encoding='utf-8', mode='r+') as test_file:
    test_json = json.load(test_file)
    test_json['default'] = False
    data = json.dumps(test_json, ensure_ascii=False, indent=4,sort_keys=True)
    # print(data)

    with open('./config/algorithm.json', encoding='utf-8', mode='w') as write_file:
        write_file.write(data)


# with open('./config/genetic.json', encoding='utf-8') as genetic_file:
#     genetic_json = json.load(genetic_file)
#     with open('./config/algorithm.json', encoding='utf-8') as algorithm_file:
#         min = int(['min'])

# class Model(object):
#     """
#     匹配模型接口，定义模型需要实现的函数
#     """
#
#     def __init__(self):
#         self._index = "index"  # 保存训练
#         self._dictionary = None  # 保存训练词典
#         self._model = None  # 保存模型训练结果
#
#
# class AModel(Model):
#     def get_value(self):
#         print("self._index is {}".format(self._index))


# class Person:
#     def __init__(self):
#         self.name = 'zou'
#         self._age = 13
#         self.__place = 'shanghai'
#         print('__init')
#
#
# if __name__ == '__main__':
#     model = ModelFactory()
#     a = model.create_model('require')
#     print(type(a))
#     model = RequireModel()
#     # model.get_value()
#     person = Person()
#     print(person.name)
#     # print(person.__place)




# # match_algorithm = LsiMatchAlgorithm(True)
# # print(match_algorithm.get_result(True))  # 重新训练
# # print("损失函数值为:{}".format(match_algorithm.get_loss_func()))
# match_algorithm = LsiMatchAlgorithm(False)
# print(match_algorithm.get_result(True))  # 不重新训练
# print("损失函数值为:{}".format(match_algorithm.get_loss_func()))
# # match_algorithm = LdaMatchAlgorithm(True)
# # print(match_algorithm.get_result(True))  # 重新训练
# # print("损失函数值为:{}".format(match_algorithm.get_loss_func()))
# match_algorithm = LdaMatchAlgorithm(False)
# # print(match_algorithm.get_result(re_train=True, num_topics=5))  # 重新训练
# print(match_algorithm.get_result(True))  # 不重新训练
# print("损失函数值为:{}".format(match_algorithm.get_loss_func()))