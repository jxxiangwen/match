import time
import os
import os.path
import jieba
import jieba.analyse
import sys
import pickle
from gensim import corpora, models

module_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir, os.pardir, os.pardir, os.pardir))
sys.path.append(module_path)
project_path = os.path.join(sys.path[1], 'cn', 'edu', 'shu', 'match')  # 改变项目运行路径
os.chdir(project_path)

from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.topic.preprocess import get_config_json
from cn.edu.shu.match.read_property import change_json_file
import cn.edu.shu.match.global_variable as gl

ms_sql = MsSql()
config_json = get_config_json(gl.config_path)
jieba.analyse.set_stop_words(config_json['gensim_stopword_path'])
jieba.load_userdict(config_json['gensim_dict_path'])
# jieba.analyse.set_idf_path(config_json['gensim_normalization_tf_idf_path'])
jieba.analyse.set_idf_path(config_json['gensim_tf_idf_path'])


def add_list_round(sentence):
    """

    :param sentence:
    :return:
    """
    init_list = list()
    init_list.append(jieba.analyse.extract_tags(sentence, topK=10000))
    return init_list


def return_result(start, end):
    """
    根据开始和结束返回结果
    :param start:
    :param end:
    :return:
    """
    return (ms_sql.exec_continue_search(
        "SELECT {},{},{},{} FROM {} WHERE {} = {}".format(*config_json['patent_table_column_name'],
                                                          config_json['patent_table'],
                                                          config_json['patent_table_column_name'][0],
                                                          patent_id)) for
            patent_id in range(start, end))


class TopicTrain(object):
    def __init__(self):
        self.dictionary_path = config_json['gensim_dictionary_path']
        self.corpus_path = config_json['gensim_corpus_path']
        self.tf_idf_model_path = config_json['gensim_tf_idf_model_path']
        self.lsi_model_path = config_json['gensim_lsi_model_path']
        self.lda_model_path = config_json['gensim_lda_model_path']
        self.dictionary = None
        self.corpus = None
        self.tf_idf_model = None
        self.lsi_model = None
        self.lda_model = None

    def re_train_dictionary(self):
        """
        重新初始化词典数据
        :return:
        """
        # 清空训练数据
        with open(self.dictionary_path, mode='w', encoding='utf-8'):
            pass
        config_json['gensim_dictionary_patent_max_id_used'] = 0
        sentence = '张江科企资源共享平台'
        dictionary = corpora.Dictionary(add_list_round(sentence))
        dictionary.save(self.dictionary_path)
        train_list = list()
        # 利用词典训练数据
        with open(config_json['train_path'], encoding='utf-8') as train_file:
            self.add_dictionary(train_file)

        # 利用专利数据
        # 最大专利id序号
        max_patent_id_result = ms_sql.exec_continue_search(
            "SELECT MAX({}) FROM {} ".format(config_json['patent_table_column_name'][0],
                                             config_json['patent_table']))
        # 对专利数据进行分割，防止数据过大导致内存溢出
        id_range_list = (
            list(range(int(config_json['gensim_dictionary_patent_max_id_used']), int(max_patent_id_result[0][0]),
                       10000)))
        id_range_list_len = len(id_range_list)
        if len(id_range_list) == 1:
            results = (ms_sql.exec_continue_search(
                "SELECT {},{},{},{} FROM {} WHERE {} = {}".format(*config_json['patent_table_column_name'],
                                                                  config_json['patent_table'],
                                                                  config_json['patent_table_column_name'][0],
                                                                  patent_id)) for
                       patent_id in range(max_patent_id_result[0][0] + 1))
            self.add_dictionary(results, True)
        else:
            for index in range(id_range_list_len):
                if index + 1 < id_range_list_len:
                    self.add_dictionary(return_result(id_range_list[index], id_range_list[index + 1] - 1), True)
            self.add_dictionary(return_result(id_range_list[-1], int(max_patent_id_result[0][0])), True)
        # 关闭数据库连接
        ms_sql.close_conn()
        config_json['gensim_dictionary_patent_max_id_used'] = max_patent_id_result[0][0]
        change_json_file(gl.config_path, **config_json)

    def add_dictionary(self, texts, patent=False):
        """
        利用新文章更新词典中的词
        :param texts:文章
        :param patent:是否是从数据库中获得的新词
        :return:
        """
        import collections
        dictionary = corpora.Dictionary.load(self.dictionary_path)
        if isinstance(texts, str):
            dictionary.add_documents(add_list_round(texts))
        # 是专利数据
        elif patent:
            for text in texts:
                if len(text) != 0:
                    dictionary.add_documents(add_list_round(text[0][1] + text[0][2]))
        elif isinstance(texts, collections.Iterable):
            for text in texts:
                dictionary.add_documents(add_list_round(text))
        else:
            raise TypeError('只支持str和list类型，不支持%d类型' % (type(texts)))
        dictionary.save(self.dictionary_path)

    def set_dictionary(self):
        """
        得到词典
        :return:
        """
        try:
            self.dictionary = corpora.Dictionary.load(self.dictionary_path)
        except pickle.UnpicklingError:
            # print('词典数据不存在，请训练后再调用')
            self.re_train_dictionary()

    def set_corpus(self):
        """
        得到语料库
        :return:
        """
        try:
            self.corpus = corpora.MmCorpus(self.corpus_path)
        except ValueError:
            self.re_train_corpus()
            # print('语料库数据不存在，请训练后再调用')

    def re_train_corpus(self):
        """
        重新训练语料库
        :return:
        """
        if not self.dictionary:
            self.set_dictionary()
        # 清空语料训练数据
        with open(self.corpus_path, mode='w', encoding='utf-8'):
            pass
        config_json['gensim_corpus_patent_max_id_used'] = 0

        class MyCorpus(object):
            def __init__(self, corpus_dictionary):
                self.corpus_dictionary = corpus_dictionary

            def __iter__(self):
                with open(config_json['train_path'], encoding='utf-8') as train_file:
                    for train in train_file:
                        yield self.corpus_dictionary.doc2bow(jieba.analyse.extract_tags(train, topK=10000))
                    # 利用专利数据
                    # 最大专利id序号
                    max_patent_id_result = ms_sql.exec_continue_search(
                        "SELECT MAX({}) FROM {} ".format(config_json['patent_table_column_name'][0],
                                                         config_json['patent_table']))
                    # 对专利数据进行分割，防止数据过大导致内存溢出
                    id_range_list = (
                        list(range(int(config_json['gensim_dictionary_patent_max_id_used']),
                                   int(max_patent_id_result[0][0]), 10000)))
                    id_range_list_len = len(id_range_list)
                    if len(id_range_list) == 1:
                        results = (ms_sql.exec_continue_search(
                            "SELECT {},{},{},{} FROM {} WHERE {} = {}".format(*config_json['patent_table_column_name'],
                                                                              config_json['patent_table'],
                                                                              config_json['patent_table_column_name'][
                                                                                  0],
                                                                              patent_id)) for
                                   patent_id in range(max_patent_id_result[0][0] + 1))
                        for result in results:
                            if len(result) != 0:
                                yield self.corpus_dictionary.doc2bow(
                                    jieba.analyse.extract_tags(result[0][1] + result[0][2], topK=10000))
                    else:
                        for index in range(id_range_list_len):
                            if index + 1 < id_range_list_len:
                                for text in return_result(id_range_list[index], id_range_list[index + 1] - 1):
                                    if len(text) != 0:
                                        yield self.corpus_dictionary.doc2bow(
                                            jieba.analyse.extract_tags(text[0][1] + text[0][2], topK=10000))
                                for text in return_result(id_range_list[-1], int(max_patent_id_result[0][0])):
                                    yield self.corpus_dictionary.doc2bow(
                                        jieba.analyse.extract_tags(text[0][1] + text[0][2], topK=10000))
                    # 关闭数据库连接
                    ms_sql.close_conn()
                    config_json['gensim_corpus_patent_max_id_used'] = max_patent_id_result[0][0]
                    change_json_file(gl.config_path, **config_json)

        corpus = MyCorpus(self.dictionary)
        corpora.MmCorpus.serialize(self.corpus_path, corpus)

    def set_tf_idf(self):
        """
        设置tf_idf模型
        :return:
        """
        if not self.corpus:
            self.set_corpus()
        self.tf_idf_model = models.TfidfModel(self.corpus)

    def save_tf_idf(self):
        """
        保存tf_idf模型
        :return:
        """
        if not self.tf_idf_model:
            self.set_tf_idf()
        self.tf_idf_model.save(self.tf_idf_model_path)

    def re_train_lsi(self):
        """
        重新训练lsi主题模型
        :return:
        """
        if not self.tf_idf_model:
            self.set_tf_idf()
        if not self.dictionary:
            self.set_dictionary()
        self.lsi_model = models.LsiModel(self.tf_idf_model[self.corpus], id2word=self.dictionary,
                                         num_topics=config_json['lsi_model_num_topics'])
        self.lsi_model.save(self.lsi_model_path)

    def get_lsi(self):
        """
        重新训练lsi主题模型
        :return:
        """
        try:
            self.lsi_model = models.LsiModel.load(self.lsi_model_path)
        except pickle.UnpicklingError:
            self.re_train_lsi()

    def re_train_lda(self):
        """
        得到lda主题模型
        :return:
        """
        if not self.tf_idf_model:
            self.set_tf_idf()
        if not self.dictionary:
            self.set_dictionary()
        self.lda_model = models.LdaModel(self.tf_idf_model[self.corpus], id2word=self.dictionary,
                                         num_topics=config_json['lda_model_num_topics'])
        self.lda_model.save(self.lda_model_path)

    def get_lda(self):
        """
        得到lda主题模型
        :return:
        """
        try:
            self.lda_model = models.LdaModel.load(self.lda_model_path)
        except pickle.UnpicklingError:
            self.re_train_lda()


if __name__ == '__main__':
    topic_train = TopicTrain()
    start = time.clock()
    # topic_train.re_train_dictionary()
    # topic_train.re_train_corpus()
    # topic_train.set_tf_idf()
    # topic_train.save_tf_idf()
    topic_train.re_train_lsi()
    topic_train.re_train_lda()
    end = time.clock()
    print('运行时间：%s' % (end - start))
