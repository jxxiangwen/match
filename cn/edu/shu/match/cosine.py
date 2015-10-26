#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'jxxia'

import logging
from time import strftime, localtime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('log/cosine_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='a')