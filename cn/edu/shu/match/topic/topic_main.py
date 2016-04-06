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

from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.topic.preprocess import get_config_json
from cn.edu.shu.match.match_algorithm import MatchAlgorithm
from cn.edu.shu.match.topic.topic_train import TopicTrain
from cn.edu.shu.match.topic.topic_match import TopicUtils
import cn.edu.shu.match.global_variable as gl

ms_sql = MsSql()
config_json = get_config_json(gl.config_path)
algorithm_json = get_config_json(gl.algorithm_config_path)
require_table_json = get_config_json(gl.require_table_path)
provide_table_json = get_config_json(gl.provide_table_path)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('log/build_sql_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='a')


def produce_match_document():
    """
    产生匹配的需求和服务
    :return:
    """
    topic_train = TopicTrain()
    topic_train.update_all()
    dictionary = topic_train.get_dictionary()
    tf_idf_model = topic_train.get_tf_idf()
    lda_model = topic_train.get_lda()
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
                    MatchAlgorithm.save(require_id, provide_id, match_degree, '')
        else:
            for index in range(id_range_list_len):
                if index + 1 < id_range_list_len:
                    for require_id in range(id_range_list[index], id_range_list[index + 1] - 1):
                        provide_dict = topic_utils.get_match_provide_by_require(lda_model, tf_idf_model, dictionary,
                                                                                require_id)
                        for provide_id, match_degree in provide_dict.items():
                            MatchAlgorithm.save(require_id, provide_id, match_degree, '')

            for require_id in range(id_range_list[-1], int(max_require_id[0][0]) + 1):
                provide_dict = topic_utils.get_match_provide_by_require(lda_model, tf_idf_model, dictionary, require_id)
                for provide_id, match_degree in provide_dict.items():
                    MatchAlgorithm.save(require_id, provide_id, match_degree, '')


if __name__ == '__main__':
    # import jieba
    # topic_train = TopicTrain()
    # topic_utils = TopicUtils()
    # dictionary = topic_train.get_dictionary()
    # lda_model = topic_train.get_lda()
    # tf_idf_model = topic_train.get_tf_idf()
    # print('tf_idf_model:', tf_idf_model)
    # print(lda_model[dictionary.doc2bow(jieba.cut('太赫兹人体安检仪技术能级升级难题攻克'))])
    # topic_utils.get_match_provide_by_require(lda_model, tf_idf_model, dictionary, 131)
    while True:
        start = time.clock()
        produce_match_document()
        end = time.clock()
        print("程序运行了: %f 秒" % (end - start))
        sleep_time = 3600 * 24 - int(end - start)
        if sleep_time > 0:
            time.sleep(sleep_time)
