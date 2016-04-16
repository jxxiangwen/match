import logging
import os
import os.path
import pickle
import sys
import time

import jieba
import jieba.analyse
from gensim import corpora, models

module_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir, os.pardir, os.pardir, os.pardir))
sys.path.append(module_path)
for a_path in sys.path:
    if os.path.exists(os.path.join(a_path, 'cn', 'edu', 'shu', 'match')):
        os.chdir(os.path.join(a_path, 'cn', 'edu', 'shu', 'match'))
        break

from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.topic.preprocess import get_config_json
import cn.edu.shu.match.global_variable as gl

ms_sql = MsSql()
config_json = get_config_json(gl.config_path)
require_table_json = get_config_json(gl.require_table_path)
provide_table_json = get_config_json(gl.provide_table_path)
jieba.analyse.set_stop_words(config_json['gensim_stopword_path'])
jieba.load_userdict(config_json['gensim_dict_path'])
# jieba.analyse.set_idf_path(config_json['gensim_normalization_tf_idf_path'])
jieba.analyse.set_idf_path(config_json['gensim_tf_idf_path'])


class MyTfIdfModel(object):
    """

    """

    def __init__(self):
        """

        :return:
        """
        self.tf_idf_model_path = config_json['gensim_tf_idf_model_path']
        self.tf_idf_model = None

    def re_train_tf_idf(self, corpus):
        """
        设置tf_idf模型
        :param corpus:
        :return:
        """
        logging.warning("开始重新训练tf_idf模型")
        logging.warning("corpus:{}".format(corpus))
        self.tf_idf_model = models.TfidfModel(corpus)
        self.save_tf_idf()
        logging.warning("结束重新训练tf_idf模型")

    def get_tf_idf(self):
        """

        :return:
        """
        try:
            if not self.tf_idf_model:
                self.tf_idf_model = models.TfidfModel.load(self.tf_idf_model_path)
            return self.tf_idf_model
        except pickle.UnpicklingError:
            return self.re_train_tf_idf()

    def save_tf_idf(self):
        """
        保存tf_idf模型
        :return:
        """
        if not self.tf_idf_model:
            self.re_train_tf_idf()
        self.tf_idf_model.save(self.tf_idf_model_path)
