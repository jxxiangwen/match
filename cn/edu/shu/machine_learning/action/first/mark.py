__author__ = '祥文'

"""将输入的分数转化为等级"""
def result(mark):
    dic = {10:'perfect',9:'A',8:'B',7:'C',6:'D'}
    if mark >100 or mark < 0:
        raise ValueError
    my = mark/10
    for value in sorted(dic.keys()):
        if my == value:
            out = dic[value]
            break
        else:
            out = 'F'

    return out

if __name__ == '__main__':
    mark = int(input("请输入成绩："))
    print(result(mark))
