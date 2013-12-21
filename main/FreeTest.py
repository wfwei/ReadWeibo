# !/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2013-10-7

@author: plex
'''

words = u'数据挖掘dataminingdm机器学习machinelearingml自然语言处理\
    natual language process nlp搜索searchrank数据分析datananlysis\
    机器翻译个性化推荐技术推荐系统recommendsystem大数据bigdata信息检索计算机视觉'

def jieba_cut(words=words):
    import jieba

    print 'before adding dict:'
    print u' /'.join(jieba.cut(words))
    print 'after adding dict:'
    jieba.load_userdict("/etc/jieba/jieba.dic")
    print u'/'.join(jieba.cut(words))

def jieba_posseg(words=words):

    import jieba
    import jieba.posseg as pseg
    jieba.load_userdict("/etc/jieba/jieba.dic")

    for w in pseg.cut(words):
        print w.word, w.flag

    for w in pseg.cut("这是一段话，我爱中国"):
        print w.word, w.flag


if __name__ == '__main__':
    import sys
    print sys.argv[0]
    jieba_posseg("")
    pass
