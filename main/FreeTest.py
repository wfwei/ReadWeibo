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
	print ' /'.join(jieba.cut(words))
	jieba.load_userdict("../data/dic/jieba.dic")
	print 'after adding dict:'
	print '/'.join(jieba.cut(words))
	
	for wd in jieba.cut(words):
		print wd

if __name__ == '__main__':
	jieba_test()
	pass