#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.process.model import Model
from cn.edu.shu.match.process.get_text import get_data_from_text
import sys

__author__ = 'jxxia'

"""
需求模型
"""


class RequireModel(Model):
    """
    需求模型
    """

    def __init__(self, algorithm_type, require_id=[], read_file=True, match_need=dict()):
        """
        初始化函数
        :param algorithm_type: 需要训练的算法类型
        :param read_file: 是否从文件中读取conclude和weight数据
        :param match_need: 如果read_file为False，此处必填
        :return:
        """
        super().__init__(algorithm_type, read_file, match_need)
        self._document_id = require_id

    def set_text(self, train='all'):
        """
        设置匹配数据
        :param train: 为'train'使用训练数据，为'test'使用测试数据,'all'使用所有数据
        """
        super().set_text(train)
        if 'all' != train:
            try:
                self._document_id = self._mongo.find()['require_id']
            except KeyError as e:
                print("集合{}文件中不存在{}字段".format(self._train_collection, 'require_id'))
                sys.exit()
            assert len(self._document_id) > 0, "集合{}文件中不存在{}字段长度为0".format(self._train_collection, 'require_id')
        else:
            if 0 == len(self._document_id):
                ms_sql = MsSql()
                require_str = "select RequireDocInfor_ID from RequireDocInfor where RequireDocInfor_status not in (0)"
                results = ms_sql.exec_search(require_str)
                if 0 == len(results):
                    return
                # 得到需求id
                self._document_id = [result[0] for result in results]
                # 获取语料库
        self._text = get_data_from_text(self._document_id, self._algorithm_config_path, 'require',
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
