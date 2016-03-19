import os
import os.path
import docx2txt
import re


def joint(regular, text):
    pattern = re.compile(regular[0].strip())  # 索引0是正则式
    result_list = pattern.findall(text)  # 找出文章中所有符合的正则式
    if result_list:
        result_list = [re.sub(r'[\s|\n|\t]', '', result[int(regular[1])]) for result in
                       result_list]  # 提取需要的内容并去除无用字符，如制表符，换行符
    return result_list

def test_data():
    # 训练语料所在文件夹
    root_dir = os.path.join(os.getcwd(), 'test')
    for parent, dir_names, file_names in os.walk(root_dir):
        # case 1:
        for dir_name in dir_names:
            pass
            # print("parent folder is:" + parent)
            # print("dirname is:" + dir_name)
        # case 2
        file_names = [os.path.join(parent, file_name) for file_name in file_names]
        for file_name in file_names:  # 遍历文件
            text = docx2txt.process(file_name)  # 读取文件数据
            with open('regular.txt', mode='r', encoding='utf-8') as regular_file:  # 读取正则表达式
                for regulars in regular_file:  # 读取正则表达式中正则式
                    if regulars.startswith('#'):
                        continue
                    regular_list = regulars.split('and')
                    regular_list = [a_regular.strip().split('for') for a_regular in
                                    regular_list]  # 对正则式进行分割，提取正则式和需要部分索引
                    result_list = [joint(regular, text) for regular in regular_list]
                    print(len(result_list[0]))
                    print(len(result_list[1]))
                    with open('title.txt', mode='w', encoding='utf-8') as title_file:
                        for index, title in enumerate(result_list[0]):
                            if index == 56:
                                s = '本公司已初步掌握口部一次成型技术，需要进一步的提升，使该项技术在低硼硅玻璃管、中性硼硅玻璃管加工中熟练掌握，使产品各项质量指标符合国际标准。'
                                title_file.write(str(index) + '  ' + title + '      ' + s)
                                title_file.write('\n')
                            if index < 56:
                                title_file.write(str(index) + '  ' + title + '      ' + result_list[1][index])
                                title_file.write('\n')
                            if index > 56:
                                title_file.write(str(index) + '  ' + title + '      ' + result_list[1][index-1])
                                title_file.write('\n')
                    # with open('content.txt', mode='w', encoding='utf-8') as content_file:
                    #     for index, content in enumerate(result_list[1]):
                    #         content_file.write(str(index) + ':' + content)
                    #         content_file.write('\n')

def get_train_data():
    # 训练语料所在文件夹
    root_dir = os.path.join(os.getcwd(), 'test')
    for parent, dir_names, file_names in os.walk(root_dir):
        # case 1:
        for dir_name in dir_names:
            pass
            # print("parent folder is:" + parent)
            # print("dirname is:" + dir_name)
        # case 2
        file_names = [os.path.join(parent, file_name) for file_name in file_names]
        for file_name in file_names:  # 遍历文件
            text = docx2txt.process(file_name)  # 读取文件数据
            with open('regular.txt', mode='r', encoding='utf-8') as regular_file:  # 读取正则表达式
                for regulars in regular_file:  # 读取正则表达式中正则式
                    if regulars.startswith('#'):
                        continue
                    regular_list = regulars.split('and')
                    regular_list = [a_regular.strip().split('for') for a_regular in
                                    regular_list]  # 对正则式进行分割，提取正则式和需要部分索引
                    result_list = [joint(regular, text) for regular in regular_list]
                    print(len(result_list[0]))
                    print(len(result_list[1]))
                    with open('train.txt', mode='a', encoding='utf-8') as title_file:
                        for index, title in enumerate(result_list[0]):
                            if index == 56:
                                s = '本公司已初步掌握口部一次成型技术，需要进一步的提升，使该项技术在低硼硅玻璃管、中性硼硅玻璃管加工中熟练掌握，使产品各项质量指标符合国际标准。'
                                title_file.write(title + '，' + s)
                                title_file.write('\n')
                            if index < 56:
                                title_file.write(title + '，' + result_list[1][index])
                                title_file.write('\n')
                            if index > 56:
                                title_file.write(title + '，' + result_list[1][index-1])
                                title_file.write('\n')
                        # for index, title in enumerate(result_list[0]):
                        #     title_file.write(title + '，' + result_list[1][index])
                        #     title_file.write('\n')
                    # with open('content.txt', mode='w', encoding='utf-8') as content_file:
                    #     for index, content in enumerate(result_list[1]):
                    #         content_file.write(str(index) + ':' + content)
                    #         content_file.write('\n')


if __name__ == '__main__':
    get_train_data()
