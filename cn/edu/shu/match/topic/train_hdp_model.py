import logging
import os
import os.path
import pickle
import sys
import jieba
import jieba.analyse
from gensim import models

module_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir, os.pardir, os.pardir, os.pardir))
sys.path.append(module_path)
for a_path in sys.path:
    if os.path.exists(os.path.join(a_path, 'cn', 'edu', 'shu', 'match')):
        os.chdir(os.path.join(a_path, 'cn', 'edu', 'shu', 'match'))
        break

from cn.edu.shu.match.topic.get_documents import MyDocument
from cn.edu.shu.match.topic.train_corpus import MyCorpus
from cn.edu.shu.match.topic.train_tf_idf_model import MyTfIdfModel
from cn.edu.shu.match.topic.train_utils import Utils
from cn.edu.shu.match.topic.train_dictionary import MyDictionary
from cn.edu.shu.match.topic.preprocess import get_config_json
import cn.edu.shu.match.global_variable as gl

config_json = get_config_json(gl.config_path)
hdp_config_json = get_config_json(gl.hdp_config_path)
require_table_json = get_config_json(gl.require_table_path)
provide_table_json = get_config_json(gl.provide_table_path)
jieba.analyse.set_stop_words(config_json['gensim_stopword_path'])
jieba.load_userdict(config_json['gensim_dict_path'])
# jieba.analyse.set_idf_path(config_json['gensim_normalization_tf_idf_path'])
jieba.analyse.set_idf_path(config_json['gensim_tf_idf_path'])


class MyHdpModel(object):
    """

    """

    def __init__(self):
        """

        :return:
        """
        self.hdp_model_path = config_json['gensim_hdp_model_path']
        self.hdp_model = None

    @classmethod
    def update_hdp_config(cls):
        """
        根据训练使用过的文档修改配置文件使用或的文档id
        :return:
        """
        Utils.update_train_file_used_config(gl.hdp_config_path, 'hdp')

    def re_train_or_update_hdp(self, update=True):
        """
        得到或更新hdp主题模型
        :param update:
        :return:
        """
        # 更新词典
        dictionary = MyDictionary()
        dictionary.re_train_or_update_dictionary()
        dictionary = dictionary.get_dictionary()
        # 重新得到语料库
        corpus = MyCorpus()
        if not corpus.re_train_corpus():
            # 语料库不存在
            return None
        tf_idf_model = MyTfIdfModel()
        if corpus.is_update():
            # 语料库有更新，重新得到tf_idf模型
            tf_idf_model.re_train_tf_idf(corpus.get_corpus())
        tf_idf_model = tf_idf_model.get_tf_idf()
        if update:
            if not self.hdp_model:
                if not self.get_hdp():
                    # 语料不够，没有模型
                    return None
            documents = MyDocument(train_file=hdp_config_json['hdp_train_used'],
                                   begin_require_id=int(hdp_config_json['hdp_max_require_id_used']),
                                   begin_provide_id=int(hdp_config_json['hdp_max_provide_id_used']),
                                   begin_patent_id=int(hdp_config_json['hdp_max_patent_id_used']))
            if 1 == documents.judge_document_exist():
                logging.warning("开始更新hdp模型")
                self.hdp_model.update(tf_idf_model[MyCorpus.get_corpus_by_document(documents)])
                logging.warning("结束更新hdp模型")
        else:
            logging.warning("开始重新训练hdp模型")
            self.hdp_model = models.HdpModel(tf_idf_model[corpus.get_corpus()], id2word=dictionary)
            logging.warning("结束重新训练hdp模型")
        self.hdp_model.save(self.hdp_model_path)
        MyHdpModel.update_hdp_config()
        return self.hdp_model

    def get_hdp(self):
        """
        得到hdp主题模型
        :return:
        """
        try:
            self.hdp_model = models.HdpModel.load(self.hdp_model_path)
            return self.hdp_model
        except pickle.UnpicklingError:
            if not self.re_train_or_update_hdp():
                return None
        return self.hdp_model
