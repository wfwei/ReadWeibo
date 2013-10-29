# !/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2013-10-7

@author: plex
'''

def jieba_test():
    import jieba
    words = u'数据挖掘dataminingdm机器学习machinelearingml自然语言处理\
    natual language process nlp搜索searchrank数据分析datananlysis\
    机器翻译个性化推荐技术推荐系统recommendsystem大数据bigdata信息检索计算机视觉'

    print 'before adding dict:'
    print u' /'.join(jieba.cut(words))

    print 'after adding dict:'
    jieba.load_userdict("jieba.dic")
    print u'/'.join(jieba.cut(words))


if __name__ == '__main__':
    import sys
    print sys.argv[0]
    pass
