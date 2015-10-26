__author__ = '祥文'

import os

fileName = input("请输入要创建的完整文件名：")
fileName = fileName.encode('gbk')
try:
    newFile = open(fileName)
except IOError as error:
    print("文件不存在或权限不够",error)
else:
    for line in newFile:
        print(line)

    newFile.close()
