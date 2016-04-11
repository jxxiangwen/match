import logging
import os
import os.path
import sys
import jieba
import jieba.analyse


module_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir, os.pardir, os.pardir, os.pardir))
sys.path.append(module_path)
for a_path in sys.path:
    if os.path.exists(os.path.join(a_path, 'cn', 'edu', 'shu', 'match')):
        os.chdir(os.path.join(a_path, 'cn', 'edu', 'shu', 'match'))
        break

import cn.edu.shu.match.global_variable as gl
from gensim import corpora
from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.topic.get_documents import MyDocument
from cn.edu.shu.match.topic.train_utils import Utils
from cn.edu.shu.match.topic.train_dictionary import MyDictionary
from cn.edu.shu.match.topic.preprocess import get_config_json

ms_sql = MsSql()
config_json = get_config_json(gl.config_path)
corpus_config_json = get_config_json(gl.corpus_config_path)
temp_corpus_config_json = get_config_json(gl.temp_corpus_config_path)
require_table_json = get_config_json(gl.require_table_path)
provide_table_json = get_config_json(gl.provide_table_path)
jieba.analyse.set_stop_words(config_json['gensim_stopword_path'])
jieba.load_userdict(config_json['gensim_dict_path'])
# jieba.analyse.set_idf_path(config_json['gensim_normalization_tf_idf_path'])
jieba.analyse.set_idf_path(config_json['gensim_tf_idf_path'])


class MyCorpus(object):
    def __init__(self):
        """

        :return:
        """
        self.corpus_path = config_json['gensim_corpus_path']
        self.corpus = None
        self.isUpdate = True

    def is_update(self):
        """
        语料库是否更新
        :return:
        """
        return self.isUpdate

    @classmethod
    def update_corpus_config(cls):
        """
        根据训练使用过的文档修改配置文件使用过的文档id
        :return:
        """
        Utils.update_train_file_used_config(gl.corpus_config_path, 'corpus')

    @classmethod
    def update_temp_corpus_config(cls):
        """
        根据训练使用过的文档修改临时语料库使用过的文档id
        :return:
        """
        Utils.update_train_file_used_config(gl.temp_corpus_config_path, 'corpus')

    @classmethod
    def get_corpus_by_document(cls, dictionary, texts, patent=False):
        """
        通过新文章返回语料
        :param dictionary:
        :param texts:
        :param patent:
        :return:
        """
        if not texts:
            return
        import collections
        if isinstance(texts, str):
            dictionary.add_documents(Utils.add_list_round(texts))
            yield dictionary.doc2bow(jieba.cut(texts))
        # 是专利数据
        elif patent:
            for text in texts:
                if len(text) != 0:
                    yield dictionary.doc2bow(jieba.cut(text[0][1] + text[0][2]))
        elif isinstance(texts, collections.Iterable):
            for text in texts:
                dictionary.add_documents(Utils.add_list_round(text))
                yield dictionary.doc2bow(jieba.cut(text))
        else:
            raise TypeError('只支持str和list类型，不支持%d类型' % (type(texts)))

    def get_corpus(self):
        """
        得到语料库
        :return:
        """
        try:
            if not self.corpus:
                self.corpus = corpora.MmCorpus(self.corpus_path)
            return self.corpus
        except:
            self.re_train_corpus()
            return self.corpus

    def re_train_corpus(self):
        """
        重新或更新训练语料库
        :return:
        """
        logging.warning("开始重新训练语料库")
        documents = MyDocument(train_file=temp_corpus_config_json['corpus_train_used'],
                               begin_require_id=int(temp_corpus_config_json['corpus_max_require_id_used']),
                               begin_provide_id=int(temp_corpus_config_json['corpus_max_provide_id_used']),
                               begin_patent_id=int(temp_corpus_config_json['corpus_max_patent_id_used']))
        # 没有更新直接返回原始语料库
        if 0 == documents.judge_document_exist():
            logging.warning("语料库没有更新")
            try:
                if not self.corpus:
                    self.corpus = corpora.MmCorpus(self.corpus_path)
                self.isUpdate = False
                return self.corpus
            except:
                return None
        # 清空语料训练数据
        with open(self.corpus_path, mode='w', encoding='utf-8'):
            logging.warning("清空语料库数据")
            pass
        documents = MyDocument(train_file=corpus_config_json['corpus_train_used'],
                               begin_require_id=int(corpus_config_json['corpus_max_require_id_used']),
                               begin_provide_id=int(corpus_config_json['corpus_max_provide_id_used']),
                               begin_patent_id=int(corpus_config_json['corpus_max_patent_id_used']))
        dictionary = MyDictionary()
        dictionary.re_train_or_update_dictionary()
        dictionary = dictionary.get_dictionary()
        self.corpus = (dictionary.doc2bow(Utils.yield_document(document, participle=True, add_list=False))
                       for document in documents)
        corpora.MmCorpus.serialize(self.corpus_path, self.corpus)
        # MyCorpus.update_corpus_config()
        MyCorpus.update_temp_corpus_config()
        logging.warning("结束重新训练语料库")
        return self.corpus
