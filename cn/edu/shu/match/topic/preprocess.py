import logging
import time
import os
import os.path
import docx2txt
import re
import json
import jieba
import jieba.analyse
import sys

module_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir, os.pardir, os.pardir, os.pardir))
sys.path.append(module_path)
project_path = os.path.join(sys.path[1], 'cn', 'edu', 'shu', 'match')  # 改变项目运行路径
os.chdir(project_path)

from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.read_property import change_json_file

jieba.analyse.set_stop_words("./topic/stopwords.dic")
jieba.load_userdict("./topic/dict1.txt")

ms_sql = MsSql()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('main_%s.log' % time.strftime('%Y-%m-%d', time.localtime())),
                    filemode='a')


def get_config_json():
    """
    得到config.json数据
    :return:
    """
    with open('./topic/config.json', encoding='utf-8') as config_file:
        config_json = json.load(config_file)
        return config_json


def get_dir_path(path):
    """
    得到文件夹地址
    :param path:
    :return:
    """
    if os.path.isdir(path):
        pass
    else:
        path = os.path.join(os.getcwd(), path)
    assert True == os.path.isdir(path), '文件夹路径不正确'
    return path


def get_file_path(path):
    """
    得到文件地址
    :param path: 
    :return: 
    """
    if os.path.isfile(path):
        pass
    else:
        path = os.path.join(os.getcwd(), path)
    print(path)
    assert True == os.path.isfile(path), '文档路径不正确'
    return path


def joint(regular, text):
    """
    根据正则表达式提取文档的需求部分
    :param regular: 正则表达式
    :param text: 需要提取的文本
    :return:
    """
    # 索引0是正则式
    pattern = re.compile(regular[0].strip())
    # 找出文章中所有符合的正则式
    result_list = pattern.findall(text)
    if result_list:
        # 提取需要的内容并去除无用字符，如制表符，换行符
        result_list = [re.sub(r'[\s|\n|\t]', '', result[int(regular[1])]) for result in
                       result_list]
    return result_list


def test_extract_data():
    """
    测试提取是否成功
    :return:
    """
    config_json = get_config_json()
    root_dir = get_dir_path(config_json['doc_path'])
    # dir_names是文件夹，file_names是文件
    for parent, dir_names, file_names in os.walk(root_dir):
        file_names = [os.path.join(parent, file_name) for file_name in file_names]
        # 遍历文件
        for file_name in file_names:
            # 读取文件数据
            text = docx2txt.process(file_name)
            # 读取正则表达式中正则式
            for regulars in config_json['regulars']:
                if not regulars.startswith('#'):
                    regular_list = regulars.split('and')
                    # 对正则式进行分割，提取正则式和需要部分索引
                    regular_list = [a_regular.strip().split('for') for a_regular in
                                    regular_list]
                    result_list = [joint(regular, text) for regular in regular_list]
                    print(len(result_list[0]))
                    print(len(result_list[1]))
                    with open('title.txt', mode='w', encoding='utf-8') as title_file:
                        for index, title in enumerate(result_list[0]):
                            title_file.write(title + '      ' + result_list[1][index])
                            title_file.write('\n')


def extract_train_data():
    """
    正式提取
    :return:
    """
    config_json = get_config_json()
    root_dir = get_dir_path(config_json['doc_path'])
    for parent, dir_names, file_names in os.walk(root_dir):
        file_names = [os.path.join(parent, file_name) for file_name in file_names]
        # 遍历文件
        for file_name in file_names:
            # 读取文件数据
            text = docx2txt.process(file_name)
            # 读取正则表达式中正则式
            for regulars in config_json['regulars']:
                if not regulars.startswith('#'):
                    regular_list = regulars.split('and')
                    # 对正则式进行分割，提取正则式和需要部分索引
                    regular_list = [a_regular.strip().split('for') for a_regular in
                                    regular_list]
                    result_list = [joint(regular, text) for regular in regular_list]
                    print(len(result_list[0]))
                    print(len(result_list[1]))
                    with open('train.txt', mode='a', encoding='utf-8') as title_file:
                        for index, title in enumerate(result_list[0]):
                            title_file.write(title + '，' + result_list[1][index])
                            title_file.write('\n')
                            # with open('content.txt', mode='w', encoding='utf-8') as content_file:
                            #     for index, content in enumerate(result_list[1]):
                            #         content_file.write(str(index) + ':' + content)
                            #         content_file.write('\n')


def update_or_insert_data(data):
    """
    根据数据更新td_idf表
    :param data:
    :return:
    """
    config_json = get_config_json()
    # 最多抽取分词后的10000个词语
    participle_result = jieba.analyse.extract_tags(data, topK=10000)
    for word in participle_result:
        if str.isdigit(word):
            continue
        # 查看数据中是否存在word
        results = ms_sql.exec_continue_search(
            "SELECT {},{},{} FROM {} WHERE {} = '{}'".format(*config_json['idf_corpus_column_name'],
                                                             config_json['idf_corpus_table'],
                                                             config_json['idf_corpus_column_name'][1],
                                                             word))
        if len(results) == 0:
            # 插入数据
            ms_sql.exec_continue_non_search(
                # print(
                "INSERT INTO {} ({},{})VALUE ('{}',{})".format(config_json['idf_corpus_table'],
                                                               config_json['idf_corpus_column_name'][1],
                                                               config_json['idf_corpus_column_name'][2],
                                                               word, 1))
        else:
            # 更新数据
            ms_sql.exec_continue_non_search(
                # print(
                "UPDATE {} SET {} = {} WHERE {} = '{}'".format(config_json['idf_corpus_table'],
                                                               config_json['idf_corpus_column_name'][2],
                                                               results[0][2] + 1,
                                                               config_json['idf_corpus_column_name'][1],
                                                               word))
    return participle_result


def update_tf_idf_by_data(data):
    """
    通过新增数据更新idf表
    :return:
    """
    config_json = get_config_json()
    # 训练文件地址
    train_file_path = get_file_path(config_json['train_path'])
    # 分词后存放地址
    participle_file_path = get_file_path(config_json['participle_path'])
    with open(train_file_path, encoding='utf-8') as train_file:
        with open(participle_file_path, mode='w', encoding='utf-8') as participle_file:
            file_line_num = 0  # 文件行数目，即文件数
            if not data and len(data) != 0:
                file_line_num = 1
                update_or_insert_data(data)
            else:
                # 遍历抽取的数据开始
                for train in train_file:
                    file_line_num += 1
                    participle_result = update_or_insert_data(train)
                    # 写入分词文件
                    participle_file.writelines(' '.join(participle_result) + '\n')
                    # 遍历抽取的数据结束

                # 遍历专利数据开始
                # 最大专利id序号
                max_patent_id_result = ms_sql.exec_continue_search(
                    "SELECT MAX({}) FROM {} ".format(config_json['patent_table_column_name'][0],
                                                     config_json['patent_table']))
                # 上次使用的最大专利号
                assert str.isdigit(config_json['patent_max_id_used']), 'patent_max_id_used必须是整数'
                if max_patent_id_result[0][0] <= int(config_json['patent_max_id_used']):
                    pass
                else:
                    # 新增专利数量
                    new_patent_num_result = ms_sql.exec_continue_search(
                        "SELECT COUNT(*) FROM {} WHERE {} BETWEEN {} AND {} ".format(
                            config_json['patent_table'], config_json['patent_table_column_name'][0],
                            config_json['patent_max_id_used'], max_patent_id_result[0][0]))
                    file_line_num += new_patent_num_result
                    # 得到可用的专利训练数据
                    results = (ms_sql.exec_continue_search(
                        "SELECT {},{},{},{} FROM {} WHERE {} = {}".format(*config_json['patent_table_column_name'],
                                                                          config_json['patent_table'],
                                                                          config_json['patent_table_column_name'][0],
                                                                          patent_id)) for
                               patent_id in range(int(config_json['patent_max_id_used']) + 1,
                                                  max_patent_id_result[0][0] + 1))
                    for result in results:
                        if len(result) != 0:
                            update_or_insert_data(result[0][1] + result[0][2])
                    config_json['patent_max_id_used'] = max_patent_id_result  # 修改使用过的专利数据最大id
                    change_json_file('./topic/config.json', config_json)
                    # 遍历专利数据结束
            # 文档总数
            file_num_result = ms_sql.exec_continue_search(
                "SELECT * FROM {} WHERE {} = '{}'".format(
                    config_json['idf_corpus_table'], config_json['idf_corpus_column_name'][1],
                    config_json['idf_corpus_total_key_name']))
            file_num = file_num_result[0][2]
            # 更新文件总数
            ms_sql.exec_continue_non_search(
                # print(
                "UPDATE {} SET {} = {} WHERE {} = '{}'".format(config_json['idf_corpus_table'],
                                                               config_json['idf_corpus_column_name'][2],
                                                               file_num + file_line_num,
                                                               config_json['idf_corpus_column_name'][1],
                                                               config_json['idf_corpus_total_key_name']))


def produce_tf_idf_file():
    """
    通过训练数据和专利数据产生tf-idf
    :return:
    """
    config_json = get_config_json()
    # 最大id序号，查看tf-idf表最大id
    max_id_result = ms_sql.exec_continue_search(
        "SELECT MAX({}) FROM {} ".format(config_json['idf_corpus_column_name'][0],
                                         config_json['idf_corpus_table']))
    max_id = max_id_result[0][0] + 1
    # 文档总数
    file_num_result = ms_sql.exec_continue_search(
        "SELECT * FROM {} WHERE {} = '{}'".format(
            config_json['idf_corpus_table'], config_json['idf_corpus_column_name'][1],
            config_json['idf_corpus_total_key_name']))
    file_num = file_num_result[0][2]
    # 查看idf数据
    results = (ms_sql.exec_continue_search(
        "SELECT * FROM {} WHERE {} = {}".format(
            config_json['idf_corpus_table'], config_json['idf_corpus_column_name'][0], tdf_id)) for tdf_id in
               range(max_id) if tdf_id != 0)
    import math
    with open('./topic/tf_idf.txt', mode='w', encoding='utf-8') as tf_idf_file:
        for result in results:
            if len(result) != 0:
                tf_idf_file.writelines(
                    str(result[0][1]).strip() + ' ' + str(math.log(file_num / result[0][2])).strip() + '\n')


def normalization_tf_idf():
    """
    对tf_idf进行归一化
    :return:
    """
    tf_idf_list = list()
    with open('./topic/tf_idf.txt', encoding='utf-8') as tf_idf_file:
        with open('./topic/normalization_tf_idf.txt', mode='w', encoding='utf-8') as normalization_tf_idf_file:
            for tf_idf in tf_idf_file:
                tf_idf_list.append(tf_idf.strip().split(' '))
            tf_idf_list = sorted(tf_idf_list, key=lambda a_tf_idf: float(a_tf_idf[1]))
            for tf_idf in tf_idf_list:
                normalization_tf_idf_file.writelines(
                    str(tf_idf[0]).strip() + ' ' + str(float(tf_idf[1]) / float(tf_idf_list[-1][1])).strip() + '\n')


if __name__ == '__main__':
    # produce_tf_idf_file()
    # ms_sql.close_conn()
    # normalization_tf_idf()
    pass
