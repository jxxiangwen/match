#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'jxxiangwen'

import os, operator, logging, matplotlib, datetime
from .fileExist import fileExist
import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')  # ,


#                filename='myapp.log',
#                filemode='w')

def createData():
    group = np.array([[1.0, 1.1], [1.0, 1.0], [0, 0], [0, 0.1]])
    lables = ['A', 'A', 'B', 'B']
    return group, lables


def classify(intX, dataSet, lables, k):
    '''kNN 算法核心
    intX:比较向量
    dataSet:数据集
    labels:类别集
    k:类别数
    '''

    # 矩阵维度
    dataSetSize = dataSet.shape[0]
    # 扩充intX维度使得和dataSet相等，再相减，获得差值
    diffMat = np.tile(intX, (dataSetSize, 1)) - dataSet
    # 开根号
    sqDiffMat = diffMat ** 2
    # 获得距离
    sqDistances = sqDiffMat.sum(axis=1)
    distances = sqDistances ** 0.5
    # 按索引对距离排序
    sortedDistIndicies = distances.argsort()

    classCount = {}
    # 求得标签出现次数
    for i in range(k):
        voteIlabel = lables[sortedDistIndicies[i]]
        classCount[voteIlabel] = classCount.get(voteIlabel, 0) + 1
    # 按出现次数排序
    sortedClassCount = sorted(classCount.items(), key=operator.itemgetter(1), reverse=True)
    return sortedClassCount[0][0]


def file2matrix(filename, column=3):
    '''读入文件转化为类型和数据矩阵'''

    if not fileExist.fileExist(filename):
        return None
    with open(filename) as data:
        arrayOnLines = data.readlines()
        numberOfLines = len(arrayOnLines)
        # 创建数据数组
        returnMat = np.zeros((numberOfLines, column))
        classLabelVector = []
        for index, line in enumerate(arrayOnLines):
            line = line.strip()
            if 0 == index:
                print('line : %s' % line)
            listFromLine = line.split('\t')
            if 0 == index:
                print('listFromLine : %s' % listFromLine)
            returnMat[index:] = listFromLine[0:3]

            classLabelVector.append(int(listFromLine[-1]))

    return returnMat, classLabelVector


def autoNorm(dataSet):
    '''数据归一化'''
    minVals = dataSet.min(0)
    print(minVals)
    maxVals = dataSet.max(0)

    rangeVal = maxVals - minVals
    normSet = np.zeros(np.shape(dataSet))

    m = dataSet.shape[0]
    normSet = dataSet - np.tile(minVals, (m, 1))
    normSet = normSet / np.tile(rangeVal, (m, 1))

    return normSet, rangeVal, minVals


def datingClassTest():
    '''分类器测试'''
    hoRatio = 0.10
    datingDataMat, datingLabels = file2matrix('datingTestSet2.txt')
    normSet, ranges, minVals = autoNorm(datingDataMat)
    m = normSet.shape[0]
    numTestVecs = int(m * hoRatio)
    errorCount = 0.0
    for i in range(numTestVecs):
        classifierResult = classify(normSet[i, :], normSet[numTestVecs:m, :], datingLabels[numTestVecs:m], 3)
        # print('the Classifier came back with: %d, the real answer is: %d' % (classifierResult, datingLabels[i]))
        if classifierResult != datingLabels[i]:
            errorCount += 1.0

    print('the total error rate is : %f' % (errorCount / float(numTestVecs)))


def img2vector(filename):
    '''数字转化为向量'''
    returnVect = np.zeros((1, 1024))
    fr = open(filename)
    for i in range(32):
        lineStr = fr.readline()
        for j in range(32):
            returnVect[0, 32 * i + j] = int(lineStr[j])
    return returnVect


def handwritingClassTest():
    '''数字测试'''
    hwLabels = []
    trainingFileList = os.listdir('trainingDigits')  # load the training set
    m = len(trainingFileList)
    trainingMat = np.zeros((m, 1024))
    for i in range(m):
        fileNameStr = trainingFileList[i]
        fileStr = fileNameStr.split('.')[0]  # take off .txt
        classNumStr = int(fileStr.split('_')[0])
        hwLabels.append(classNumStr)
        trainingMat[i, :] = img2vector('trainingDigits/%s' % fileNameStr)
    testFileList = os.listdir('testDigits')  # iterate through the test set
    errorCount = 0.0
    mTest = len(testFileList)
    for i in range(mTest):
        fileNameStr = testFileList[i]
        fileStr = fileNameStr.split('.')[0]  # take off .txt
        classNumStr = int(fileStr.split('_')[0])
        vectorUnderTest = img2vector('testDigits/%s' % fileNameStr)
        classifierResult = classify(vectorUnderTest, trainingMat, hwLabels, 3)
        # print ("the classifier came back with: %d, the real answer is: %d" % (classifierResult, classNumStr))
        if (classifierResult != classNumStr): errorCount += 1.0
    print ("\nthe total number of errors is: %d" % errorCount)
    print ("\nthe total error rate is: %f" % (errorCount / float(mTest)))


if __name__ == '__main__':
    starttime = datetime.datetime.now()
    handwritingClassTest()
    endtime = datetime.datetime.now()
    print ('程序运行了：%s秒！' % ((endtime - starttime).seconds))
    # group, lables = createData()
    # lab = classify([0, 0], group, lables, 3)
    # print(lab)
    # dataMat, dataLabels = file2matrix('datingTestSet2.txt')
    # normSet, ranges, minVals = autoNorm(dataMat)
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # ax.scatter(normSet[:, 0], normSet[:, 1], 15 * np.array(dataLabels), 15 * np.array(dataLabels))
    # plt.show()
    # datingClassTest()
