from time import strftime, localtime
from pymongo import MongoClient
import json
import sys
import logging
import os

from cn.edu.shu.match.build_mongodb import Mongo
from cn.edu.shu.match.topic.preprocess import get_config_json
import cn.edu.shu.match.global_variable as gl
from cn.edu.shu.match.build_sql import MsSql
from cn.edu.shu.match.process.get_text import get_data_from_text

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
                    filename=('log/insert_document_to_mongo_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='a')

mongo = Mongo()
mongodb_json = get_config_json(gl.mongodb_path)
require_table_json = get_config_json(gl.require_table_path)
provide_table_json = get_config_json(gl.provide_table_path)


def insert_require_vector_to_mongo(require_doc_id):
    """
    将需求文档向量插入mongo数据库
    :param require_doc_id:
    :return:
    """
    mongo.set_collection(mongodb_json['require'])


def insert_provide_vector_to_mongo(provide_doc_id):
    """
    将服务文档向量插入mongo数据库
    :param provide_doc_id:
    :return:
    """
    mongo.set_collection(mongodb_json['provide'])
