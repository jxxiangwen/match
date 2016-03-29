#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 10:50:50 2015

@author: 祥文
"""

from collections import namedtuple
from time import strftime, localtime
import pymssql, json, logging, datetime

logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=('log/build_sql_%s.log' % strftime('%Y-%m-%d', localtime())),
                    filemode='a')


class MsSql:
    """
    对pymssql的简单封装
    pymssql库，该库到这里下载：http://www.lfd.uci.edu/~gohlke/pythonlibs/#pymssql
    使用该库时，需要在Sql Server Configuration Manager里面将TCP/IP协议开启

    用法：
    """

    def __init__(self):
        with open('./config/database.json', encoding='utf-8') as database_file:
            database_json = json.load(database_file)
            self.host = database_json['host']
            self.user = database_json['user']
            self.password = database_json['password']
            self.database = database_json['database']
            if not self.database:
                raise (NameError, "没有设置数据库信息")
            self.conn = pymssql.connect(host=self.host, user=self.user, password=self.password, database=self.database,
                                        port=25366, charset="utf8")

    def __get_connect(self):
        """
        得到连接信息
        返回: conn.cursor()
        :return:
        """
        self.conn = pymssql.connect(host=self.host, user=self.user, password=self.password, database=self.database,
                                    port=25366, charset="utf8")
        cursor = self.conn.cursor()
        if not cursor:
            raise (NameError, "连接数据库失败")
        else:
            return cursor

    def exec_search(self, sql):
        """
        执行查询语句
        返回的是一个包含tuple的list，list的元素是记录行，tuple的元素是每行记录的字段

        调用示例：
                ms = MSSQL(host="localhost",user="sa",password="123456",database="PythonWeiboStatistics")
                resList = ms.exec_search("SELECT id,NickName FROM WeiBoUser")
                for (id,NickName) in resList:
                    print str(id),NickName
        :param sql: 查询语句sql代码
        :return:
        """
        cursor = self.__get_connect()
        cursor.execute(sql)
        res_list = cursor.fetchall()

        # 查询完毕后必须关闭连接
        self.conn.close()
        return res_list

    def exec_non_search(self, sql):
        """
        执行非查询语句

        调用示例：
            cur = self.__get_connect()
            cur.execute(sql)
            self.conn.commit()
            self.conn.close()
        :param sql: 非查询语句sql代码
        :return:
        """
        cursor = self.__get_connect()
        cursor.execute(sql)
        self.conn.commit()
        self.conn.close()

    def exec_continue_search(self, sql):
        """
        执行持续查询语句
        需要手动关闭连接
        返回的是一个包含tuple的list，list的元素是记录行，tuple的元素是每行记录的字段

        调用示例：
                ms = MSSQL(host="localhost",user="sa",password="123456",database="PythonWeiboStatistics")
                resList = ms.exec_search("SELECT id,NickName FROM WeiBoUser")
                for (id,NickName) in resList:
                    print str(id),NickName
        :param sql: 查询语句sql代码
        :return:
        """
        cursor = self.__get_connect()
        # print(cursor)
        cursor.execute(sql)
        res_list = cursor.fetchall()
        return res_list

    def exec_continue_non_search(self, sql):
        """
        执行持续非查询语句
        需要手动关闭连接
        调用示例：
            cur = self.__get_connect()
            cur.execute(sql)
            self.conn.commit()
            self.conn.close()
        :param sql: 非查询语句sql代码
        :return:
        """
        cursor = self.__get_connect()
        cursor.execute(sql)
        self.conn.commit()

    def close_conn(self):
        """
        关闭连接
        :return:
        """
        self.conn.close()

    def get_cursor(self):
        """
        得到cursor
        :return:
        """
        return self.__get_connect()


if __name__ == '__main__':
    # 创建一个数据库对象
    sql = MsSql()
    match_comment_structure = list()
    with open('./config/match_comment_table.json', encoding='utf-8') as match_comment_file:
        match_comment_json = json.load(match_comment_file)
        match_comment_structure = match_comment_json['match_comment_structure']
    DocMatchInfoComment = namedtuple('DocMatchInfoComment', match_comment_structure)
    str = "select * from DocMatchInfoComment where match_id  in (select DocMatchInfor_ID from DocMatchInfor where Algorithm_Type like '%lsi%') and create_time between '{}' and '{}'".format(
        str(datetime.datetime.now() - datetime.timedelta(days=10))[0:-3], str(datetime.datetime.now())[0:-3])
    # str = "select * from DocMatchInfoComment WHERE create_time < '{}'".format(str(datetime.datetime.now())[0:-3])
    print(str)
    results = sql.exec_search(str)
    # "select * from DocMatchInfoComment WHERE create_time < {}".format(str(datetime.datetime.now())[0:-3]))
    # results = sql.exec_search("select * from DocMatchInfoComment")
    # data = (4,'require', datetime.datetime.now(),2,'good',82)
    # results = sql.exec_search("INSERT INTO DocMatchInfoComment VALUES(%d, %s, %s,%d,%s,%d)" % data)
    print("result{}".format(results))
    for result in results:
        print("result{}".format(result))
        match = DocMatchInfoComment(*result)
        print("match_id{}".format(match.match_id))
        # 取出所有记录，返回的是一个包含tuple的list，list的元素是记录行，tuple的元素是每行记录的字段
        # for result in results:
        # print("time:{},UserInfor_Name:{1}".format(str(user_infor[0]), user_infor[2]))
