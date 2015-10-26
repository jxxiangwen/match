__author__ = '祥文'

import os

fileName = input("请输入要创建的完整文件名：")

while True:
    if os.path.exists(fileName):
        fileName = input("文件已存在，请重新输入：")
    else:
        break

content = []
while True:
    temp = input("请输入要填入的信息：")
    if temp == '.':
        break
    else:
        content.append(temp)

newFile = open(fileName,'w')

newFile.writelines(content)
newFile.close()
