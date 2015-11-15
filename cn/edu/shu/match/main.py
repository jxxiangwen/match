#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cn.edu.shu.match.lsi_algorithm import LsiMatchAlgorithm
from cn.edu.shu.match.lda_algorithm import LdaMatchAlgorithm

__author__ = 'jxxia'

if __name__ == '__main__':
    import time

    start = time.clock()
    match_algorithm = LsiMatchAlgorithm()
    # print(match_algorithm.get_result(re_train=True, num_topics=5))  # 重新训练
    print(match_algorithm.get_result(False))  # 不重新训练
    # match_algorithm = LdaMatchAlgorithm()
    # print(match_algorithm.get_result(re_train=True, num_topics=5))  # 重新训练
    # print(match_algorithm.get_result(False))  # 不重新训练
    end = time.clock()
    print("程序运行了: %f 秒" % (end - start))
