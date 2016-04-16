import logging
from time import strftime, localtime
import os
import sys
import time

module_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir, os.pardir, os.pardir, os.pardir))
sys.path.append(module_path)
for a_path in sys.path:
    if os.path.exists(os.path.join(a_path, 'cn', 'edu', 'shu', 'match')):
        os.chdir(os.path.join(a_path, 'cn', 'edu', 'shu', 'match'))
        break

import cn.edu.shu.match.global_variable as gl
from cn.edu.shu.match.build_mongodb import Mongo
from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.topic.preprocess import get_config_json
from cn.edu.shu.match.match_algorithm import MatchAlgorithm
from cn.edu.shu.match.topic.topic_train import TopicTrain
from cn.edu.shu.match.topic.train_corpus import MyCorpus
from cn.edu.shu.match.topic.train_tf_idf_model import MyTfIdfModel
from cn.edu.shu.match.topic.train_dictionary import MyDictionary
from cn.edu.shu.match.topic.train_lda_model import MyLdaModel
from cn.edu.shu.match.topic.insert_document_to_mongo import insert_data
from cn.edu.shu.match.topic.topic_match import TopicUtils

mongo = Mongo()
ms_sql = MsSql()
config_json = get_config_json(gl.config_path)
mongodb_json = get_config_json(gl.mongodb_path)
algorithm_json = get_config_json(gl.algorithm_config_path)
require_table_json = get_config_json(gl.require_table_path)
provide_table_json = get_config_json(gl.provide_table_path)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('log/build_sql_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='a')


def insert_into_match(require_id, provide_id, match_degree, algorithm_type):
    """
    向数据库插入匹配结果
    :param require_id:
    :param provide_id:
    :param match_degree:
    :param algorithm_type:
    :return:
    """
    mongo.set_collection(mongodb_json['require'])
    require_vector = mongo.get_collection().find_one({"require_id": require_id})
    mongo.set_collection(mongodb_json['provide'])
    provide_vector = mongo.get_collection().find_one({"provide_id": provide_id})
    if TopicUtils.get_cos_value(require_vector['require_vector'],
                                provide_vector['provide_vector']) > gl.cos_match_threshold:
        MatchAlgorithm.save(require_id, provide_id, match_degree, algorithm_type)


def produce_match_document(update=True):
    """
    产生匹配的需求和服务
    :param update: 
    :return: 
    """
    logging.warning("开始进行匹配计算")
    topic_train = TopicTrain()
    if update:
        topic_train.update_all()
    else:
        topic_train.re_train_all()
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
    insert_data()
    lda_model = MyLdaModel().get_lda()
    if not lda_model:
        return None
    topic_utils = TopicUtils()
    # 最大需求id序号
    max_require_id = ms_sql.exec_continue_search(
        "SELECT MAX ({}) FROM {} WHERE {} IN {}".format(
            require_table_json['require_id'], require_table_json['require'], require_table_json['require_status'],
            gl.require_normal_status))
    # 对需求数据进行分割，防止数据过大导致内存溢出
    id_range_list = (list(range(0, int(max_require_id[0][0]), 100)))
    id_range_list_len = len(id_range_list)
    if 0 != len(id_range_list):
        if 1 == len(id_range_list):
            for require_id in range(0, max_require_id[0][0] + 1):
                provide_dict = topic_utils.get_match_provide_by_require(lda_model, tf_idf_model, dictionary, require_id)
                for provide_id, match_degree in provide_dict.items():
                    insert_into_match(require_id, provide_id, match_degree, 'topic')
        else:
            for index in range(id_range_list_len):
                if index + 1 < id_range_list_len:
                    for require_id in range(id_range_list[index], id_range_list[index + 1] - 1):
                        provide_dict = topic_utils.get_match_provide_by_require(lda_model, tf_idf_model, dictionary,
                                                                                require_id)
                        for provide_id, match_degree in provide_dict.items():
                            insert_into_match(require_id, provide_id, match_degree, 'topic')

            for require_id in range(id_range_list[-1], int(max_require_id[0][0]) + 1):
                provide_dict = topic_utils.get_match_provide_by_require(lda_model, tf_idf_model, dictionary, require_id)
                for provide_id, match_degree in provide_dict.items():
                    insert_into_match(require_id, provide_id, match_degree, 'topic')
    logging.warning("结束匹配计算")


if __name__ == '__main__':
    times = 1
    while True:
        start = time.clock()
        # 每10次重新训练一次
        if times % 10 == 0:
            produce_match_document(update=False)
        else:
            produce_match_document()
        end = time.clock()
        print("程序运行了: %f 秒" % (end - start))
        logging.warning("程序运行了: %f 秒" % (end - start))
        sleep_time = config_json['time_to_run'] * 3600 * 24 - int(end - start)
        if sleep_time > 0:
            time.sleep(sleep_time)
