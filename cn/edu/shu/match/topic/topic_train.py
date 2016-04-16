import logging
import os
import os.path
import sys
import time
import jieba
import jieba.analyse


module_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir, os.pardir, os.pardir, os.pardir))
sys.path.append(module_path)
for a_path in sys.path:
    if os.path.exists(os.path.join(a_path, 'cn', 'edu', 'shu', 'match')):
        os.chdir(os.path.join(a_path, 'cn', 'edu', 'shu', 'match'))
        break

import cn.edu.shu.match.global_variable as gl
from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.topic.train_lsi_model import MyLsiModel
from cn.edu.shu.match.topic.train_lda_model import MyLdaModel
from cn.edu.shu.match.topic.train_hdp_model import MyHdpModel
from cn.edu.shu.match.topic.preprocess import get_config_json


ms_sql = MsSql()
config_json = get_config_json(gl.config_path)
require_table_json = get_config_json(gl.require_table_path)
provide_table_json = get_config_json(gl.provide_table_path)
jieba.analyse.set_stop_words(config_json['gensim_stopword_path'])
jieba.load_userdict(config_json['gensim_dict_path'])
# jieba.analyse.set_idf_path(config_json['gensim_normalization_tf_idf_path'])
jieba.analyse.set_idf_path(config_json['gensim_tf_idf_path'])


class TopicTrain(object):
    """
    主题模型统一调用接口
    """

    @classmethod
    def update_all(cls):
        """
        更新所有模型
        :return:
        """
        MyLsiModel().re_train_or_update_lsi()
        MyLdaModel().re_train_or_update_lda()
        # MyHdpModel().re_train_or_update_hdp()

    @classmethod
    def re_train_all(cls):
        """
        重新训练所有模型
        :return:
        """
        MyLsiModel().re_train_or_update_lsi(update=False)
        MyLdaModel().re_train_or_update_lda(update=False)
        # MyHdpModel().re_train_or_update_hdp(update=False)


if __name__ == '__main__':
    topic_train = TopicTrain()
    start = time.clock()
    TopicTrain.re_train_all()
    end = time.clock()
    print('lda运行时间：%s' % (end - start))
