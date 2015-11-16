#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cn.edu.shu.match.build_mongodb import Mongo
import json

__author__ = 'jxxia'

"""
匹配模型
"""


class Model(object):
    """
    匹配模型接口，定义模型需要实现的函数
    """

    def __init__(self, algorithm_type, read_file=True, match_need=dict()):
        """
        初始化函数
        :param algorithm_type: 需要训练的算法类型
        :param read_file: 是否从文件中读取conclude和weight数据
        :param match_need: 如果read_file为False，此处必填
        :return:
        """
        self._mongo = Mongo()  # 连接MongoDB数据库
        self._text = None  # 保存模型训练文本
        self._index = None  # 保存训练
        self._dictionary = None  # 保存训练词典
        self._tf_idf = None  # 保存训练的TF-IDF值
        self._model = None  # 保存模型训练结果
        self._corpus = None  # 保存模型训练语料
        self._algorithm_type = algorithm_type  # 训练的算法类型
        if not read_file:
            assert len(match_need) > 0, "match_need不能为空"
        self._read_file = read_file  # 是否从配置文件中读取语料库
        self._match_need = match_need  # 如果read_file为False，此处必填
        with open('./config/mongodb.json', encoding='utf-8') as mongodb_file:
            mongodb_json = json.load(mongodb_file)
            self._train_collection = mongodb_json['train']  # 训练配置文件集合名
            self._test_collection = mongodb_json['test']  # 测试配置文件地址
        with open('./process/path.json', encoding='utf-8') as path_file:
            path_json = json.load(path_file)
            self._algorithm_config_path = path_json['algorithm_config_path']  # 算法配置文件地址
            self._save_path = path_json['save_path']  # 训练结果保存目录
            self._database_path = path_json['database_path']  # 数据库配置文件地址

    def set_text(self, train=True):
        """
        设置训练数据
        :param train: 为True使用训练数据，否则使用测试数据
        :return: None
        """
        if train:
            self._mongo.set_collection(self._train_collection)  # 将MongoDB集合设置为训练集
        else:
            self._mongo.set_collection(self._test_collection)  # 将MongoDB集合设置为测试集合

    def get_text(self):
        """
        返回训练数据
        :return: 训练数据
        """
        return self._text

    def train(self, model_type, doc_type, re_train=True, num_topics=5):
        """
        训练模型
        :param model_type: 需要训练的模型类型
        :param doc_type: 需要训练的文本类型
        :param re_train: 重新训练还是直接读取训练结果
        :param num_topics: 需要训练的模型的主题数目
        :return: None
        """
        from gensim import corpora, models, similarities
        # import time

        # start = time.clock()
        if re_train:
            # print("正在重新训练模型")
            # print("lib_texts,", lib_texts)
            self._dictionary = corpora.Dictionary(self._text)  # 将文本转化为词典形式为(word,word_id)
            #  logging.info("dictionary: %s" % dictionary)
            self._corpus = [self._dictionary.doc2bow(text) for text in self._text]  # 根据词典对文本进行处理
            # doc2bow(): 将collection words 转为词袋，用两元组(word_id, word_frequency)表示
            # logging.warning("corpus: %s" % corpus)
            self._tf_idf = models.TfidfModel(self._corpus)  # 训练td-idf模型
            #  logging.info("tfidf: %s" % tfidf)
            corpus_tfidf = self._tf_idf[self._corpus]  # 得到文本的td-idf数据
            #  logging.info("corpus_tfidf: %s" % corpus_tfidf)
            # 根据model_type训练相应模型
            if 'lsi' == model_type:
                self._model = models.LsiModel(corpus_tfidf, id2word=self._dictionary, num_topics=num_topics)
            elif 'lda' == model_type:
                self._model = models.LdaModel(corpus_tfidf, id2word=self._dictionary, num_topics=num_topics)
            else:
                raise TypeError("模型类型{}不存在".format(model_type))

            self._index = similarities.MatrixSimilarity(
                self._model[self._corpus])  # index 是 gensim.similarities.docsim.MatrixSimilarity 实例
            #  logging.info("index: %s" % index)

            # 保存训练结果
            self._dictionary.save('{}/{}.dict'.format(self._save_path, doc_type))
            corpora.MmCorpus.serialize('{}/{}.corpus'.format(self._save_path, doc_type), self._corpus)
            self._index.save('{}/{}.index'.format(self._save_path, doc_type))
            self._model.save('{}/{}.{}'.format(self._save_path, doc_type, model_type))
        else:
            # print("正在加载已训练模型")
            # 从保存的训练数据中加载返回
            self._dictionary = corpora.Dictionary.load('{}/{}.dict'.format(self._save_path, doc_type))
            self._corpus = corpora.MmCorpus('{}/{}.corpus'.format(self._save_path, doc_type))
            self._index = similarities.MatrixSimilarity.load('{}/{}.index'.format(self._save_path, doc_type))
            if 'lsi' == model_type:
                self._model = models.LsiModel.load('{}/{}.{}'.format(self._save_path, doc_type, model_type))
            elif 'lda' == model_type:
                self._model = models.LdaModel.load('{}/{}.{}'.format(self._save_path, doc_type, model_type))
            else:
                raise TypeError("模型类型{}不存在".format(model_type))
        # end = time.clock()
        # print("模型构建运行了: %f 秒" % (end - start))

    def get_model(self):
        """
        得到模型训练结果
        :return: 模型训练结果
        """
        return tuple((self._index, self._dictionary, self._model))

    def get_document_id(self):
        """
        得到模型文档id号
        :return: 模型训练结果
        """
        pass

        # if __name__ == '__main__':
        #     with open('./path.json', encoding='utf-8') as path_file:
        #         path_json = json.load(path_file)
        #         print(path_json['train_path'])  # 训练配置文件地址
