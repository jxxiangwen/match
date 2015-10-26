# -*- coding: utf-8 -*-

__author__ = 'jxxiangwen'

import os


def fileExist(filename):
    returnBool = False;
    if os.path.exists(filename):
        returnBool = True
    else:
        message = '对不起，"%s"文件不存在!'
        print (message % filename)

    return returnBool
