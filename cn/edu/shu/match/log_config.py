#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, logging
from time import strftime, localtime

__author__ = 'jxxia'


class Log_Config:
    def congif(self):
        with open('algorithm.json', encoding='utf-8') as f:
            json_data = json.load(f)
            algorithm_type = json_data['algorithm']
            if "plsa" == algorithm_type:
                logging.basicConfig(level=logging.INFO,
                                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                                    datefmt='%a, %d %b %Y %H:%M:%S',
                                    filename=('cn_matchPlsa_%s.log' % strftime('%Y-%m-%d', localtime())),
                                    filemode='a')
            elif "lda" == algorithm_type:
                logging.basicConfig(level=logging.INFO,
                                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                                    datefmt='%a, %d %b %Y %H:%M:%S',
                                    filename=('cn_matchLda_%s.log' % strftime('%Y-%m-%d', localtime())),
                                    filemode='a')
            elif "cos" == algorithm_type:
                logging.basicConfig(level=logging.INFO,
                                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                                    datefmt='%a, %d %b %Y %H:%M:%S',
                                    filename=('cn_matchCos_%s.log' % strftime('%Y-%m-%d', localtime())),
                                    filemode='a')
            elif "all" == algorithm_type:
                logging.basicConfig(level=logging.INFO,
                                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                                    datefmt='%a, %d %b %Y %H:%M:%S',
                                    filename=('cn_matchAll_%s.log' % strftime('%Y-%m-%d', localtime())),
                                    filemode='a')
            else:
                raise ValueError
