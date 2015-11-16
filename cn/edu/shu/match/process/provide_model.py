#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cn.edu.shu.match.process.model import Model
from cn.edu.shu.match.process.get_text import get_data_from_text
import sys

__author__ = 'jxxia'

"""
服务模型
"""


class ProvideModel(Model):
    """
    服务模型
    """

    def __init__(self, algorithm_type, read_file=True, match_need=dict()):
        """
        初始化函数
        :param algorithm_type: 需要训练的算法类型
        :param read_file: 是否从文件中读取conclude和weight数据
        :param match_need: 如果read_file为False，此处必填
        :return:
        """
        super().__init__(algorithm_type, read_file, match_need)
        self._document_id = list()

    def set_text(self, train=True):
        """
        设置训练数据
        :param train: 为True使用训练数据，否则使用测试数据
        """
        super().set_text(train)
        self._mongo.set_collection(self._train_collection)  # 将MongoDB集合设置为训练集
        try:
            self._document_id = self._mongo.find()['provide_id']
        except KeyError as e:
            print("集合{}文件中不存在{}字段".format(self._train_collection, 'provide_id'))
            sys.exit()
        assert len(self._document_id) > 0, "集合{}文件中不存在{}字段长度为0".format(self._train_collection, 'provide_id')
        # 获取语料库
        self._text = get_data_from_text(self._document_id, self._algorithm_config_path, 'provide',
                                        self._algorithm_type, self._read_file, self._match_need)

    def train(self, model_type, doc_type, re_train=True, num_topics=5):
        """
        训练模型
        :param model_type: 需要训练的模型类型
        :param doc_type: 需要训练的文本类型
        :param re_train: 重新训练还是直接读取训练结果
        :param num_topics: 需要训练的模型的主题数目
        :return: None
        """
        super().train(model_type, doc_type, re_train, num_topics)

    def get_document_id(self):
        """
        得到模型文档id号
        :return: 模型训练结果
        """
        return self._document_id
