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

from cn.edu.shu.match.build_mongodb import Mongo
from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.topic.train_corpus import MyCorpus
from cn.edu.shu.match.topic.train_tf_idf_model import MyTfIdfModel
from cn.edu.shu.match.topic.train_dictionary import MyDictionary
from cn.edu.shu.match.topic.preprocess import get_config_json
import cn.edu.shu.match.global_variable as gl
from cn.edu.shu.match.process.get_text import product_conclude
from cn.edu.shu.match.read_property import change_json_file

mongo = Mongo()
ms_sql = MsSql()
mongodb_json = get_config_json(gl.mongodb_path)
config_json = get_config_json(gl.config_path)
insert_config_json = get_config_json(gl.insert_config_path)
require_table_json = get_config_json(gl.require_table_path)
provide_table_json = get_config_json(gl.provide_table_path)
jieba.analyse.set_stop_words(config_json['gensim_stopword_path'])
jieba.load_userdict(config_json['gensim_dict_path'])
# jieba.analyse.set_idf_path(config_json['gensim_normalization_tf_idf_path'])
jieba.analyse.set_idf_path(config_json['gensim_tf_idf_path'])


def merge_data(data, data_index):
    """
    通过数据和索引抽取数据
    :param data: 文档id
    :param data_index: 算法配置文件地址
    :return: 预处理后数据
    """
    return_data = list()  # 返回数据
    for document in data:
        text = str()
        # 提取文档匹配所需信息
        for conclude_index, subscript in enumerate(data_index):
            int_sub = int(subscript)
            if document[int_sub]:
                if gl.default_industry_name != document[int_sub]:
                    text += document[int_sub] + ","
        text_list = list()
        text_list.append(text)
        return_data.append(text_list)
    return return_data


def insert_require_vector_to_mongo():
    """
    将需求文档向量插入mongo数据库
    :return:
    """
    dictionary = MyDictionary().get_dictionary()
    # 重新得到语料库
    corpus = MyCorpus()
    if not corpus.re_train_corpus():
        # 语料库不存在
        return None
    tf_idf_model = MyTfIdfModel()
    if corpus.is_update():
        # 语料库有更新，重新得到tf_idf模型
        tf_idf_model.re_train_tf_idf(corpus.get_corpus())
    tf_idf_model = tf_idf_model.get_tf_idf()
    mongo.set_collection(mongodb_json['provide'])
    # 最大需求id序号
    max_require_id = ms_sql.exec_continue_search(
        "SELECT MAX ({}) FROM {} WHERE {} IN {}".format(
            require_table_json['require_id'], require_table_json['require'], require_table_json['require_status'],
            gl.require_normal_status))
    # 利用需求数据
    if int(max_require_id[0][0]) <= insert_config_json['insert_max_require_id_used']:
        return
    # 对需求数据进行分割，防止数据过大导致内存溢出
    id_range_list = (list(range(0, int(max_require_id[0][0]), 100)))
    id_range_list_len = len(id_range_list)
    # logging.warning(id_range_list)
    if 0 != len(id_range_list):
        if 1 == len(id_range_list):
            # 获取语料库
            require_result, require_conclude_data_index = product_conclude(range(0, max_require_id[0][0] + 1),
                                                                           gl.algorithm_config_path,
                                                                           'require')
            for require_data in require_result:
                # 计算一个需求和一个服务的匹配度
                if not require_data:
                    continue
                mongo.insert({"require_id": require_data[0], "default": True, "require_vector": tf_idf_model[
                    dictionary.doc2bow(jieba.cut(merge_data(require_data, require_conclude_data_index)))]})
        else:
            for index in range(id_range_list_len):
                if index + 1 < id_range_list_len:
                    # 获取语料库
                    require_result, require_conclude_data_index = product_conclude(
                        range(id_range_list[index], id_range_list[index + 1] - 1),
                        gl.algorithm_config_path, 'require')
                    for require_data in require_result:
                        if not require_data:
                            continue
                        mongo.insert({"require_id": require_data[0], "default": True, "require_vector": tf_idf_model[
                            dictionary.doc2bow(jieba.cut(merge_data(require_data, require_conclude_data_index)))]})
            require_result, require_conclude_data_index = product_conclude(
                range(id_range_list[-1], int(max_require_id[0][0]) + 1),
                gl.algorithm_config_path, 'require')
            for require_data in require_result:
                if not require_data:
                    continue
                mongo.insert({"require_id": require_data[0], "default": True, "require_vector": tf_idf_model[
                    dictionary.doc2bow(jieba.cut(merge_data(require_data, require_conclude_data_index)))]})
    insert_config_json['insert_max_require_id_used'] = int(max_require_id[0][0])
    change_json_file(gl.insert_config_path, **insert_config_json)


def insert_provide_vector_to_mongo():
    """
    将服务文档向量插入mongo数据库
    :return:
    """
    dictionary = MyDictionary().get_dictionary()
    # 重新得到语料库
    corpus = MyCorpus()
    if not corpus.re_train_corpus():
        # 语料库不存在
        return None
    tf_idf_model = MyTfIdfModel()
    if corpus.is_update():
        # 语料库有更新，重新得到tf_idf模型
        tf_idf_model.re_train_tf_idf(corpus.get_corpus())
    tf_idf_model = tf_idf_model.get_tf_idf()
    mongo.set_collection(mongodb_json['provide'])
    # 最大服务id序号
    max_provide_id = ms_sql.exec_continue_search(
        "SELECT MAX ({}) FROM {} WHERE {} IN {}".format(
            provide_table_json['provide_id'], provide_table_json['provide'], provide_table_json['provide_status'],
            gl.provide_normal_status))
    # 利用需求数据
    print(insert_config_json['insert_max_provide_id_used'])
    if int(max_provide_id[0][0]) <= insert_config_json['insert_max_provide_id_used']:
        return
    # 对服务数据进行分割，防止数据过大导致内存溢出
    id_range_list = (list(range(0, int(max_provide_id[0][0]), 100)))
    id_range_list_len = len(id_range_list)
    print(id_range_list)
    # logging.warning(id_range_list)
    if 0 != len(id_range_list):
        if 1 == len(id_range_list):
            # 获取语料库
            provide_result, provide_conclude_data_index = product_conclude(range(0, max_provide_id[0][0] + 1),
                                                                           gl.algorithm_config_path,
                                                                           'provide')
            for provide_data in provide_result:
                # 计算一个需求和一个服务的匹配度
                if not provide_data:
                    continue
                mongo.insert({"provide_id": provide_data[0], "default": True, "provide_vector": tf_idf_model[
                    dictionary.doc2bow(jieba.cut(merge_data(provide_data, provide_conclude_data_index)))]})
        else:
            for index in range(id_range_list_len):
                if index + 1 < id_range_list_len:
                    # 获取语料库
                    provide_result, provide_conclude_data_index = product_conclude(
                        range(id_range_list[index], id_range_list[index + 1] - 1),
                        gl.algorithm_config_path, 'provide')
                    for provide_data in provide_result:
                        if not provide_data:
                            continue
                        mongo.insert({"provide_id": provide_data[0], "default": True, "provide_vector": tf_idf_model[
                            dictionary.doc2bow(jieba.cut(merge_data(provide_data, provide_conclude_data_index)))]})
            provide_result, provide_conclude_data_index = product_conclude(
                range(id_range_list[-1], int(max_provide_id[0][0]) + 1),
                gl.algorithm_config_path, 'provide')
            for provide_data in provide_result:
                if not provide_data:
                    continue
                mongo.insert({"provide_id": provide_data[0], "default": True, "provide_vector": tf_idf_model[
                    dictionary.doc2bow(jieba.cut(merge_data(provide_data, provide_conclude_data_index)))]})
    insert_config_json['insert_max_provide_id_used'] = int(max_provide_id[0][0])
    change_json_file(gl.insert_config_path, **insert_config_json)


def insert_data():
    """

    :return:
    """
    insert_require_vector_to_mongo()
    insert_provide_vector_to_mongo()


if __name__ == '__main__':
    insert_data()
