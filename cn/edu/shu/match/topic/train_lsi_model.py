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
lsi_config_json = get_config_json(gl.lsi_config_path)
require_table_json = get_config_json(gl.require_table_path)
provide_table_json = get_config_json(gl.provide_table_path)
jieba.analyse.set_stop_words(config_json['gensim_stopword_path'])
jieba.load_userdict(config_json['gensim_dict_path'])
# jieba.analyse.set_idf_path(config_json['gensim_normalization_tf_idf_path'])
jieba.analyse.set_idf_path(config_json['gensim_tf_idf_path'])


class MyLsiModel(object):
    """

    """

    def __init__(self):
        """

        :return:
        """
        self.lsi_model_path = config_json['gensim_lsi_model_path']
        self.lsi_model = None

    @classmethod
    def update_lsi_config(cls):
        """
        根据训练使用过的文档修改配置文件使用或的文档id
        :return:
        """
        Utils.update_train_file_used_config(gl.lsi_config_path, 'lsi')

    def re_train_or_update_lsi(self, update=True):
        """
        得到或更新lda主题模型
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
            if not self.lsi_model:
                if not self.get_lsi():
                    # 语料不够，没有模型
                    return None
            documents = MyDocument(train_file=lsi_config_json['lsi_train_used'],
                                   begin_require_id=int(lsi_config_json['lsi_max_require_id_used']),
                                   begin_provide_id=int(lsi_config_json['lsi_max_provide_id_used']),
                                   begin_patent_id=int(lsi_config_json['lsi_max_patent_id_used']))
            if 1 == documents.judge_document_exist():
                logging.warning("开始更新lsi模型")
                self.lsi_model.add_documents(tf_idf_model[MyCorpus.get_corpus_by_document(documents)])
                logging.warning("结束更新lsi模型")
        else:
            logging.warning("开始重新训练lsi模型")
            self.lsi_model = models.LsiModel(tf_idf_model[corpus.get_corpus()], id2word=dictionary,
                                             num_topics=lsi_config_json['lsi_model_num_topics'])
            logging.warning("结束重新训练lsi模型")
        self.lsi_model.save(self.lsi_model_path)
        MyLsiModel.update_lsi_config()
        return self.lsi_model

    def get_lsi(self):
        """
        得到lsi主题模型
        :return:
        """
        try:
            self.lsi_model = models.LsiModel.load(self.lsi_model_path)
            return self.lsi_model
        except pickle.UnpicklingError:
            if not self.re_train_or_update_lsi():
                return None
        return self.lsi_model
