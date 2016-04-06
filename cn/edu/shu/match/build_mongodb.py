#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 10:50:50 2015

@author: 祥文
"""

from time import strftime, localtime
from pymongo import MongoClient
import json
import sys
import logging
import os

# 将路径更改为项目初始路径
module_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir, os.pardir, os.pardir, os.pardir))
sys.path.append(module_path)
for a_path in sys.path:
    if os.path.exists(os.path.join(a_path, 'cn', 'edu', 'shu', 'match')):
        os.chdir(os.path.join(a_path, 'cn', 'edu', 'shu', 'match'))
        break

logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('log/build_mongo_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='a')


class Mongo:
    """
    对pymssql的简单封装
    pymssql库，该库到这里下载：http://www.lfd.uci.edu/~gohlke/pythonlibs/#pymssql
    使用该库时，需要在Sql Server Configuration Manager里面将TCP/IP协议开启

    用法：
    """

    def __init__(self, database_name=None, collection_name=None):
        """
        初始化对象
        :param database_name: 使用MongoDB哪个数据库
        :param collection_name: 使用MongoDB哪个集合
        :return:
        """
        with open('./config/mongodb.json', encoding='utf-8') as mongodb_file:
            mongodb_json = json.load(mongodb_file)
            self._url = mongodb_json['url']  # 连接地址
            if database_name:
                self._database_name = database_name  # 需要连接的数据库名字
            else:
                self._database_name = mongodb_json['default_database']  # 默认使用MongoDB哪个数据库
            if collection_name:
                self._collection_name = collection_name
            else:
                self._collection_name = mongodb_json['default_collection']  # 默认使用MongoDB哪个集合
        # 初始化连接
        self._client = MongoClient(self._url)  # 连接数据库客户端
        self._database = self._client[self._database_name]  # 数据库
        self._collection = self._database[self._collection_name]  # 集合

    def get_collection(self):
        """
        得到连接的集合
        返回: 连接的集合
        :return:连接的集合
        """
        return self._collection

    def set_database(self, database):
        """
        设置数据库
        :param database: 数据库名称
        :return:
        """
        self._database = self._client[database]

    def set_collection(self, collection):
        """
        设置集合
        :param collection: 集合名称
        :return:
        """
        self._collection = self._database[collection]

    def find(self, default=True, *args, **kwargs):
        """
        调用pymongo的find
        :param default: 使用集合的默认配置数据
        :param args:
        :param kwargs:
        :return:
        """
        if default:
            return self._collection.find({'default': True})[0]
        return self._collection.find(*args, **kwargs)

    def find_one(self, filter=None, *args, **kwargs):
        """
        调用pymongo的find_one
        :param filter:
        :param args:
        :param kwargs:
        :return:
        """
        return self._collection.find(*args, **kwargs)[0]

    def insert(self, doc_or_docs, manipulate=True, check_keys=True, continue_on_error=False, **kwargs):
        """
        调用pymongo的insert
        :param doc_or_docs:
        :param manipulate:
        :param check_keys:
        :param continue_on_error:
        :param kwargs:
        :return:
        """
        self._collection.insert(doc_or_docs, manipulate, check_keys, continue_on_error, **kwargs)

    def save(self, to_save, manipulate=True, check_keys=True, **kwargs):
        """
        调用pymongo的save
        :param to_save:
        :param manipulate:
        :param check_keys:
        :param kwargs:
        :return:
        """
        self._collection.save(to_save, manipulate, check_keys, **kwargs)


if __name__ == '__main__':
    # 创建一个数据库对象
    mongo = Mongo()
    print(mongo.get_collection())
    mongo.set_collection('algorithm')
    print(mongo.get_collection())
    try:
        print(mongo.find()['lsi_comment'])
    except KeyError as e:
        print("配置文件中不存在{}字段".format('lsi_comment'))
        sys.exit()
