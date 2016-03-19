#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os

module_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir, os.pardir, os.pardir))
sys.path.append(module_path)

from cn.edu.shu.match.change_doc_status import change_require_status, change_provide_status
from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.match_algorithm_factory import MatchAlgorithmFactory
from cn.edu.shu.match.match_algorithm import MatchAlgorithm
from cn.edu.shu.match.get_comment import GetComment
import numpy as np
import time, json, logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('log/main_%s.log' % time.strftime('%Y-%m-%d', time.localtime())),
                    filemode='a')

__author__ = 'jxxia'

if __name__ == '__main__':
    # lsa算法获得更好权重
    lsi_get_comment = GetComment('lsi')
    lsi_get_comment.init_record()
    # lda算法获得更好权重
    lda_get_comment = GetComment('lda')
    lda_get_comment.init_record()
    # cos算法获得更好权重
    cos_get_comment = GetComment('cos')
    cos_get_comment.init_record()
    while True:
        change_require_status()  # 更新需求状态
        change_provide_status()  # 更新服务状态
        algorithm_type_list = list()
        algorithm_type = str()
        start = time.clock()
        ms_sql = MsSql()
        require_str = "select RequireDocInfor_ID from RequireDocInfor"
        provide_str = "select ProvideDocInfor_ID from ProvideDocInfor"
        results = ms_sql.exec_search(require_str)
        # 得到需求id
        require_ids = [result[0] for result in results]
        results = ms_sql.exec_search(provide_str)
        # 得到服务id
        provide_ids = [result[0] for result in results]
        match_algorithm_factory = MatchAlgorithmFactory()
        ones_matrix = np.ones((len(require_ids), len(provide_ids)))
        lsi_result, lda_result, cos_result = (None, None, None)
        with open('./config/algorithm.json', encoding='utf-8') as algorithm_file:
            algorithm_json = json.load(algorithm_file)
            lsi_threshold = algorithm_json['lsi_threshold']#lsi算法阈值
            lda_threshold = algorithm_json['lda_threshold']#lda算法阈值
            # cos_threshold = algorithm_json['cos_threshold']#cos算法阈值
            min_threshold = min(lsi_threshold, lda_threshold)#算法最小阈值
            bool_result = None  # 存储布尔型结果矩阵
            if algorithm_json['lsi'] or algorithm_json['lda'] or algorithm_json['cos']:#至少有一个算法成立
                if algorithm_json['lsi']:
                    algorithm_type_list.append('lsi')
                    # lsi算法
                    match_algorithm = match_algorithm_factory.create_match_algorithm('lsi', 'all', require_ids,
                                                                                     provide_ids)
                    while isinstance(lsi_result, type(None)):
                        lsi_result = match_algorithm.get_result(True)
                    bool_result = lsi_result > lsi_threshold
                    # 获得更好权重
                    lsi_get_comment.do_better()
                    # print('lsi运算结果{}'.format(lsi_result))
                if algorithm_json['lda']:
                    algorithm_type_list.append('lda')
                    # lda算法
                    match_algorithm = match_algorithm_factory.create_match_algorithm('lda', 'all', require_ids,
                                                                                     provide_ids)
                    while isinstance(lda_result, type(None)):
                        lda_result = match_algorithm.get_result(True)
                    bool_result &= lda_result > lda_threshold
                    lda_get_comment.do_better()
                    # print('lda运算结果{}'.format(lda_result))
                    # if algorithm_json['cos']:
                    #     algorithm_type_list.append('cos')
                    #     # cos算法
                    #     match_algorithm = match_algorithm_factory.create_match_algorithm('cos', 'all', require_ids,
                    #                                                                      provide_ids)
                    #     cos_result = match_algorithm.get_result(True)
                    #     # bool_result &= cos_result > cos_threshold
                    #     cos_get_comment.do_better()
            else:
                raise ValueError("至少需要选择一个算法")
        algorithm_type = ','.join(algorithm_type_list)
        lsi_result = ones_matrix if isinstance(lsi_result, type(None)) else lsi_result
        lda_result = ones_matrix if isinstance(lda_result, type(None)) else lda_result
        cos_result = ones_matrix if isinstance(cos_result, type(None)) else cos_result
        MatchAlgorithm.save_to_database(require_ids, provide_ids, algorithm_type, min_threshold,
                                        *(lsi_result, lda_result, cos_result))
        end = time.clock()
        print("程序运行了: %f 秒" % (end - start))
        sleep_time = 3600 * 24 - int(end - start)
        if sleep_time > 0:
            time.sleep(sleep_time)
