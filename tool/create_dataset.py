# -*- coding: utf-8 -*-
from __future__ import print_function
from pdb import set_trace
import os
import lmdb # install lmdb by "pip install lmdb"
import cv2
import numpy as np
#from genLineText import GenTextImage

def checkImageIsValid(imageBin):
    if imageBin is None:
        return False
    imageBuf = np.fromstring(imageBin, dtype=np.uint8)
    img = cv2.imdecode(imageBuf, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return False
    imgH, imgW = img.shape[0], img.shape[1]
    if imgH * imgW == 0:
        return False
    return True

def writeCache(env, cache):
    with env.begin(write=True) as txn:
        for k, v in cache.items():
            #txn.put(k.encode(), v)
            txn.put(k, v)


def createDataset(outputPath, imagePathList, labelList, lexiconList=None, checkValid=True):
    """
    Create LMDB dataset for CRNN training.

    ARGS:
        outputPath    : LMDB output path
        imagePathList : list of image path
        labelList     : list of corresponding groundtruth texts
        lexiconList   : (optional) list of lexicon lists
        checkValid    : if true, check the validity of every image
    """
    #print (len(imagePathList) , len(labelList))
    assert(len(imagePathList) == len(labelList))
    nSamples = len(imagePathList)
    print('...................')
    # map_size=1099511627776 定义最大空间是1TB
    env = lmdb.open(outputPath, map_size=1099511627776)
    
    cache = {}
    cnt = 1
    print(labelList[0])
    print('Begin to Create LMDB')
    for i in range(nSamples):
        imagePath = imagePathList[i]
        label = labelList[i]
        print(label)
        print('label len: {}'.format(len(label)))
        if not os.path.exists(imagePath):
            print('%s does not exist' % imagePath)
            continue
        print(imagePath)
        with open(imagePath, 'rb') as f:
            imageBin = f.read()
        if checkValid:
            if not checkImageIsValid(imageBin):
                print('%s is not a valid image' % imagePath)
                continue


        ########## .mdb数据库文件保存了两种数据，一种是图片数据，一种是标签数据，它们各有其key
        imageKey = 'image-%09d' % cnt
        labelKey = 'label-%09d' % cnt
        cache[imageKey.encode()] = imageBin
        cache[labelKey.encode()] = label.encode()
        ##########
        if lexiconList:
            lexiconKey = 'lexicon-%09d' % cnt
            cache[lexiconKey] = ' '.join(lexiconList[i])
        if cnt % 1000 == 0:
            writeCache(env, cache)
            cache = {}
            print('Written %d / %d' % (cnt, nSamples))
        cnt += 1
        if i%100 ==0:
            print('{}/{}'.format(i,nSamples))
    nSamples = cnt-1
    cache['num-samples'.encode()] = str(nSamples).encode()
    writeCache(env, cache)
    print('Created dataset with %d samples' % nSamples)


def read_text(path):
    
    with open(path) as f:
        text = f.read()
    text = text.strip()
    
    return text

import glob
if __name__ == '__main__':
    
    #lmdb 输出目录
    outputPath = '../lmdb/train'
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

    # 训练图片路径，标签是txt格式，名字跟图片名字要一致，如123.png对应标签需要是123.txt
    path = '../augmented_currency/train/*.png'


    imagePathList = glob.glob(path)

    len_list = len(imagePathList)
    print('------------',len_list,'------------')
    imgLabelLists = []
    print('Begin add imageName to labelLists')

    num = 0
    for p in imagePathList:
        text_name = p.replace('.png','.txt').replace('img', 'text')
        #if not os.path.exists(p.replace('.png','.txt')):
        if not os.path.exists(text_name):
            #print('{} does not exist!'.format(p.replace('.png','.txt')))
            print('{} does not exist!'.format(text_name))
            continue
        t = read_text(text_name)
        imgLabelLists.append((p,t))
        num+=1
        if num%500 ==0:
            print('{}/{}'.format(num,len_list))
    print('add imageName to labelLists Done!!')
    #imgLabelList = [ (p,read_text(p.replace('.png','.txt'))) for p in imagePathList]
    ##sort by lebelList
    print('Begin to srot')
    imgLabelList = sorted(imgLabelLists,key = lambda x:len(x[1]))
    #imgPaths = [ p[0].encode() for p in imgLabelList]
    imgPaths = [ p[0] for p in imgLabelList]
    #txtLists = [ p[1].encode() for p in imgLabelList]
    txtLists = [ p[1] for p in imgLabelList]
    print('srot ok!!!')
    createDataset(outputPath, imgPaths, txtLists, lexiconList=None, checkValid=True)
