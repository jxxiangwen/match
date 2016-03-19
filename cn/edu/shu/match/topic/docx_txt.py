import os
import os.path
import docx2txt
import re

# 训练语料所在文件夹
root_dir = os.getcwd() + '\企业技术需求'
print(root_dir)
for parent, dir_names, file_names in os.walk(root_dir):
    # case 1:
    for dir_name in dir_names:
        print("parent folder is:" + parent)
        print("dirname is:" + dir_name)
    # case 2
    for file_name in file_names:  # 遍历文件
        text = docx2txt.process(file_name)  # 读取文件数据
        with open(file_name, mode='r', encoding='utf-8') as regular_file:  # 读取正则表达式
            for regular in regular_file:
                pattern = re.compile(regular)
                match = pattern.match(text)
                print(match.group())
