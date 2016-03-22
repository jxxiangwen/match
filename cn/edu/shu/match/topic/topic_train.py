import time
import os
import os.path
import json
import jieba
import jieba.analyse
import sys
from gensim import corpora, models

module_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir, os.pardir, os.pardir, os.pardir))
sys.path.append(module_path)
project_path = os.path.join(sys.path[1], 'cn', 'edu', 'shu', 'match')  # 改变项目运行路径
os.chdir(project_path)
jieba.analyse.set_stop_words("./topic/stopwords.dic")
jieba.load_userdict("./topic/dict.txt")
# jieba.analyse.set_idf_path("./topic/normalization_tf_idf.txt")
jieba.analyse.set_idf_path("./topic/tf_idf.txt")
from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.topic.preprocess import get_config_json

ms_sql = MsSql()


class TopicTrain(object):
    def __init__(self):
        pass

    def re_train(self):
        """
        重新训练主题模型
        :return:
        """
        config_json = get_config_json()
        # 最大专利id序号
        max_patent_id_result = ms_sql.exec_continue_search(
            "SELECT MAX({}) FROM {} ".format(config_json['patent_table_column_name'][0],
                                             config_json['patent_table']))
        # 得到可用的专利训练数据
        results = (ms_sql.exec_continue_search(
            "SELECT {},{},{},{} FROM {} WHERE {} = {}".format(*config_json['patent_table_column_name'],
                                                              config_json['patent_table'],
                                                              config_json['patent_table_column_name'][0],
                                                              patent_id)) for
                   patent_id in range(max_patent_id_result[0][0] + 1))
        train_list = list()
        # 利用专利数据
        for result in results:
            if len(result) != 0:
                train_list.append(jieba.analyse.extract_tags(result[0][1] + result[0][2], topK=10000, withWeight=1))
        # 关闭数据库连接
        ms_sql.close_conn()
        # 利用训练数据
        with open('./topic/train.txt', encoding='utf-8') as train_file:
            for line in train_file:
                train_list.append(jieba.analyse.extract_tags(line, topK=10000, withWeight=1))

            word_list = [[word[0] for word in documents] for documents in train_list]
            tf_idf_list = [[word[1] for word in documents] for documents in train_list]
            # tf_idf_list = (word(1) for word in train_list)
            # dictionary = corpora.Dictionary(word_list)
            # # 保存
            # dictionary.save('./topic/dictionary.dict')
            # corpus = [dictionary.doc2bow(text) for text in word_list]

        def add_dictionary(self, texts):
            """

            :param text:
            :return:
            """
            dictionary = corpora.Dictionary.load('./topic/dictionary.dict')

            if isinstance(texts, str):
                dictionary.add_documents(jieba.analyse.extract_tags(texts, topK=10000))
            elif isinstance(texts, list):
                for text in texts:
                    dictionary.add_documents(jieba.analyse.extract_tags(text, topK=10000))
            else:
                raise TypeError('只支持str和list类型，不支持%d类型' % (type(texts)))
            dictionary.save('./topic/dictionary.dict')

        def get_tf_idf(self, paragraph):
            pass


if __name__ == '__main__':
    topic_train = TopicTrain()
    topic_train.re_train()
