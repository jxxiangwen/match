import logging
import os
import os.path
import pickle
import sys
import jieba
import jieba.analyse
from gensim import corpora

module_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir, os.pardir, os.pardir, os.pardir))
sys.path.append(module_path)
for a_path in sys.path:
    if os.path.exists(os.path.join(a_path, 'cn', 'edu', 'shu', 'match')):
        os.chdir(os.path.join(a_path, 'cn', 'edu', 'shu', 'match'))
        break

from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.topic.get_documents import MyDocument
from cn.edu.shu.match.topic.train_utils import Utils
from cn.edu.shu.match.topic.preprocess import get_config_json
import cn.edu.shu.match.global_variable as gl

ms_sql = MsSql()
config_json = get_config_json(gl.config_path)
dictionary_config_path = get_config_json(gl.dictionary_config_path)
require_table_json = get_config_json(gl.require_table_path)
provide_table_json = get_config_json(gl.provide_table_path)
jieba.analyse.set_stop_words(config_json['gensim_stopword_path'])
jieba.load_userdict(config_json['gensim_dict_path'])
# jieba.analyse.set_idf_path(config_json['dictionary_normalization_tf_idf_path'])
jieba.analyse.set_idf_path(config_json['gensim_tf_idf_path'])


class MyDictionary(object):
    """
    词典类，记录所有出现过的单词
    """

    def __init__(self):
        self.dictionary_path = config_json['gensim_dictionary_path']
        self.dictionary = None

    @classmethod
    def update_dictionary_config(cls):
        """
        根据训练使用过的文档修改配置文件使用或的文档id
        :return: 
        """
        Utils.update_train_file_used_config(gl.dictionary_config_path, 'dictionary')

    def __train_dictionary_by_document(self, documents):
        """
        通过词典训练
        :param documents:
        :return:
        """
        if not documents:
            return
        for document in documents:
            self.__update_dictionary_by_text(list(jieba.cut(document)))

    def __re_train_dictionary(self):
        """
        重新训练词典
        :return:
        """
        logging.warning('清空词典数据')
        # 非更新则清空训练数据
        with open(self.dictionary_path, mode='w', encoding='utf-8'):
            pass
        # 先保存一次，避免出现None
        sentence = '张江科企资源共享平台'
        self.dictionary = corpora.Dictionary(Utils.add_list_round(sentence))
        documents = MyDocument()
        if 1 == documents.judge_document_exist():
            self.__train_dictionary_by_document(documents)

    def __update_dictionary(self):
        """
        更新词典
        :return:
        """
        # 更新则直接读取词典
        try:
            if not self.dictionary:
                self.dictionary = corpora.Dictionary.load(self.dictionary_path)
        except pickle.UnpicklingError:
            # 词典不存在则重新训练
            self.__re_train_dictionary()
        documents = MyDocument(train_file=dictionary_config_path['dictionary_train_used'],
                               begin_require_id=int(dictionary_config_path['dictionary_max_require_id_used']),
                               begin_provide_id=int(dictionary_config_path['dictionary_max_provide_id_used']),
                               begin_patent_id=int(dictionary_config_path['dictionary_max_patent_id_used']))
        if 1 == documents.judge_document_exist():
            self.__train_dictionary_by_document(documents)

    def re_train_or_update_dictionary(self, update=True):
        """
        训练词典数据
        :param update: 是更新还是重新训练
        :return:
        """
        logging.warning("开始重新训练或更新词典")
        if update:
            self.__update_dictionary()
        else:
            self.__re_train_dictionary()
        # 更新使用过的id数据
        self.__save_dictionary()
        MyDictionary.update_dictionary_config()
        logging.warning("结束重新训练或更新词典")

    def update_dictionary_by_text(self, text):
        """
        利用新文章更新词典中的词
        :param text:文章
        :return:
        """
        self.__update_dictionary_by_text(text)
        self.__save_dictionary()

    def __update_dictionary_by_text(self, text):
        """
        利用新文章更新词典中的词
        :param text:文章
        :return:
        """
        try:
            if not self.dictionary:
                self.dictionary = corpora.Dictionary.load(self.dictionary_path)
            if text:
                self.dictionary.add_documents(Utils.add_list_round(text))
            return self.dictionary
        except pickle.UnpicklingError:
            self.__re_train_dictionary()
            self.dictionary = corpora.Dictionary.load(self.dictionary_path)
            if text:
                self.dictionary.add_documents(Utils.add_list_round(text))

    def __save_dictionary(self):
        """
        保存词典
        :return:
        """
        if self.dictionary:
            self.dictionary.save(self.dictionary_path)

    def get_dictionary(self):
        """
        得到词典
        :return:
        """
        try:
            if not self.dictionary:
                self.dictionary = corpora.Dictionary.load(self.dictionary_path)
            return self.dictionary
        except pickle.UnpicklingError:
            self.__re_train_dictionary()
            self.dictionary = corpora.Dictionary.load(self.dictionary_path)
            return self.dictionary
