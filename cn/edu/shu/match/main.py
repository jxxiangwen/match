#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.match_algorithm_factory import MatchAlgorithmFactory
from cn.edu.shu.match.get_comment import GetComment
import time, json, logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('log/main_%s.log' % time.strftime('%Y-%m-%d', time.localtime())),
                    filemode='a')

__author__ = 'jxxia'

if __name__ == '__main__':
    while True:
        start = time.clock()
        ms_sql = MsSql()
        require_str = "select RequireDocInfor_ID from RequireDocInfor"
        provide_str = "select ProvideDocInfor_ID from ProvideDocInfor"
        results = ms_sql.exec_search(require_str)
        # 得到需求id
        require_id = [result[0] for result in results]
        results = ms_sql.exec_search(provide_str)
        # 得到服务id
        provide_id = [result[0] for result in results]
        match_algorithm_factory = MatchAlgorithmFactory()
        with open('./config/algorithm.json', encoding='utf-8') as algorithm_file:
            algorithm_json = json.load(algorithm_file)
            if algorithm_json['lsi'] or algorithm_json['lda'] or algorithm_json['cos']:
                if algorithm_json['lsi']:
                    # lsi算法
                    match_algorithm = match_algorithm_factory.create_match_algorithm('lsi', 'all', require_id, provide_id)
                    lsi_result = match_algorithm.get_result(True)
                    lsi_get_comment = GetComment('lsi')
                    lsi_get_comment.init_record()
                    lsi_get_comment.do_better()
                if algorithm_json['lda']:
                    # lda算法
                    match_algorithm = match_algorithm_factory.create_match_algorithm('lda', 'all', require_id, provide_id)
                    lda_result = match_algorithm.get_result(True)
                    lda_get_comment = GetComment('lda')
                    lda_get_comment.init_record()
                    lda_get_comment.do_better()
                if algorithm_json['cos']:
                    # cos算法
                    match_algorithm = match_algorithm_factory.create_match_algorithm('cos', 'all', require_id, provide_id)
                    cos_result = match_algorithm.get_result(True)
                    cos_get_comment = GetComment('cos')
                    cos_get_comment.init_record()
                    cos_get_comment.do_better()
            else:
                raise ValueError("至少需要选择一个算法")
        end = time.clock()
        print('lsi运算结果{}'.format(lsi_result))
        print('lda运算结果{}'.format(lda_result))
        print("程序运行了: %f 秒" % (end - start))

