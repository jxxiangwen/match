#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'jxxia'

import logging
from time import strftime, localtime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('log/preprocess_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='a')


def pre_process_cn(courses, low_freq_filter=False):
    """
    预处理(easy_install nltk)
    简化的 中文+英文 预处理
        1.去掉停用词
        2.去掉标点符号
        3.处理为词干
        4.去掉低频词

    """
    import jieba.analyse
    from nltk.tokenize import word_tokenize

    texts_tokenized = []
    # print("courses : %s" % courses)
    for document in courses:
        # print("document : %s" % document)
        texts_tokenized_tmp = []
        for word in word_tokenize(document):
            # logging.warning("word : " + word)
            texts_tokenized_tmp += jieba.analyse.extract_tags(word, 10)
            # print("jieba.analyse.extract_tags(word) : %s" % jieba.analyse.extract_tags(word))
        # print("texts_tokenized_tmp:",texts_tokenized_tmp)
        texts_tokenized.append(texts_tokenized_tmp)

    texts_filtered_stopwords = texts_tokenized
    # print("texts_filtered_stopwords:",texts_filtered_stopwords)

    # 去除标点符号
    english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']
    texts_filtered = [[word for word in document if not word in english_punctuations] for document in
                      texts_filtered_stopwords]

    # 词干化
    from nltk.stem.lancaster import LancasterStemmer
    st = LancasterStemmer()
    texts_stemmed = [[st.stem(word) for word in docment] for docment in texts_filtered]
    logging.debug("预处理后的数据为:", texts_stemmed)

    # 去除过低频词
    if low_freq_filter:
        all_stems = sum(texts_stemmed, [])
        logging.debug("all_stems:", all_stems)
        stems_once = set(stem for stem in set(all_stems) if all_stems.count(stem) == 1)
        return [[stem for stem in text if stem not in stems_once] for text in texts_stemmed]
    else:
        return texts_stemmed
