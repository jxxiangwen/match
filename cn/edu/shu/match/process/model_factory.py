#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cn.edu.shu.match.process.require_model import RequireModel
from cn.edu.shu.match.process.provide_model import ProvideModel

__author__ = 'jxxia'

"""
匹配模型工厂类
"""


class ModelFactory(object):
    """
    创建匹配算法对象
    """

    def __init__(self):
        """
        初始化类包含的算法类型
        :return:
        """
        self._model = dict()
        self._model_type = ['require', 'provide']

    def create_model(self, model_name, algorithm_type):
        """
        通过algorithm_name创建匹配算法对象
        :param model_name: 需要创建的模型类型
        :param algorithm_type: 需要创建的算法类型
        :return: 创建的算法对象，如果不存在则抛出TypeError异常
        """
        self._model['require'] = RequireModel(algorithm_type)
        self._model['provide'] = ProvideModel(algorithm_type)
        if model_name in self._model_type:
            return self._model[model_name]
        raise TypeError("不存在{}模型".format(model_name))
