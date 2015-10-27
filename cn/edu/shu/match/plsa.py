#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'jxxia'

from get_data import get_datas_from_text, get_one_from_text
import logging
from time import strftime, localtime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('log/plsa_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='a')


def train_by_plsa(lib_texts, topic_num=9):
    """
    通过LSI模型的训练
    :param lib_texts:训练文本
    :param topic_num:主题数目
    :return:plsa训练结果
    """
    from gensim import corpora, models, similarities
    # print("lib_texts,", lib_texts)
    dictionary = corpora.Dictionary(lib_texts)
    #  logging.info("dictionary: %s" % dictionary)
    corpus = [dictionary.doc2bow(text) for text in lib_texts]
    # doc2bow(): 将collection words 转为词袋，用两元组(word_id, word_frequency)表示
    # logging.warning("corpus: %s" % corpus)
    tfidf = models.TfidfModel(corpus)
    #  logging.info("tfidf: %s" % tfidf)
    corpus_tfidf = tfidf[corpus]
    #  logging.info("corpus_tfidf: %s" % corpus_tfidf)

    # 拍脑袋的：训练topic数量为10的LSI模型
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=topic_num)
    index = similarities.MatrixSimilarity(lsi[corpus])  # index 是 gensim.similarities.docsim.MatrixSimilarity 实例
    #  logging.info("index: %s" % index)
    return tuple((index, dictionary, lsi))


def get_result_from_plsa(require_id, provide_id, algorithm_config, doc_type='text', src='require', dest='provide',
                         read_file=True, match_need={}, topic_num=9):
    """
    文档匹配结果
    :param require_id:全局需求id
    :param provide_id:全局服务id
    :param algorithm_config:算法配置文件地址
    :param doc_type:获取文本方式，text读取完整文本，keys直接去除文本tfidf
    :param src:匹配源文档类型
    :param dest:匹配目标文档类型
    :param read_file:通过文件读取匹配所需还是通过match_need读取True为通过文件读取
    :param match_need：匹配所需信息
    :param topic_num:主题数目
    :return:元组，由结果和匹配源文档类型组成
    """
    require_id.clear()
    provide_id.clear()
    result = []
    # if 'keys' == doc_type:
    #     text = get_datas_from_keys(src)
    #     sort_sims = []
    #     for doc_id, data in enumerate(get_one_from_keys(dest)):
    #         (index, dictionary, lsi) = train_by_plsa(text, topic_num)
    #         # 词袋处理
    #         ml_bow = dictionary.doc2bow(data)
    #         # 在上面选择的模型数据 lsi 中，计算其他数据与其的相似度
    #         ml_lsi = lsi[ml_bow]  # ml_lsi 形式如 (topic_id, topic_value)
    #         sims = index[ml_lsi]  # sims 是最终结果了， index[xxx] 调用内置方法 __getitem__() 来计算ml_lsi
    #
    #         # 排序，为输出方便
    #         sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])
    #         result.append(sort_sims)
    #         logging.warning("第%s篇%s文档匹配结果：%s" % (doc_id, dest, sort_sims))
    #     return tuple(require_id, provide_id,result, src)
    if 'text' == doc_type:
        text = get_datas_from_text(require_id, provide_id, algorithm_config, dest, "plsa",read_file=read_file, match_need=match_need)
        # logging.warning("text : %s" % text)
        # print("text : ", text)
        sort_sims = []
        for doc_id, data in enumerate(get_one_from_text(require_id, provide_id, algorithm_config, src, "plsa",read_file=read_file, match_need=match_need)):
            (index, dictionary, lsi) = train_by_plsa(text, topic_num)
            # 词袋处理
            ml_bow = dictionary.doc2bow(data)
            # 在上面选择的模型数据 lsi 中，计算其他数据与其的相似度
            ml_lsi = lsi[ml_bow]  # ml_lsi 形式如 (topic_id, topic_value)
            sims = index[ml_lsi]  # sims 是最终结果了， index[xxx] 调用内置方法 __getitem__() 来计算ml_lsi

            # 排序，为输出方便
            sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])
            result.append(sort_sims)
            logging.warning("第%s篇%s文档匹配结果：%s" % (doc_id, dest, sort_sims))
        return tuple((require_id, provide_id, result, src))
    else:
        raise ValueError
