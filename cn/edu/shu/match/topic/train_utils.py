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

import cn.edu.shu.match.global_variable as gl
from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.topic.preprocess import get_config_json
from cn.edu.shu.match.read_property import change_json_file

ms_sql = MsSql()
config_json = get_config_json(gl.config_path)
require_table_json = get_config_json(gl.require_table_path)
provide_table_json = get_config_json(gl.provide_table_path)
jieba.analyse.set_stop_words(config_json['gensim_stopword_path'])
jieba.load_userdict(config_json['gensim_dict_path'])
# jieba.analyse.set_idf_path(config_json['gensim_normalization_tf_idf_path'])
jieba.analyse.set_idf_path(config_json['gensim_tf_idf_path'])


class Utils(object):
    """
    主题模型训练工具方法类
    """

    @classmethod
    def add_list_round(cls, sentence):
        """

        :param sentence:
        :return:
        """
        init_list = list()
        if isinstance(sentence, str):
            init_list.append(list(jieba.cut(sentence)))
        elif isinstance(sentence, list):
            init_list.append(sentence)
        else:
            raise TypeError('只支持str和list类型，不支持%d类型' % (type(sentence)))
        return init_list

    @classmethod
    def yield_document(cls, texts, add_list=True, participle=False):
        """
        对数据进行预处理
        :param texts:文章
        :param add_list:是否用列表包围数据列表
        :param participle:是否分词
        :return:
        """
        import collections
        if isinstance(texts, str):
            if add_list:
                return Utils.add_list_round(texts)
            elif participle:
                return jieba.cut(texts)
            else:
                return texts
        elif isinstance(texts, collections.Iterable):
            for text in texts:
                if text and 0 != len(text):
                    if add_list:
                        if isinstance(text, list):
                            return text
                        else:
                            return Utils.add_list_round(text)
                    elif participle:
                        if isinstance(text, list):
                            return jieba.cut(text[0])
                        else:
                            return jieba.cut(text)
                    else:
                        if isinstance(text, list):
                            return text[0]
                        else:
                            return text
        else:
            raise TypeError('只支持str和list类型，不支持%d类型' % (type(texts)))

    @classmethod
    def return_result(cls, start, end):
        """
        根据开始和结束返回结果
        :param start:
        :param end:
        :return:
        """
        return (ms_sql.exec_continue_search(
            "SELECT {},{},{},{} FROM {} WHERE {} BETWEEN {} AND {}".format(*config_json['patent_table_column_name'],
                                                                           config_json['patent_table'],
                                                                           config_json['patent_table_column_name'][0],
                                                                           start, end)))

    @classmethod
    def update_train_file_used_config(cls, config_path, prefix):
        """

        :param config_path: 文件路径
        :param prefix: 前缀
        :return:
        """
        modify_config_json = get_config_json(config_path)
        if not modify_config_json:
            raise ValueError("配置文件不存在：{}".format(config_path))
        if not prefix:
            raise ValueError("前缀不存在")
        modify_config_json['{}_train_used'.format(prefix)] = True
        # 最大需求id序号
        max_require_id = ms_sql.exec_continue_search(
            "SELECT MAX ({}) FROM {} WHERE {} IN {}".format(
                require_table_json['require_id'], require_table_json['require'],
                require_table_json['require_status'],
                gl.require_normal_status))
        modify_config_json['{}_max_require_id_used'.format(prefix)] = max_require_id[0][0]
        # 最大服务id序号
        max_provide_id = ms_sql.exec_continue_search(
            "SELECT MAX ({}) FROM {} WHERE {} IN {}".format(
                provide_table_json['provide_id'], provide_table_json['provide'],
                provide_table_json['provide_status'],
                gl.provide_normal_status))
        modify_config_json['{}_max_provide_id_used'.format(prefix)] = max_provide_id[0][0]
        # 最大专利id序号
        max_patent_id_result = ms_sql.exec_continue_search(
            "SELECT MAX({}) FROM {} ".format(config_json['patent_table_column_name'][0],
                                             config_json['patent_table']))
        modify_config_json['{}_max_patent_id_used'.format(prefix)] = max_patent_id_result[0][0]
        change_json_file(config_path, **modify_config_json)
