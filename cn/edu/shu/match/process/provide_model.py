#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from cn.edu.shu.match.process.model import Model
from cn.edu.shu.match.process.get_text import get_data_from_text
from cn.edu.shu.match.tool import str_value_to_int_list

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
        :param read_file: 是否从配置文件中读取语料库
        :param match_need: 如果read_file为False，此处必填
        :return:
        """
        super().__init__(algorithm_type, read_file, match_need)
        self._document_id = list()

    def set_text(self):
        """
        设置训练语料库
        :return: None
        """
        with open(self._train_path, encoding='utf-8') as train_file:
            train_json = json.load(train_file)
            if not train_json['provide_id']:
                raise TypeError("配置文件中不存在{}字段".format('provide_id'))
            self._document_id = train_json['provide_id'].strip().split(',')  # 保存训练语料库中的需求id
        self._document_id = str_value_to_int_list(self._document_id)  # 将字符串id转化为整数id
        assert len(self._document_id) > 0, "配置文件中需求id不存在"
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
