import numpy as np
import re
import jieba
import jieba.analyse
import logging
import os
import sys
from time import strftime, localtime

module_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir, os.pardir, os.pardir, os.pardir))
sys.path.append(module_path)
for a_path in sys.path:
    if os.path.exists(os.path.join(a_path, 'cn', 'edu', 'shu', 'match')):
        os.chdir(os.path.join(a_path, 'cn', 'edu', 'shu', 'match'))
        break

from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.topic.preprocess import get_config_json
from cn.edu.shu.match.process.get_text import product_conclude
import cn.edu.shu.match.global_variable as gl
from cn.edu.shu.match.tool import str_list_to_dict

ms_sql = MsSql()
# lda_model = TopicTrain
config_json = get_config_json(gl.config_path)
lda_config_json = get_config_json(gl.lda_config_path)
algorithm_json = get_config_json(gl.algorithm_config_path)
require_table_json = get_config_json(gl.require_table_path)
provide_table_json = get_config_json(gl.provide_table_path)

logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('log/preprocess_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='a')


def add_list_round(sentence):
    """

    :param sentence:
    :return:
    """
    init_list = list()
    init_list.append(sentence)
    return init_list


class TopicUtils(object):
    @classmethod
    def make_len_equal(cls, sentence_x, sentence_y):
        """
        扩充两个句子使得两句子向量长度相等以便可以进行余弦运算
        :param sentence_x:句子x
        :param sentence_y:句子y
        :return:长度相等的两个句子向量
        """
        # 对句子向量按照词序号排序
        # logging.warning('排序前sentence_x:{},sentence_y:{}'.format(sentence_x, sentence_y))
        if 2 == len(sentence_x) and isinstance(sentence_x, tuple):
            sentence_x = add_list_round(sentence_x)
        if 2 == len(sentence_y) and isinstance(sentence_y, tuple):
            sentence_y = add_list_round(sentence_y)
        # logging.warning('排序后sentence_x:{},sentence_y:{}'.format(sentence_x, sentence_y))
        sentence_x = sorted(sentence_x, key=lambda item: item[0])
        sentence_y = sorted(sentence_y, key=lambda item: item[0])
        word_ids = set()
        # 两个for循环得到两句子出现的所有词号
        for word in sentence_x:
            word_ids.add(word[0])
        for word in sentence_y:
            word_ids.add(word[0])
        # 转为list可以通过词号得到索引号
        word_ids = list(word_ids)
        # 初始化两个全为0且长度相等的列表用于存放扩容后句子向量
        new_sentence_x = [0 for i in range(len(word_ids))]
        new_sentence_y = [0 for i in range(len(word_ids))]
        # 将词出现的次数赋值到新向量中
        for word in sentence_x:
            new_sentence_x[word_ids.index(word[0])] += word[1]
        for word in sentence_y:
            new_sentence_y[word_ids.index(word[0])] += word[1]
        return (new_sentence_x, new_sentence_y)

    @classmethod
    def get_cos_value(cls, vector_x, vector_y):
        """
        得到余弦距离
        :param vector_x:向量x
        :param vector_y:向量y
        :return:余弦相似度
        """
        if not vector_x or not vector_y:
            return 0
        if 0 == len(vector_x) or 0 == len(vector_y):
            return 0
        vector_x, vector_y = TopicUtils.make_len_equal(vector_x, vector_y)
        array_x = np.array(vector_x)  # 将列表转化为数组，更好的数学理解是向量
        array_y = np.array(vector_y)  # 将列表转化为数组，更好的数学理解是向量
        sum_x_y = np.sum(array_x * array_y)  # cos(a,b)=a*b/(|a|+|b|)
        len_x = np.sqrt(sum(array_x * array_x))
        len_y = np.sqrt(sum(array_y * array_y))
        return sum_x_y / (float(len_x * len_y))

    @classmethod
    def get_euclidean_metric_value(cls, vector_x, vector_y):
        """
        得到欧氏距离
        :param vector_x:向量x
        :param vector_y:向量y
        :return:欧氏距离
        """
        if 0 == len(vector_x) or 0 == len(vector_y):
            return 0
        vector_x, vector_y = TopicUtils.make_len_equal(vector_x, vector_y)
        array_x = np.array(vector_x)  # 将列表转化为数组，更好的数学理解是向量
        array_y = np.array(vector_y)  # 将列表转化为数组，更好的数学理解是向量
        diff_array = array_x - array_y
        return 1 / (1 + np.sqrt(sum(diff_array * diff_array)))

    @classmethod
    def calculate_sim_table(cls, topic_datas, distance_value):
        """
        计算主题模型概率向量相邻向量之间的距离
        :param topic_datas:主题模型概率向量
        :param distance_value: 距离函数
        :return:相邻向量之间的距离列表
        """
        sim_table = list()
        for i in range(len(topic_datas) - 1):
            sim_table.append(distance_value(topic_datas[i], topic_datas[i + 1]))
        return sim_table

    @classmethod
    def calculate_diff(cls, vectors):
        """
        计算相邻向量之间的差值
        :param vectors: 向量
        :return:邻向量之间的差值
        """
        diff_table = list()
        for i in range(len(vectors) - 1):
            diff_table.append(vectors[i + 1] - vectors[i])
        return diff_table

    @classmethod
    def calculate_between(cls, value, lower, upper):
        """
        判断value是否在lower和upper之间
        :param value:值
        :param lower:上限
        :param upper:下限
        :return:是否在阈值之间
        """
        if upper:
            return not (lower <= value <= upper)
        else:
            return not value <= lower

    @classmethod
    def combine_string(cls, datas, begin_index, length):
        """
        拼接字符串
        :param datas: 原始数据
        :param begin_index: 起始位置
        :param length: 拼接长度
        :return: 拼接后字符串
        """
        if 1 == length:
            return datas[begin_index]
        s = str()
        for index in range(length):
            s += datas[begin_index + index] + ','
        return s

    @classmethod
    def segment_by_threshold(cls, datas, sim_table, lower, upper=None):
        """
        通过阈值分割数据
        :param datas:原始数据
        :param lower:分割下限
        :param upper:分割上限
        :return:分割后数据
        """
        if len(datas) != len(sim_table) + 1:
            raise ValueError('数据长度必须必距离长度大1')
        return_list = list()
        begin_index = 0
        length = 1
        for index, sim in enumerate(sim_table):
            # 同一分段，继续
            if TopicUtils.calculate_between(sim, lower, upper):
                length += 1
                continue
            # 不同分段，拼接
            else:
                return_list.append(TopicUtils.combine_string(datas, begin_index, length))
                begin_index = begin_index + length
                length = 1
        return_list.append(TopicUtils.combine_string(datas, begin_index, length))
        return return_list

    @classmethod
    def segment_data_by_cos_threshold(cls, topic_datas, datas):
        """
        通过余弦相似度分割数据
        :param topic_datas:主题模型下概率向量
        :param datas:原始数据
        :return:分割后数据
        """
        # 得到相邻两个主题概率向量之间距离值
        sim_table = TopicUtils.calculate_sim_table(topic_datas, TopicUtils.get_cos_value)
        # sim_table = calculate_sim_table(topic_datas, TopicUtils.get_euclidean_metric_value)
        return TopicUtils.segment_by_threshold(datas, sim_table, gl.cos_segment_threshold)

    @classmethod
    def segment_data_by_dynamic_constant(cls, topic_datas, datas):
        """
        通过动态常数法分割数据
        :param topic_datas:主题模型下概率向量
        :param datas:原始数据
        :return:分割后数据
        """
        # 得到相邻两个主题概率向量之间距离值
        sim_table = TopicUtils.calculate_sim_table(topic_datas, TopicUtils.get_cos_value)
        # sim_table = calculate_sim_table(topic_datas, TopicUtils.get_euclidean_metric_value)
        if 2 == len(sim_table):
            TopicUtils.segment_data_by_cos_threshold(topic_datas, datas)
        # 分割阈值上限
        avg_sim = sum(sim_table) / len(sim_table)
        diff_table = TopicUtils.calculate_diff(sim_table)
        # 分割阈值下限
        avgm_sim = sum(diff_table) / len(diff_table)
        return TopicUtils.segment_by_threshold(datas, sim_table, avgm_sim, avg_sim)

    # @classmethod
    # def segment_data_by_local_minimum(cls, topic_datas, datas):
    #     """
    #     通过局部最小值法分割数据
    #     :param topic_datas:主题模型下概率向量
    #     :param datas:原始数据
    #     :return:分割后数据
    #     """
    #     # 得到相邻两个主题概率向量之间距离值
    #     sim_table = TopicUtils.calculate_sim_table(topic_datas, TopicUtils.get_cos_value)
    #     # sim_table = calculate_sim_table(topic_datas, TopicUtils.get_euclidean_metric_value)

    @classmethod
    def get_merge_topic_data(cls, lda_model, tf_idf_model, dictionary, datas, merge=True):
        """
        根据语句前后关联程度合并语句并返回主题模型概率向量
        :param lda_model:主题模型
        :param tf_idf_model:tf_idf_model模型
        :param dictionary:词典
        :param datas:原始数据
        :param merge:是否合并
        :return:
        """
        # logging.warning(type(datas))
        if not (isinstance(datas, list) or isinstance(datas, str)):
            raise TypeError('只能合并列表类型或字符串')
        # import collections
        # 如果不需要合并或者数据长度为1，直接返回将数据转为主题概率返回
        # lda_model = lda_model.get_lda()
        # dictionary = lda_model.get_dictionary()
        # # 利用文章更新词典
        # dictionary.add_documents([jieba.cut(data) for data in datas if 0 != len(data)])
        # logging.warning(datas)
        if not merge or 1 == len(datas):
            if isinstance(datas, str):
                return tf_idf_model[dictionary.doc2bow(jieba.cut(datas))]
            else:
                return tf_idf_model[dictionary.doc2bow(jieba.cut(datas[0]))]

        # 对列表每一个句子进行处理
        topic_data = list()
        for data in datas:
            # logging.warning(data)
            # 把句子中词转化为词典中的id
            word_id_data = dictionary.doc2bow(jieba.cut(data))
            topic_vector = lda_model.get_document_topics(word_id_data, minimum_probability=gl.minimum_probability)
            topic_data.append(topic_vector)

        # 返回经过分割的主题模型概率数据
        return_data = list()
        segment_result = TopicUtils.segment_data_by_cos_threshold(topic_data, datas)
        for data in segment_result:
            return_data.append(
                lda_model.get_document_topics(dictionary.doc2bow(jieba.cut(data)),
                                              minimum_probability=gl.minimum_probability))
        return return_data
        # return_data.append(TopicUtils.segment_data_by_dynamic_constant(topic_data, datas))
        # return_data.append(TopicUtils.segment_data_by_local_minimum(topic_data, datas))

    @classmethod
    def get_match_degree(cls, lda_model, tf_idf_model, dictionary, require_data, provide_data, match_degree_function,
                         segment=True):
        """
        计算需求某一段和服务某一段匹配度
        :param lda_model:主题模型
        :param tf_idf_model:tf_idf_model模型
        :param dictionary:词典
        :param require_data:需求数据
        :param provide_data:服务数据
        :param match_degree_function:匹配度函数
        :param segment:是否分割
        :return:某一段匹配度
        """
        if segment:
            if not (isinstance(require_data, str) and isinstance(provide_data, str)):
                return 0
            require_merge_data = TopicUtils.get_merge_topic_data(lda_model, tf_idf_model, dictionary,
                                                                 re.split(gl.split_symbol, require_data))
            provide_merge_data = TopicUtils.get_merge_topic_data(lda_model, tf_idf_model, dictionary,
                                                                 re.split(gl.split_symbol, provide_data))
        else:
            if not require_data or not provide_data:
                return 0
            return match_degree_function(tf_idf_model[dictionary.doc2bow(jieba.cut(require_data))],
                                         tf_idf_model[dictionary.doc2bow(jieba.cut(provide_data))])
            # require_merge_data = TopicUtils.get_merge_topic_data(lda_model, dictionary, require_data, False)
            # provide_merge_data = TopicUtils.get_merge_topic_data(lda_model, dictionary, provide_data, False)
        # logging.warning('分割后需求数据：{}'.format(require_merge_data))
        # logging.warning('分割后服务数据：{}'.format(provide_merge_data))
        # 如果主题模型返回为空或者返回长度等于主题数量，直接使用余弦相似度计算
        if len(require_merge_data) in (0, lda_config_json['lda_model_num_topics']) or \
                        len(provide_merge_data) in (0, lda_config_json['lda_model_num_topics']):
            return match_degree_function(tf_idf_model[dictionary.doc2bow(jieba.cut(require_data))],
                                         tf_idf_model[dictionary.doc2bow(jieba.cut(provide_data))])
        else:
            degree_result = list()
            # if not segment:
            #     return match_degree_function(require_data, provide_data)
            # else:
            logging.warning('分割后需求数据：{}'.format(require_merge_data))
            logging.warning('分割后服务数据：{}'.format(provide_merge_data))
            for require in require_merge_data:
                match_degree_list = list()
                for provide in provide_merge_data:
                    match_degree_list.append(match_degree_function(require, provide))
                degree_result.append(match_degree_list)
            degree_matrix = np.matrix(degree_result)
            # logging.warning('匹配度矩阵为：{}'.format(degree_matrix))
            # 如果返回行是以需求为主，返回列是以服务为主
            # 返回矩阵每一行的最大值作为匹配数据
            # return sum(degree_matrix.max(1).tolist()[0]) / len(require_data)
            # 返回矩阵每一行的最小值作为匹配数据
            # return sum(degree_matrix.min(0).tolist()[0]) / len(require_data)
            # #返回矩阵每一列的最小值作为匹配数据
            # return sum(degree_matrix.min(0).tolist()[0]) / len(provide_data)
            # 返回矩阵每一列的最大值作为匹配数据
            # logging.warning('provide_data:{}'.format(provide_data))
            logging.warning('某一段最大匹配结果：{}'.format(degree_matrix.max(0).tolist()[0]))
            return sum(degree_matrix.max(0).tolist()[0]) / len(degree_matrix.max(0).tolist()[0])

    @classmethod
    def calculate_match_degree(cls, lda_model, tf_idf_model, dictionary, require_data, require_conclude, provide_data,
                               provide_conclude,
                               weight_dict):
        """
        计算需求文档和服务文档的匹配度
        2-需求名,4-行业类别,8-难题概述,11-主要技术指标,18-需求描述
        服务：2,4,8,9,12,16,17,18,20,25
        2-服务名,4-行业类别,8-概述解决该难题技术的方法,9-解决过类似项目的经验,12-完成技术指标,16-所获得的相关专利,17-技术储备,18-拟采取的研究方法,19-主要实现的技术指标,20-项目进度计划,25-服务描述",
        :param lda_model: 主题模型
        :param tf_idf_model: tf_idf_model模型
        :param dictionary: 词典
        :param require_data: 需求数据
        :param require_conclude: 需求内容所在索引号
        :param provide_data: 服务数据
        :param provide_conclude: 服务内容所在索引号
        :param weight_dict: 需求权重数据
        :return:一个需求和一个服务的匹配度
        """
        # logging.warning("开始计算一篇文档")
        # 计算权重和
        weight_sum = 0
        logging.warning('weight_dict:{}'.format(weight_dict))
        for value in weight_dict.values():
            weight_sum += float(value)
        logging.warning('weight_sum:{}'.format(weight_sum))
        result_list = list()
        # 对需求的每一部分计算其和服务的每一部分的匹配度，取最好匹配或最差匹配
        for require_index in require_conclude:
            if not str.isdigit(require_index):
                raise TypeError('需求表索引必须是整数')
            int_require_index = int(require_index)
            match_degree_list = list()
            for provide_index in provide_conclude:
                if not str.isdigit(provide_index):
                    raise TypeError('服务表索引必须是整数')
                int_provide_index = int(provide_index)
                logging.warning('匹配需求数据：{}'.format(require_data[int_require_index]))
                logging.warning('匹配服务数据：{}'.format(provide_data[int_provide_index]))
                if int_require_index in gl.require_no_segment or int_provide_index in gl.provide_no_segment:
                    degree = TopicUtils.get_match_degree(lda_model, tf_idf_model, dictionary,
                                                         require_data[int_require_index],
                                                         provide_data[int_provide_index],
                                                         TopicUtils.get_cos_value, False) * float(
                        weight_dict[require_index])
                    logging.warning(
                        'require_index:{},provide_index:{},匹配度:{}'.format(require_index, provide_index, degree))
                    match_degree_list.append(degree)
                    logging.warning('match_degree_list:{}，'.format(match_degree_list))
                else:
                    degree = TopicUtils.get_match_degree(lda_model, tf_idf_model, dictionary,
                                                         require_data[int_require_index],
                                                         provide_data[int_provide_index],
                                                         TopicUtils.get_cos_value) * float(weight_dict[require_index])
                    logging.warning(
                        'require_index:{},provide_index:{},匹配度:{}'.format(require_index, provide_index, degree))
                    match_degree_list.append(degree)
                    logging.warning('match_degree_list:{}，'.format(match_degree_list))
            logging.warning('需求索引{}，匹配结果:{}'.format(require_index, match_degree_list))
            result_list.append(match_degree_list)
        result_matrix = np.matrix(result_list)
        logging.warning('最大值结果:{}'.format(result_matrix.max(1).tolist()))
        # 如果返回行是以需求为主，返回列是以服务为主
        # 返回矩阵每一行的最大值作为匹配数据
        result = 0
        degree_max_list = result_matrix.max(1).tolist()
        # 返回矩阵每一行的最小值作为匹配数据
        # degree_max_list = result_matrix.min(1).tolist()
        # #返回矩阵每一列的最大值作为匹配数据
        # degree_max_list = result_matrix.max(0).tolist()
        # # 返回矩阵每一列的最小值作为匹配数据
        # degree_max_list = result_matrix.min(0).tolist()
        for degree in degree_max_list:
            result += degree[0]
        return result / weight_sum

    @classmethod
    def get_match_id_by_dict(cls, match_dict):
        """
        返回符合要求的匹配度字典
        :param match_dict:
        :return:
        """
        total_degree = 0.0
        length = 0
        # 将大于最小动态阈值的匹配度相加
        for match_degree in match_dict.values():
            if match_degree > gl.dynamic_match_min_threshold:
                total_degree += match_degree
                length += 1
        if 0 == length:
            return {}
        # 求得平均匹配度
        avg_match_degree = total_degree / length
        match_ids = list()
        # 得到大于平均匹配度且大于最小匹配度的服务号
        for provide_id, match_degree in match_dict.items():
            if match_degree < avg_match_degree or match_degree < gl.match_threshold:
                match_dict.pop(provide_id)
        return match_dict

    @classmethod
    def get_match_provide_by_require(cls, lda_model, tf_idf_model, dictionary, require_id):
        """
        通过需求找到匹配的服务
        需求：2,4,8,11,18
        2-需求名,4-行业类别,8-难题概述,11-主要技术指标,18-需求描述
        服务：2,4,8,9,12,16,17,18,20,25
        2-服务名,4-行业类别,8-概述解决该难题技术的方法,9-解决过类似项目的经验,12-完成技术指标,16-所获得的相关专利,17-技术储备,18-拟采取的研究方法,19-主要实现的技术指标,20-项目进度计划,25-服务描述",
        :param lda_model: 主题模型
        :param tf_idf_model: tf_idf_model模型
        :param dictionary: 词典
        :param require_id: 需要查找的需求id
        :return:与需求相匹配的服务列表
        """
        # logging.warning("进入匹配")
        match_provide_dict = dict()
        require_data, require_conclude_data_index = product_conclude(require_id, gl.algorithm_config_path, 'require')
        # 需求数据不存在或状态不符合要求
        if not require_data or 0 == len(require_data):
            return dict()
        # 读取算法配置
        # 获得需求表匹配时字段索引
        weight = algorithm_json['{}_weight'.format('require')].strip().split(',')
        weight_dict = str_list_to_dict(weight)
        # provide_data, provide_conclude_data_index = product_conclude(169, gl.algorithm_config_path, 'provide')
        # match_provide_dict[provide_data[0][0]] = TopicUtils.calculate_match_degree(lda_model, tf_idf_model, dictionary,
        #                                                                            require_data[0],
        #                                                                            require_conclude_data_index,
        #                                                                            provide_data[0],
        #                                                                            provide_conclude_data_index,
        #                                                                            weight_dict)
        # 最大服务id序号
        max_provide_id = ms_sql.exec_continue_search(
            "SELECT MAX ({}) FROM {} WHERE {} IN {}".format(
                provide_table_json['provide_id'], provide_table_json['provide'], provide_table_json['provide_status'],
                gl.provide_normal_status))
        # 对服务数据进行分割，防止数据过大导致内存溢出
        id_range_list = (list(range(0, int(max_provide_id[0][0]), 100)))
        id_range_list_len = len(id_range_list)
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
                    match_provide_dict[provide_data[0]] = TopicUtils.calculate_match_degree(lda_model, tf_idf_model,
                                                                                            dictionary,
                                                                                            require_data[0],
                                                                                            require_conclude_data_index,
                                                                                            provide_data,
                                                                                            provide_conclude_data_index,
                                                                                            weight_dict)

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
                            # 计算一个需求和一个服务的匹配度
                            match_provide_dict[provide_data[0]] = TopicUtils.calculate_match_degree(lda_model,
                                                                                                    tf_idf_model,
                                                                                                    dictionary,
                                                                                                    require_data[0],
                                                                                                    require_conclude_data_index,
                                                                                                    provide_data,
                                                                                                    provide_conclude_data_index,
                                                                                                    weight_dict)
                provide_result, provide_conclude_data_index = product_conclude(
                    range(id_range_list[-1], int(max_provide_id[0][0]) + 1),
                    gl.algorithm_config_path, 'provide')
                for provide_data in provide_result:
                    if not provide_data:
                        continue
                    # 计算一个需求和一个服务的匹配度
                    match_provide_dict[provide_data[0]] = TopicUtils.calculate_match_degree(lda_model, tf_idf_model,
                                                                                            dictionary,
                                                                                            require_data[0],
                                                                                            require_conclude_data_index,
                                                                                            provide_data,
                                                                                            provide_conclude_data_index,
                                                                                            weight_dict)
        logging.warning(match_provide_dict)
        ms_sql.close_conn()
        return TopicUtils.get_match_id_by_dict(match_provide_dict)


if __name__ == '__main__':
    # logging.warning(TopicUtils.make_len_equal([(0, 0.0003703703703703729)],[(0, 0.00083333333333333024)]))
    pass
