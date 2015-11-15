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
            if "lsi" == algorithm_type:
                logging.basicConfig(level=logging.INFO,
                                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                                    datefmt='%a, %d %b %Y %H:%M:%S',
                                    filename=('match_lsi_%s.log' % strftime('%Y-%m-%d', localtime())),
                                    filemode='a')
            elif "lda" == algorithm_type:
                logging.basicConfig(level=logging.INFO,
                                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                                    datefmt='%a, %d %b %Y %H:%M:%S',
                                    filename=('match_lda_%s.log' % strftime('%Y-%m-%d', localtime())),
                                    filemode='a')
            elif "cos" == algorithm_type:
                logging.basicConfig(level=logging.INFO,
                                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                                    datefmt='%a, %d %b %Y %H:%M:%S',
                                    filename=('match_cos_%s.log' % strftime('%Y-%m-%d', localtime())),
                                    filemode='a')
            elif "all" == algorithm_type:
                logging.basicConfig(level=logging.INFO,
                                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                                    datefmt='%a, %d %b %Y %H:%M:%S',
                                    filename=('match_all_%s.log' % strftime('%Y-%m-%d', localtime())),
                                    filemode='a')
            else:
                raise ValueError
