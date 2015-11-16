#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cn.edu.shu.match.save import save_to_database
from cn.edu.shu.match.lsi import get_result_from_lsi
from cn.edu.shu.match.lda import get_result_from_lda
from time import strftime, localtime
import logging,json

__author__ = 'jxxia'
"""
   匹配算法
"""

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('log/main_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='w')
# 全局变量，存储需求和服务编号顺序
require_id = []
provide_id = []


def invoke_algorithm(individuation=False):
    if not individuation:
        with open('./config/algorithm.json', encoding='utf-8') as f:
            json_data = json.load(f)
            algorithm_type = json_data['algorithm']
            if json_data['lsi']:
                save_to_database(
                    *get_result_from_lsi(require_id, provide_id, './config/algorithm.json', 'text', src='provide',
                                          dest='require'))
                print(get_result_from_lsi(require_id, provide_id, './config/algorithm.json', 'text', src='provide',
                                           dest='require'))
            elif json_data['lda']:
                logging.debug("test")
                save_to_database(
                    *get_result_from_lda(require_id, provide_id, './config/algorithm.json', 'text', src='provide',
                                         dest='require'))
                logging.debug("test")
            elif json_data['cos']:
                save_to_database(*get_result_from_lsi(require_id, provide_id, 'text', src='provide', dest='require'))
            else:
                raise ValueError


if __name__ == '__main__':
    # log_config = Log_Config()
    # log_config.congif()
    import time

    while True:
        start = time.clock()
        invoke_algorithm()
        print('\a')
        end = time.clock()
        print("程序运行了: %f 秒" % (end - start))
        if end - start < 60:
            time.sleep(60)
        else:
            time.sleep(round((end - start)))
