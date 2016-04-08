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
from cn.edu.shu.match.topic.train_hdp_model import MyHdpModel
from cn.edu.shu.match.topic.train_utils import Utils
from cn.edu.shu.match.topic.train_dictionary import MyDictionary
from cn.edu.shu.match.topic.preprocess import get_config_json
import cn.edu.shu.match.global_variable as gl

config_json = get_config_json(gl.config_path)
lda_config_json = get_config_json(gl.lda_config_path)
require_table_json = get_config_json(gl.require_table_path)
provide_table_json = get_config_json(gl.provide_table_path)
jieba.analyse.set_stop_words(config_json['gensim_stopword_path'])
jieba.load_userdict(config_json['gensim_dict_path'])
# jieba.analyse.set_idf_path(config_json['gensim_normalization_tf_idf_path'])
jieba.analyse.set_idf_path(config_json['gensim_tf_idf_path'])


class MyLdaModel(object):
    """

    """

    def __init__(self):
        """

        :return:
        """
        self.lda_model_path = config_json['gensim_lda_model_path']
        self.lda_model = None

    @classmethod
    def update_lda_config(cls):
        """
        根据训练使用过的文档修改配置文件使用或的文档id
        :return:
        """
        Utils.update_train_file_used_config(gl.lda_config_path, 'lda')

    def re_train_or_update_lda(self, update=True, alpha='symmetric', beta=None):
        """
        得到或更新lda主题模型
        :param update:
        :param alpha:
        :param beta:
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
            if not self.lda_model:
                if not self.get_lda():
                    # 语料不够，没有模型
                    return None
            documents = MyDocument(train_file=lda_config_json['lda_train_used'],
                                   begin_require_id=int(lda_config_json['lda_max_require_id_used']),
                                   begin_provide_id=int(lda_config_json['lda_max_provide_id_used']),
                                   begin_patent_id=int(lda_config_json['lda_max_patent_id_used']))
            if 1 == documents.judge_document_exist():
                logging.warning("开始更新lda模型")
                self.lda_model.update(tf_idf_model[MyCorpus.get_corpus_by_document(documents)])
                logging.warning("结束更新lda模型")
        else:
            logging.warning("开始重新训练lda模型")
            self.lda_model = models.LdaModel(tf_idf_model[corpus.get_corpus()], id2word=dictionary,
                                             num_topics=lda_config_json['lda_model_num_topics'], alpha=alpha,
                                             eta=beta)
            logging.warning("结束重新训练lda模型")
        self.lda_model.save(self.lda_model_path)
        MyLdaModel.update_lda_config()
        return self.lda_model

    def get_lda(self):
        """
        得到lda主题模型
        :return:
        """
        try:
            self.lda_model = models.LdaModel.load(self.lda_model_path)
            return self.lda_model
        except pickle.UnpicklingError:
            if not self.re_train_or_update_lda():
                return None
        return self.lda_model

    def re_train_lda_by_hdp(self):
        """
        通过hdp模型训练lda模型
        :return: 
        """
        hdp_model = MyHdpModel()
        hdp_model.re_train_or_update_hdp()
        hdp_model = hdp_model.get_hdp()
        if not hdp_model:
            return None
        else:
            return self.re_train_or_update_lda(update=False, alpha=hdp_model.hdp_to_lda()[0],
                                               beta=hdp_model.hdp_to_lda()[1])
