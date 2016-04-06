import os
import os.path
import jieba
import jieba.analyse
import sys
import logging

module_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir, os.pardir, os.pardir, os.pardir))
sys.path.append(module_path)
for a_path in sys.path:
    if os.path.exists(os.path.join(a_path, 'cn', 'edu', 'shu', 'match')):
        os.chdir(os.path.join(a_path, 'cn', 'edu', 'shu', 'match'))
        break

from time import strftime, localtime
from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.topic.preprocess import get_config_json
from cn.edu.shu.match.process.get_text import get_data_from_text
import cn.edu.shu.match.global_variable as gl

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('./log/get_corpus_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='a')

ms_sql = MsSql()
config_json = get_config_json(gl.config_path)
require_table_json = get_config_json(gl.require_table_path)
provide_table_json = get_config_json(gl.provide_table_path)
jieba.analyse.set_stop_words(config_json['gensim_stopword_path'])
jieba.load_userdict(config_json['gensim_dict_path'])
jieba.analyse.set_idf_path(config_json['gensim_tf_idf_path'])


class Document(object):
    def __init__(self, train_file=True, begin_require_id=0, begin_provide_id=0, begin_patent_id=0):
        """
        初始化语料库信息
        :param train_file: 是否使用抽取的需求数据，即train.txt文件
        :param begin_require_id: 初始需求id，结束id为最大需求id
        :param begin_provide_id: 初始服务id，结束id为最大服务id
        :param begin_patent_id: 初始专利id，结束id为最大专利id
        :return: None
        """
        self.train_file = train_file
        self.begin_require_id = begin_require_id
        self.begin_provide_id = begin_provide_id
        self.begin_patent_id = begin_patent_id

    @classmethod
    def return_result(cls, start, end):
        """
        根据开始和结束返回结果
        :param start:初始专利id
        :param end:结束专利id
        :return:查询专利信息的迭代器
        """
        return (ms_sql.exec_continue_search(
            "SELECT {},{},{},{} FROM {} WHERE {} BETWEEN {} AND {}".format(*config_json['patent_table_column_name'],
                                                                           config_json['patent_table'],
                                                                           config_json['patent_table_column_name'][0],
                                                                           start, end)))

    def get_train_document(self):
        """
        得到train.txt文件内容
        :return:
        """
        # 利用需求文件训练数据
        if not self.train_file:
            logging.info("获取train.txt内容")
            with open(config_json['train_path'], encoding='utf-8') as train_file:
                for train in train_file:
                    if 0 != len(train):
                        yield train

    def get_require_document(self):
        """
        得到数据库中需求文件
        :return:
        """
        # 利用需求数据
        # 最大需求id序号
        max_require_id = ms_sql.exec_continue_search(
            "SELECT MAX ({}) FROM {} WHERE {} IN {}".format(
                require_table_json['require_id'], require_table_json['require'], require_table_json['require_status'],
                gl.require_normal_status))
        # 对需求数据进行分割，防止数据过大导致内存溢出
        id_range_list = (list(range(self.begin_require_id, int(max_require_id[0][0]), 100)))
        id_range_list_len = len(id_range_list)
        if 0 != len(id_range_list):
            logging.info("获取数据库中需求文件")
            if 1 == len(id_range_list):
                # 获取语料库
                require_result = get_data_from_text(range(self.begin_require_id, max_require_id[0][0] + 1),
                                                    gl.algorithm_config_path, 'require')
                for require in require_result:
                    if 0 != len(require[0]):
                        yield require[0]
            else:
                for index in range(id_range_list_len):
                    if index + 1 < id_range_list_len:
                        # 获取语料库
                        require_result = get_data_from_text(range(id_range_list[index], id_range_list[index + 1] - 1),
                                                            gl.algorithm_config_path, 'require')
                        for require in require_result:
                            if 0 != len(require[0]):
                                yield require[0]
                require_result = get_data_from_text(range(id_range_list[-1], int(max_require_id[0][0]) + 1),
                                                    gl.algorithm_config_path, 'require')
                for require in require_result:
                    if 0 != len(require[0]):
                        yield require[0]

    def get_provide_document(self):
        """
        得到数据库中服务文件
        :return:
        """
        # 利用服务数据
        # 最大服务id序号
        max_provide_id = ms_sql.exec_continue_search(
            "SELECT MAX ({}) FROM {} WHERE {} IN {}".format(
                provide_table_json['provide_id'], provide_table_json['provide'], provide_table_json['provide_status'],
                gl.provide_normal_status))
        # 对服务数据进行分割，防止数据过大导致内存溢出
        id_range_list = (list(range(self.begin_provide_id, int(max_provide_id[0][0]), 100)))
        id_range_list_len = len(id_range_list)
        if 0 != len(id_range_list):
            logging.info("获取数据库中服务文件")
            if 1 == len(id_range_list):
                # 获取语料库
                provide_result = get_data_from_text(range(self.begin_provide_id, max_provide_id[0][0] + 1),
                                                    gl.algorithm_config_path, 'provide')
                for provide in provide_result:
                    if 0 != len(provide[0]):
                        yield provide[0]
            else:
                for index in range(id_range_list_len):
                    if index + 1 < id_range_list_len:
                        # 获取语料库
                        provide_result = get_data_from_text(range(id_range_list[index], id_range_list[index + 1] - 1),
                                                            gl.algorithm_config_path, 'provide')
                        for provide in provide_result:
                            if 0 != len(provide[0]):
                                yield provide[0]
                provide_result = get_data_from_text(range(id_range_list[-1], int(max_provide_id[0][0]) + 1),
                                                    gl.algorithm_config_path, 'provide')
                for provide in provide_result:
                    if 0 != len(provide[0]):
                        yield provide[0]

    def get_patent_document(self):
        """
        得到数据库中专利文件
        :return:
        """
        # 利用专利数据
        # 最大专利id序号
        max_patent_id_result = ms_sql.exec_continue_search(
            "SELECT MAX({}) FROM {} ".format(config_json['patent_table_column_name'][0],
                                             config_json['patent_table']))
        # 对专利数据进行分割，防止数据过大导致内存溢出
        id_range_list = (list(range(self.begin_patent_id, int(max_patent_id_result[0][0]),
                                    10000)))
        id_range_list_len = len(id_range_list)
        if 0 != len(id_range_list):
            logging.info("获取数据库中专利文件")
            if 1 == len(id_range_list):
                for result in Document.return_result(self.begin_patent_id, int(max_patent_id_result[0][0])):
                    if 0 != len(result):
                        yield result[1] + result[2]
            else:
                for index in range(id_range_list_len):
                    if index + 1 < id_range_list_len:
                        for text in Document.return_result(id_range_list[index], id_range_list[index + 1] - 1):
                            if 0 != len(text):
                                yield text[1] + text[2]
                for text in Document.return_result(id_range_list[-1], int(max_patent_id_result[0][0])):
                    if 0 != len(text):
                        yield text[1] + text[2]

    def __iter__(self):
        """
        迭代器，每迭代一次返回一篇文章数据
        :return:
        """
        for documents in (self.get_train_document(), self.get_require_document(), self.get_provide_document(),
                          self.get_patent_document()):
            for a_document in documents:
                yield a_document


if __name__ == '__main__':
    pass
