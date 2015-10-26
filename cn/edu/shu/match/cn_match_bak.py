# -*- coding: utf-8 -*-

"""
   匹配算法
"""
from build_sql import MsSql
# 为了能看到过程日志
import logging, json
from time import strftime, localtime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('cn_matchPlsi_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='w')
# 全局变量，存储需求和服务编号顺序
require_id = []
provide_id = []
degree = {97: 60, 98: 65, 99: 70, 100: 75}


def pre_process_cn(courses, low_freq_filter=True):
    """
    预处理(easy_install nltk)
    简化的 中文+英文 预处理
        1.去掉停用词
        2.去掉标点符号
        3.处理为词干
        4.去掉低频词

    """
    import nltk
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

    # 去除过低频词
    # if low_freq_filter:
    #     all_stems = sum(texts_stemmed, [])
    #     print("all_stems:",all_stems)
    #     stems_once = set(stem for stem in set(all_stems) if all_stems.count(stem) == 1)
    #     texts = [[stem for stem in text if stem not in stems_once] for text in texts_stemmed]
    # else:
    #     texts = texts_stemmed
    # print("返回的数据为:", texts_stemmed)
    return texts_stemmed


def get_datas_from_text(type, num=10):
    """
    type 取出数据的类型
    num 取出数据的个数
    """
    sql = MsSql()
    if 'require' == type:
        data = sql.exec_search("select * from RequireDocInfor")
        dataIndex = [2, 4, 8, 11, 18]
    elif 'provide' == type:
        data = sql.exec_search("select * from ProvideDocInfor")
        dataIndex = [2, 4, 8, 9, 10, 12, 16, 17, 18, 19, 20, 25]
    else:
        raise ValueError("类型'%s'不存在!" % type)
    return_data = []

    for index, document in enumerate(data):
        # 存储文档序号顺序
        if 'require' == type:
            require_id.append(document[0])
        elif 'provide' == type:
            provide_id.append(document[0])
        else:
            raise ValueError
        text = ""
        # 提取文档匹配所需信息
        for i in dataIndex:
            if document[i]:
                text += document[i] + ","
        logging.warning("第%s篇%s文档文章ID为：%s" % (index, type, document[0]))
        temp_list = []
        temp_list.append(text)
        return_data.append(pre_process_cn(temp_list)[0])
        # print("return_data:" ,return_data)
    return return_data


def get_one_from_text(type):
    """
    type 取出数据的类型
    num 取出数据的个数
    """
    sql = MsSql()
    if 'require' == type:
        data = sql.exec_search("select * from RequireDocInfor")
        dataIndex = [2, 4, 8, 11, 18]
    elif 'provide' == type:
        data = sql.exec_search("select * from ProvideDocInfor")
        dataIndex = [2, 4, 8, 9, 10, 12, 16, 17, 18, 19, 20, 25]
    else:
        raise ValueError
    # logging.info("data : %s" % data)
    for index, document in enumerate(data):
        # 存储文档序号顺序
        if 'require' == type:
            require_id.append(document[0])
        elif 'provide' == type:
            provide_id.append(document[0])
        else:
            raise ValueError
        text = ""
        # 提取文档匹配所需信息
        for i in dataIndex:
            if document[i]:
                text += document[i] + ","
        logging.warning("第%s篇%s文档文章为：%s" % (index, type, document[0]))
        temp_list = []
        temp_list.append(text)
        yield pre_process_cn(temp_list)[0]


def get_datas_from_keys(type, num=10):
    """
    type 取出数据的类型
    num 取出数据的个数
    """
    sql = MsSql()
    if 'require' == type:
        data = sql.exec_search("select * from RequireDocKeyWs")
    elif 'provide' == type:
        data = sql.exec_search("select * from ProvideDocKeyWs")
    else:
        raise ValueError
    return_data = []
    for index, document in enumerate(data):
        # 存储文档序号顺序
        if 'require' == type:
            require_id.append(document[0])
        elif 'provide' == type:
            provide_id.append(document[0])
        else:
            raise ValueError
        document_word = []
        # 提取文档匹配所需信息
        for i in range(2, num * 2, 2):
            document_word.append(document[i])
        logging.warning("第%s篇%s文档词为：%s" % (index, type, document[0]))
        return_data.append(document_word)

    return return_data


def get_one_from_keys(type, num=10):
    """
    type 取出数据的类型
    num 取出数据的个数
    """
    sql = MsSql()
    if 'require' == type:
        data = sql.exec_search("select * from RequireDocKeyWs")
    elif 'provide' == type:
        data = sql.exec_search("select * from ProvideDocKeyWs")
    else:
        raise ValueError
    logging.info("data : %s" % data)
    for index, document in enumerate(data):
        # 存储文档序号顺序
        if 'require' == type:
            require_id.append(document[0])
        elif 'provide' == type:
            provide_id.append(document[0])
        else:
            raise ValueError
        logging.warning("第%s篇%s文档词为：%s" % (index, type, document[0]))
        document_word = []
        # 提取文档匹配所需信息
        for i in range(2, num * 2, 2):
            #  logging.info("i的值为：%d" % i)
            document_word.append(document[i])
        yield document_word


def train_by_lsi(lib_texts, topic_num=9):
    """
        通过LSI模型的训练
    """
    from gensim import corpora, models, similarities
    # print("lib_texts,", lib_texts)
    dictionary = corpora.Dictionary(lib_texts)
    #  logging.info("dictionary: %s" % dictionary)
    corpus = [dictionary.doc2bow(text) for text in
              lib_texts]  # doc2bow(): 将collection words 转为词袋，用两元组(word_id, word_frequency)表示
    #  logging.info("corpus: %s" % corpus)
    tfidf = models.TfidfModel(corpus)
    #  logging.info("tfidf: %s" % tfidf)
    corpus_tfidf = tfidf[corpus]
    #  logging.info("corpus_tfidf: %s" % corpus_tfidf)

    # 拍脑袋的：训练topic数量为10的LSI模型
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=topic_num)
    index = similarities.MatrixSimilarity(lsi[corpus])  # index 是 gensim.similarities.docsim.MatrixSimilarity 实例
    #  logging.info("index: %s" % index)
    return (index, dictionary, lsi)


def train_by_lda(lib_texts, topic_num=9):
    """
        通过LDA模型的训练
    """
    from gensim import corpora, models, similarities

    # 为了能看到过程日志
    # import logging
    # logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    dictionary = corpora.Dictionary(lib_texts)
    #  logging.info("dictionary: %s" % dictionary)
    corpus = [dictionary.doc2bow(text) for text in
              lib_texts]  # doc2bow(): 将collection words 转为词袋，用两元组(word_id, word_frequency)表示
    #  logging.info("corpus: %s" % corpus)
    tfidf = models.TfidfModel(corpus)
    #  logging.info("tfidf: %s" % tfidf)
    corpus_tfidf = tfidf[corpus]
    #  logging.info("corpus_tfidf: %s" % corpus_tfidf)

    # 拍脑袋的：训练topic数量为10的LSI模型
    lda = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=topic_num)
    index = similarities.MatrixSimilarity(lda[corpus])  # index 是 gensim.similarities.docsim.MatrixSimilarity 实例
    #  logging.info("index: %s" % index)
    return (index, dictionary, lda)


def get_result_from_lsi(type='keys', src='require', dest='provide', topic_num=9):
    require_id.clear()
    provide_id.clear()
    result = []
    if 'keys' == type:
        text = get_datas_from_keys(src)
        sort_sims = []
        for doc_id, data in enumerate(get_one_from_keys(dest)):
            (index, dictionary, lsi) = train_by_lsi(text, topic_num)
            # 词袋处理
            ml_bow = dictionary.doc2bow(data)
            # 在上面选择的模型数据 lsi 中，计算其他数据与其的相似度
            ml_lsi = lsi[ml_bow]  # ml_lsi 形式如 (topic_id, topic_value)
            sims = index[ml_lsi]  # sims 是最终结果了， index[xxx] 调用内置方法 __getitem__() 来计算ml_lsi

            # 排序，为输出方便
            sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])
            result.append(sort_sims)
            logging.warning("第%s篇%s文档匹配结果：%s" % (doc_id, dest, sort_sims))
        return (result, src)
    elif 'text' == type:
        text = get_datas_from_text(src)
        # logging.warning("text : %s" % text)
        # print("text : ", text)
        sort_sims = []
        for doc_id, data in enumerate(get_one_from_text(dest)):
            (index, dictionary, lsi) = train_by_lsi(text, topic_num)
            # 词袋处理
            ml_bow = dictionary.doc2bow(data)
            # 在上面选择的模型数据 lsi 中，计算其他数据与其的相似度
            ml_lsi = lsi[ml_bow]  # ml_lsi 形式如 (topic_id, topic_value)
            sims = index[ml_lsi]  # sims 是最终结果了， index[xxx] 调用内置方法 __getitem__() 来计算ml_lsi

            # 排序，为输出方便
            sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])
            result.append(sort_sims)
            logging.warning("第%s篇%s文档匹配结果：%s" % (doc_id, dest, sort_sims))
        return (result, src)
    else:
        raise ValueError


def get_result_from_lda(type='keys', src='require', dest='provide', topic_num=9):
    require_id.clear()
    provide_id.clear()
    result = []
    if 'keys' == type:
        text = get_datas_from_keys(src)
        sort_sims = []
        for doc_id, data in enumerate(get_one_from_keys(dest)):
            (index, dictionary, lda) = train_by_lda(text, topic_num)
            # 词袋处理
            ml_bow = dictionary.doc2bow(data)
            # 在上面选择的模型数据 lsi 中，计算其他数据与其的相似度
            ml_lda = lda[ml_bow]  # ml_lsi 形式如 (topic_id, topic_value)
            sims = index[ml_lda]  # sims 是最终结果了， index[xxx] 调用内置方法 __getitem__() 来计算ml_lsi

            # 排序，为输出方便
            sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])
            result.append(sort_sims)
            logging.warning("第%s篇%s文档匹配结果：%s" % (doc_id, dest, sort_sims))
        return (result, src)
    elif 'text' == type:
        text = get_datas_from_text(src)
        sort_sims = []
        for doc_id, data in enumerate(get_one_from_text(dest)):
            (index, dictionary, lda) = train_by_lda(text, topic_num)
            # 词袋处理
            ml_bow = dictionary.doc2bow(data)
            # 在上面选择的模型数据 lsi 中，计算其他数据与其的相似度
            ml_lda = lda[ml_bow]  # ml_lsi 形式如 (topic_id, topic_value)
            sims = index[ml_lda]  # sims 是最终结果了， index[xxx] 调用内置方法 __getitem__() 来计算ml_lsi

            # 排序，为输出方便
            sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])
            result.append(sort_sims)
            logging.warning("第%s篇%s文档匹配结果：%s" % (doc_id, dest, sort_sims))
        return (result, src)
    else:
        raise ValueError


def save_to_database(result, src):
    from time import strftime, localtime
    sql = MsSql()
    sql.exec_search("select * from DocMatchInfor")
    # print("require_id:",require_id)
    # print("provide_id:",provide_id)
    if 'require' == src:
        for index, data in enumerate(result):
            for doc_id, cosine in data:
                # print("index : %s ,doc_id: %s" %(index,doc_id))
                # 如果余弦距离大于0.97且数据库中此记录不存在，则插入数据库
                if cosine > 0.97:
                    with open('./config/database.json', encoding='utf-8') as f:
                        data = json.load(f)
                        yours = data['yours']
                        print("yours : %s" % yours)
                        if 'ture' != yours:
                            require_data = sql.exec_search(
                                "select RequireDocInfor_UserID from RequireDocInfor where RequireDocInfor_ID = %d" % (
                                    require_id[doc_id]))
                            print("select RequireDocInfor_UserID from RequireDocInfor where RequireDocInfor_ID = %d" % (
                                require_id[doc_id]))
                            if require_data:
                                print("require_data : %s" % require_data)
                                for (RequireDocInfor_UserID) in require_data:
                                    provide_data = sql.exec_search(
                                        "select ProvideDocInfor_UserID from ProvideDocInfor where ProvideDocInfor_ID = %d" % (
                                            provide_id[index]))
                                    if provide_data:
                                        for (ProvideDocInfor_UserID) in provide_data:
                                            if ProvideDocInfor_UserID == RequireDocInfor_UserID:
                                                print("ProvideDocInfor_UserID : %s" % ProvideDocInfor_UserID)
                                                print("RequireDocInfor_UserID : %s" % RequireDocInfor_UserID)
                                                return
                    if not sql.exec_search(
                                    "select * from DocMatchInfor where DocMatchInfor_ReqID = %d and DocMatchInfor_ProID = %d" % (
                                    require_id[doc_id], provide_id[index])):
                        # print("INSERT INTO DocMatchInfor ([DocMatchInfor_ReqID], [DocMatchInfor_ProID], [DocMatchInfor_Degree], [DocMatchInfor_Status], [DocMatchInfor_CreateDate], [DocMatchInfor_ReqRead], [DocMatchInfor_ProRead]) VALUES ('%s', '%s', '%s', '0', '%s', '0', '0')" %(require_id[doc_id], provide_id[index], degree[round(cosine * 100)], strftime('%Y-%m-%d %H:%M:%S', localtime())))
                        sql.exec_non_search(
                            "INSERT INTO DocMatchInfor ([DocMatchInfor_ReqID], [DocMatchInfor_ProID], [DocMatchInfor_Degree], [DocMatchInfor_Status], [DocMatchInfor_CreateDate], [DocMatchInfor_ReqRead], [DocMatchInfor_ProRead]) VALUES ('%s', '%s', '%s', '0', '%s', '0', '0')" % (
                                require_id[doc_id], provide_id[index], degree[round(cosine * 100)],
                                strftime('%Y-%m-%d %H:%M:%S', localtime())))
    elif 'provide' == src:
        for index, data in enumerate(result):
            for doc_id, cosine in data:
                # print("index : %s ,doc_id: %s" %(index,doc_id))
                if cosine > 0.97:
                    with open('./config/database.json', encoding='utf-8') as f:
                        data = json.load(f)
                        yours = data['yours']
                        print("yours : %s" % yours)
                        if 'ture' != yours:
                            require_data = sql.exec_search(
                                "select RequireDocInfor_UserID from RequireDocInfor where RequireDocInfor_ID = %d" % (
                                    require_id[index]))
                            print("select RequireDocInfor_UserID from RequireDocInfor where RequireDocInfor_ID = %d" % (
                                require_id[doc_id]))
                            if require_data:
                                print("require_data : %s" % require_data)
                                for (RequireDocInfor_UserID) in require_data:
                                    provide_data = sql.exec_search(
                                        "select ProvideDocInfor_UserID from ProvideDocInfor where ProvideDocInfor_ID = %d" % (
                                            provide_id[doc_id]))
                                    if provide_data:
                                        for (ProvideDocInfor_UserID) in provide_data:
                                            if ProvideDocInfor_UserID == RequireDocInfor_UserID:
                                                print("ProvideDocInfor_UserID : %s" % ProvideDocInfor_UserID)
                                                print("RequireDocInfor_UserID : %s" % RequireDocInfor_UserID)
                                                return
                    if not sql.exec_search(
                                    "select * from DocMatchInfor where DocMatchInfor_ReqID = %d and DocMatchInfor_ProID = %d" % (
                                    require_id[index], provide_id[doc_id])):
                        sql.exec_non_search(
                            "INSERT INTO DocMatchInfor ([DocMatchInfor_ReqID], [DocMatchInfor_ProID], [DocMatchInfor_Degree], [DocMatchInfor_Status], [DocMatchInfor_CreateDate], [DocMatchInfor_ReqRead], [DocMatchInfor_ProRead]) VALUES ('%s', '%s', '%s', '0', '%s', '0', '0')" % (
                                require_id[index], provide_id[doc_id], degree[round(cosine * 100)],
                                strftime('%Y-%m-%d %H:%M:%S', localtime())))
    else:
        raise ValueError


if __name__ == '__main__':
    # log_config = Log_Config()
    # log_config.congif()
    import time

    while True:
        start = time.clock()
        with open('./config/algorithm.json', encoding='utf-8') as f:
            json_data = json.load(f)
            algorithm_type = json_data['algorithm']
            if "plsi" == algorithm_type:
                save_to_database(*get_result_from_lsi('text', src='provide', dest='require', ))  # 看下前10个最相似的，第一个是基准数据自身
            elif "lda" == algorithm_type:
                save_to_database(*get_result_from_lda('text', src='provide', dest='require', ))  # 看下前10个最相似的，第一个是基准数据自身
            elif "cos" == algorithm_type:
                save_to_database(*get_result_from_lsi('text', src='provide', dest='require', ))  # 看下前10个最相似的，第一个是基准数据自身
            elif "all" == algorithm_type:
                save_to_database(*get_result_from_lsi('text', src='provide', dest='require', ))  # 看下前10个最相似的，第一个是基准数据自身
            else:
                raise ValueError
        end = time.clock()
        print("程序运行了: %f 秒" % (end - start))
        if end - start < 60:
            time.sleep(60)
        else:
            time.sleep(round((end - start)))
