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
for a_path in sys.path:
    if os.path.exists(os.path.join(a_path, 'cn', 'edu', 'shu', 'match')):
        os.chdir(os.path.join(a_path, 'cn', 'edu', 'shu', 'match'))
        break

from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.topic.preprocess import get_config_json
from cn.edu.shu.match.read_property import change_json_file
from cn.edu.shu.match.process.get_text import get_data_from_text
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


def yield_document(texts, patent=False, add_list=True, participle=False):
    """
    对数据进行预处理
    :param texts:文章
    :param patent:是否是从数据库中获得的新词
    :param add_list:是否用列表包围数据列表
    :param participle:是否分词
    :return:
    """
    import collections
    if isinstance(texts, str):
        if add_list:
            return add_list_round(texts)
        elif participle:
            return jieba.analyse.extract_tags(texts, topK=10000)
        else:
            return texts
    # # 是专利数据
    # elif patent:
    #     for text in texts:
    #         if len(text) != 0:
    #             if add_list:
    #                 yield add_list_round(text[1] + text[2])
    #             if participle:
    #                 return jieba.analyse.extract_tags(text[1] + text[2], topK=10000)
    #             else:
    #                 yield text[1] + text[2]
    elif isinstance(texts, collections.Iterable):
        for text in texts:
            if text and 0 != len(text):
                if add_list:
                    if isinstance(text, list):
                        return text
                    else:
                        return add_list_round(text)
                elif participle:
                    # print(texts)
                    if isinstance(text, list):
                        return jieba.analyse.extract_tags(text[0], topK=10000)
                    else:
                        return jieba.analyse.extract_tags(text, topK=10000)
                else:
                    if isinstance(text, list):
                        return text[0]
                    else:
                        return text
    else:
        raise TypeError('只支持str和list类型，不支持%d类型' % (type(texts)))


def return_result(start, end):
    """
    根据开始和结束返回结果
    :param start:
    :param end:
    :return:
    """
    print("SELECT {},{},{},{} FROM {} WHERE {} BETWEEN {} AND {}".format(*config_json['patent_table_column_name'],
                                                                         config_json['patent_table'],
                                                                         config_json['patent_table_column_name'][0],
                                                                         start, end))
    return (ms_sql.exec_continue_search(
        "SELECT {},{},{},{} FROM {} WHERE {} BETWEEN {} AND {}".format(*config_json['patent_table_column_name'],
                                                                       config_json['patent_table'],
                                                                       config_json['patent_table_column_name'][0],
                                                                       start, end)))


class MyCorpus(object):
    def __init__(self, corpus_dictionary):
        self.corpus_dictionary = corpus_dictionary

    def __iter__(self):
        with open(config_json['train_path'], encoding='utf-8') as train_file:
            # print('begin __iter__ corpus')
            for train in train_file:
                if 0 != len(train):
                    yield self.corpus_dictionary.doc2bow(yield_document(train, participle=True, add_list=False))
        # 利用需求数据
        # 最大需求id序号
        max_require_id = ms_sql.exec_continue_search(
            "SELECT MAX (RequireDocInfor_ID) FROM RequireDocInfor WHERE RequireDocInfor_status NOT IN (0)")
        # 对需求数据进行分割，防止数据过大导致内存溢出
        id_range_list = (list(range(0, int(max_require_id[0][0]), 100)))
        id_range_list_len = len(id_range_list)
        if 0 != len(id_range_list):
            if 1 == len(id_range_list):
                # 获取语料库
                require_result = get_data_from_text(range(0, max_require_id[0][0] + 1), gl.algorithm_config_path,
                                                    'require')
                for require in require_result:
                    if 0 != len(require[0]):
                        yield self.corpus_dictionary.doc2bow(
                            yield_document(require[0], participle=True, add_list=False))
            else:
                for index in range(id_range_list_len):
                    if index + 1 < id_range_list_len:
                        # 获取语料库
                        require_result = get_data_from_text(
                            range(id_range_list[index], id_range_list[index + 1] - 1),
                            gl.algorithm_config_path, 'require')
                        for require in require_result:
                            if 0 != len(require[0]):
                                yield self.corpus_dictionary.doc2bow(
                                    yield_document(require[0], participle=True, add_list=False))
                require_result = get_data_from_text(range(id_range_list[-1], int(max_require_id[0][0]) + 1),
                                                    gl.algorithm_config_path, 'require')
                for require in require_result:
                    if 0 != len(require[0]):
                        yield self.corpus_dictionary.doc2bow(
                            yield_document(require[0], participle=True, add_list=False))
        # 利用服务数据
        # 最大服务id序号
        max_provide_id = ms_sql.exec_continue_search(
            "SELECT MAX (ProvideDocInfor_ID) FROM ProvideDocInfor WHERE ProvideDocInfor_status NOT IN (0)")
        # 对服务数据进行分割，防止数据过大导致内存溢出
        id_range_list = (list(range(0, int(max_provide_id[0][0]), 100)))
        id_range_list_len = len(id_range_list)
        if 0 != len(id_range_list):
            if 1 == len(id_range_list):
                # 获取语料库
                provide_result = get_data_from_text(range(0, max_provide_id[0][0] + 1), gl.algorithm_config_path,
                                                    'provide')
                for provide in provide_result:
                    if 0 != len(provide[0]):
                        yield self.corpus_dictionary.doc2bow(
                            yield_document(provide[0], participle=True, add_list=False))
            else:
                for index in range(id_range_list_len):
                    if index + 1 < id_range_list_len:
                        # 获取语料库
                        provide_result = get_data_from_text(
                            range(id_range_list[index], id_range_list[index + 1] - 1),
                            gl.algorithm_config_path, 'provide')
                        for provide in provide_result:
                            if 0 != len(provide[0]):
                                yield self.corpus_dictionary.doc2bow(
                                    yield_document(provide[0], participle=True, add_list=False))
                provide_result = get_data_from_text(range(id_range_list[-1], int(max_provide_id[0][0]) + 1),
                                                    gl.algorithm_config_path, 'provide')
                for provide in provide_result:
                    if 0 != len(provide[0]):
                        yield self.corpus_dictionary.doc2bow(
                            yield_document(provide[0], participle=True, add_list=False))
        # 利用专利数据
        # 最大专利id序号
        max_patent_id_result = ms_sql.exec_continue_search(
            "SELECT MAX({}) FROM {} ".format(config_json['patent_table_column_name'][0],
                                             config_json['patent_table']))
        # 对专利数据进行分割，防止数据过大导致内存溢出
        id_range_list = (list(range(0, int(max_patent_id_result[0][0]), 10000)))
        id_range_list_len = len(id_range_list)
        if 0 != len(id_range_list):
            if len(id_range_list) == 1:
                results = (ms_sql.exec_continue_search(
                    "SELECT {},{},{},{} FROM {} WHERE {} = {}".format(*config_json['patent_table_column_name'],
                                                                      config_json['patent_table'],
                                                                      config_json['patent_table_column_name'][0],
                                                                      patent_id)) for patent_id in
                           range(max_patent_id_result[0][0] + 1))
                for result in results:
                    if len(result) != 0:
                        yield self.corpus_dictionary.doc2bow(
                            yield_document(result[0][1] + result[0][2], participle=True, add_list=False))
            else:
                for index in range(id_range_list_len):
                    if index + 1 < id_range_list_len:
                        for text in return_result(id_range_list[index], id_range_list[index + 1] - 1):
                            if len(text) != 0:
                                yield self.corpus_dictionary.doc2bow(
                                    yield_document(text[0][1] + text[0][2], participle=True, add_list=False))
                for text in return_result(id_range_list[-1], int(max_patent_id_result[0][0])):
                    if 0 != len(text):
                        yield self.corpus_dictionary.doc2bow(
                            yield_document(text[0][1] + text[0][2], participle=True, add_list=False))
        # config_json['gensim_corpus_patent_max_id_used'] = max_patent_id_result[0][0]
        change_json_file(gl.config_path, **config_json)
        # 关闭数据库连接
        ms_sql.close_conn()


class TopicTrain(object):
    def __init__(self):
        self.dictionary_path = config_json['gensim_dictionary_path']
        self.corpus_path = config_json['gensim_corpus_path']
        self.tf_idf_model_path = config_json['gensim_tf_idf_model_path']
        self.lsi_model_path = config_json['gensim_lsi_model_path']
        self.lda_model_path = config_json['gensim_lda_model_path']
        self.hdp_model_path = config_json['gensim_hdp_model_path']
        self.ldamulticore_model_path = config_json['gensim_ldamulticore_model_path']
        self.dictionary = None
        self.corpus = None
        self.tf_idf_model = None
        self.lsi_model = None
        self.lda_model = None
        self.hdp_model = None
        self.ldamulticore_model = None

    def train_dictionary(self, update=True):
        """
        训练词典数据
        :param update: 是更新还是重新训练
        :return:
        """
        if not update:
            # 非更新则清空训练数据
            with open(self.dictionary_path, mode='w', encoding='utf-8'):
                pass
            # 先保存一次，避免出现None
            sentence = '张江科企资源共享平台'
            self.dictionary = corpora.Dictionary(add_list_round(sentence))
            self.dictionary.save(self.dictionary_path)
        else:
            # 更新则直接读取词典
            try:
                if not self.dictionary:
                    self.dictionary = corpora.Dictionary.load(self.dictionary_path)
            except pickle.UnpicklingError:
                # 词典不存在则重新训练
                self.train_dictionary(False)
        train_list = list()
        # 利用需求文件训练数据
        if not config_json['gensim_dictionary_train_used']:
            # print('需求文件')
            with open(config_json['train_path'], encoding='utf-8') as train_file:
                for train in train_file:
                    if 0 != len(train):
                        self.update_dictionary_by_text(train)
            config_json['gensim_dictionary_train_used'] = True
        # 利用需求数据
        # 最大需求id序号
        max_require_id = ms_sql.exec_continue_search(
            "SELECT MAX (RequireDocInfor_ID) FROM RequireDocInfor WHERE RequireDocInfor_status NOT IN (0)")
        # 对需求数据进行分割，防止数据过大导致内存溢出
        id_range_list = (
            list(range(int(config_json['gensim_max_require_id_used']), int(max_require_id[0][0]), 100)))
        id_range_list_len = len(id_range_list)
        if 0 != len(id_range_list):
            if 1 == len(id_range_list):
                # 获取语料库
                require_result = get_data_from_text(
                    range(int(config_json['gensim_max_require_id_used']), max_require_id[0][0] + 1),
                    gl.algorithm_config_path,
                    'require')
                for require in require_result:
                    if 0 != len(require[0]):
                        self.update_dictionary_by_text(require[0])
            else:
                for index in range(id_range_list_len):
                    if index + 1 < id_range_list_len:
                        # 获取语料库
                        require_result = get_data_from_text(range(id_range_list[index], id_range_list[index + 1] - 1),
                                                            gl.algorithm_config_path, 'require')
                        for require in require_result:
                            if 0 != len(require[0]):
                                self.update_dictionary_by_text(require[0])
                require_result = get_data_from_text(range(id_range_list[-1], int(max_require_id[0][0]) + 1),
                                                    gl.algorithm_config_path, 'require')
                for require in require_result:
                    if 0 != len(require[0]):
                        self.update_dictionary_by_text(require[0])
            config_json['gensim_max_require_id_used'] = max_require_id[0][0]
        # 利用服务数据
        # 最大服务id序号
        max_provide_id = ms_sql.exec_continue_search(
            "SELECT MAX (ProvideDocInfor_ID) FROM ProvideDocInfor WHERE ProvideDocInfor_status NOT IN (0)")
        # 对服务数据进行分割，防止数据过大导致内存溢出
        id_range_list = (
            list(range(int(config_json['gensim_max_provide_id_used']), int(max_provide_id[0][0]), 100)))
        id_range_list_len = len(id_range_list)
        if 0 != len(id_range_list):
            if 1 == len(id_range_list):
                # 获取语料库
                provide_result = get_data_from_text(
                    range(int(config_json['gensim_max_provide_id_used']), max_provide_id[0][0] + 1),
                    gl.algorithm_config_path, 'provide')
                for provide in provide_result:
                    if 0 != len(provide[0]):
                        self.update_dictionary_by_text(provide[0])
            else:
                for index in range(id_range_list_len):
                    if index + 1 < id_range_list_len:
                        # 获取语料库
                        provide_result = get_data_from_text(range(id_range_list[index], id_range_list[index + 1] - 1),
                                                            gl.algorithm_config_path, 'provide')
                        for provide in provide_result:
                            if 0 != len(provide[0]):
                                self.update_dictionary_by_text(provide[0])
                provide_result = get_data_from_text(range(id_range_list[-1], int(max_provide_id[0][0]) + 1),
                                                    gl.algorithm_config_path, 'provide')
                for provide in provide_result:
                    if 0 != len(provide[0]):
                        self.update_dictionary_by_text(provide[0])
            config_json['gensim_max_provide_id_used'] = max_provide_id[0][0]
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
        if 0 != len(id_range_list):
            if 1 == len(id_range_list):
                results = (ms_sql.exec_continue_search(
                    "SELECT {},{},{},{} FROM {} WHERE {} = {}".format(*config_json['patent_table_column_name'],
                                                                      config_json['patent_table'],
                                                                      config_json['patent_table_column_name'][0],
                                                                      patent_id)) for
                           patent_id in range(max_patent_id_result[0][0] + 1))
                for result in results:
                    if 0 != len(result):
                        self.update_dictionary_by_text(result[0][1] + result[0][2])
            else:
                for index in range(id_range_list_len):
                    if index + 1 < id_range_list_len:
                        for text in return_result(id_range_list[index], id_range_list[index + 1] - 1):
                            if 0 != len(text):
                                self.update_dictionary_by_text(text[0][1] + text[0][2])
                for text in return_result(id_range_list[-1], int(max_patent_id_result[0][0])):
                    if 0 != len(text):
                        self.update_dictionary_by_text(text[0][1] + text[0][2])
            config_json['gensim_dictionary_patent_max_id_used'] = max_patent_id_result[0][0]
        change_json_file(gl.config_path, **config_json)
        self.save_dictionary()
        # 关闭数据库连接
        ms_sql.close_conn()

    def update_dictionary_by_text(self, text):
        """
        利用新文章更新词典中的词
        :param text:文章
        :return:
        """
        try:
            if not self.dictionary:
                self.dictionary = corpora.Dictionary.load(self.dictionary_path)
            if text:
                self.dictionary.add_documents(add_list_round(text))
            return self.dictionary
        except pickle.UnpicklingError:
            # print('词典数据不存在，请训练后再调用')
            pass
        self.train_dictionary(False)
        self.dictionary = corpora.Dictionary.load(self.dictionary_path)
        if text:
            self.dictionary.add_documents(add_list_round(text))
        return self.dictionary

    def save_dictionary(self):
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
            # print('词典数据不存在，请训练后再调用')
            pass
        self.train_dictionary(False)
        self.dictionary = corpora.Dictionary.load(self.dictionary_path)
        return self.dictionary

    def get_corpus_by_document(self, texts, patent=False, tf_idf=True):
        """
        通过新文章返回语料
        :param texts:
        :param patent:
        :param tf_idf:
        :return:
        """
        import collections
        self.get_dictionary()
        if isinstance(texts, str):
            self.dictionary.add_documents(add_list_round(texts))
        # 是专利数据
        elif patent:
            for text in texts:
                if len(text) != 0:
                    yield self.dictionary.doc2bow(
                        jieba.analyse.extract_tags(text[0][1] + text[0][2], topK=10000))
        elif isinstance(texts, collections.Iterable):
            for text in texts:
                self.dictionary.add_documents(add_list_round(text))
        else:
            raise TypeError('只支持str和list类型，不支持%d类型' % (type(texts)))
        self.dictionary.save(self.dictionary_path)

    def get_corpus(self, re_train=False):
        """
        得到语料库
        :param re_train:
        :return:
        """
        try:
            if re_train:
                self.re_train_corpus()
            if not self.corpus:
                self.corpus = corpora.MmCorpus(self.corpus_path)
                return self.corpus
        except ValueError:
            pass
        self.re_train_corpus()
        # print('语料库数据不存在，请训练后再调用')
        self.corpus = corpora.MmCorpus(self.corpus_path)
        return self.corpus

    def re_train_corpus(self):
        """
        重新或更新训练语料库
        :return:
        """
        if not self.dictionary:
            self.get_dictionary()
        # 清空语料训练数据
        with open(self.corpus_path, mode='w', encoding='utf-8'):
            pass
        config_json['gensim_corpus_patent_max_id_used'] = 0

        corpus = MyCorpus(self.dictionary)
        corpora.MmCorpus.serialize(self.corpus_path, corpus)

    def set_tf_idf(self, update=False):
        """
        设置tf_idf模型
        :param update:
        :return:
        """
        if not self.corpus:
            self.get_corpus(update)
        # print(self.corpus)
        self.tf_idf_model = models.TfidfModel(self.corpus)
        self.save_tf_idf()
        return self.tf_idf_model

    def get_tf_idf(self):
        try:
            if not self.tf_idf_model:
                models.TfidfModel.load(self.tf_idf_model_path)
                return self.tf_idf_model
        except pickle.UnpicklingError:
            # print('词典数据不存在，请训练后再调用')
            pass
        return self.set_tf_idf()

    def save_tf_idf(self, update=False):
        """
        保存tf_idf模型
        :param update:
        :return:
        """
        if not self.tf_idf_model:
            self.set_tf_idf(update)
        self.tf_idf_model.save(self.tf_idf_model_path)

    def re_train_or_update_lsi(self, update=False, corpus=None):
        """
        得到或更新lda主题模型
        :param update:
        :param corpus:
        :return:
        """
        if not self.tf_idf_model:
            self.set_tf_idf(update)
        if not self.dictionary:
            self.get_dictionary()
        if update:
            if corpus:
                self.lsi_model.add_documents(self.tf_idf_model[corpus])
        self.lsi_model = models.LsiModel(self.tf_idf_model[self.corpus], id2word=self.dictionary,
                                         num_topics=config_json['lsi_model_num_topics'])
        self.lsi_model.save(self.lsi_model_path)
        # self.lsi_model.add_documents()

    def get_lsi(self):
        """
        得到lsi主题模型
        :return:
        """
        try:
            self.lsi_model = models.LsiModel.load(self.lsi_model_path)
            return self.lsi_model
        except pickle.UnpicklingError:
            self.re_train_or_update_lsi()
        return self.lsi_model

    def lsi_add_document(self, ):
        """

        :return:
        """

    def re_train_or_update_lda(self, update=False, corpus=None):
        """
        得到或更新lda主题模型
        :param update:
        :param corpus:
        :return:
        """
        print('re_train_or_update_lda')
        if not self.tf_idf_model:
            self.set_tf_idf(update)
        if not self.dictionary:
            self.get_dictionary()
        if update:
            if corpus:
                self.lda_model.update(self.tf_idf_model[corpus])
        else:
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
            return self.lda_model
        except pickle.UnpicklingError:
            self.re_train_or_update_lda()
        return self.lda_model

    def re_train_or_update_ldamulticore(self, update=False, corpus=None):
        """
        得到或更新lda主题模型
        :param update:
        :param corpus:
        :return:
        """
        print('re_train_or_update_ldamulticore')
        if not self.tf_idf_model:
            self.set_tf_idf(update)
        if not self.dictionary:
            self.get_dictionary()
        if update:
            if corpus:
                self.ldamulticore_model.update(self.tf_idf_model[corpus])
        else:
            self.ldamulticore_model = models.LdaMulticore(self.tf_idf_model[self.corpus], id2word=self.dictionary,
                                                          num_topics=config_json['ldamulticore_model_num_topics'])
        self.ldamulticore_model.save(self.ldamulticore_model_path)

    def get_ldamulticore(self):
        """
        得到lda主题模型
        :return:
        """
        try:
            self.ldamulticore_model = models.LdaMulticore.load(self.ldamulticore_model_path)
            return self.ldamulticore_model
        except pickle.UnpicklingError:
            self.re_train_or_update_ldamulticore()
        return self.ldamulticore_model

    def re_train_or_update_hdp(self, update=False, corpus=None):
        """
        得到或更新hdp主题模型
        :param update:
        :param corpus:
        :return:
        """
        if not self.tf_idf_model:
            self.set_tf_idf(update)
        if not self.dictionary:
            self.get_dictionary()
        if update:
            if corpus:
                self.hdp_model.update(self.tf_idf_model[corpus])
        self.hdp_model = models.HdpModel(self.tf_idf_model[self.corpus], id2word=self.dictionary)
        self.hdp_model.save(self.hdp_model_path)

    def get_hdp(self):
        """
        得到hdp主题模型
        :return:
        """
        try:
            self.hdp_model = models.HdpModel.load(self.hdp_model_path)
            return self.hdp_model
        except pickle.UnpicklingError:
            self.re_train_or_update_hdp()
        return self.hdp_model


if __name__ == '__main__':
    topic_train = TopicTrain()
    start = time.clock()
    # hdp = topic_train.get_hdp()
    # lda = hdp.hdp_to_lda()
    # # print(lda)
    # print(hdp.print_topics())
    # with open(config_json['train_path'], encoding='utf-8') as train_file:
    #     for train in train_file:
    #         print(lda.get_document_topics(dictionary.doc2bow(yield_document(train, participle=True, add_list=False))))
    # topic_train.get_corpus()
    # topic_train.get_tf_idf()
    topic_train.train_dictionary()
    topic_train.re_train_corpus()
    # tf_idf = topic_train.set_tf_idf()
    # print(tf_idf)
    # print(tf_idf[[(0, 1), (1, 1)]])
    topic_train.set_tf_idf()
    topic_train.save_tf_idf()
    topic_train.re_train_or_update_lsi()
    topic_train.re_train_or_update_lda()
    topic_train.re_train_or_update_hdp()
    # lsi = topic_train.get_lsi()
    # for topic in lsi.print_topics(10, 100):
    #     print(topic)
    # print("======================================")
    # topic_train.re_train_or_update_lda()
    # hdp = topic_train.get_hdp()
    # hdp.show_topics(10)
    # print('================================')
    # lda = topic_train.get_lda()
    # # print(lda.print_topics(1))
    # for id in range(10):
    #     print(lda.get_topic_terms(id))
    # print('================================')
    # for topic in lda.print_topics(10, 100):
    #     print(topic)
    # print('================================')
    # with open(config_json['train_path'], encoding='utf-8') as train_file:
    #     dictionary = topic_train.get_dictionary()
    #     for index, train in enumerate(train_file):
    #         if index > 5:
    #             break
    #         print(jieba.analyse.extract_tags(train, topK=10000))
    #         print(lda.get_document_topics(dictionary.doc2bow(jieba.analyse.extract_tags(train, topK=10000))))

    end = time.clock()
    print('lda运行时间：%s' % (end - start))
