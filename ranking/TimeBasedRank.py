# !/usr/bin/python
# -*- coding: utf-8 -*-

from ReadWeibo.mainapp.models import Category, Weibo, Comment
from ReadWeibo.account.models import Account
from main import Config
import DataUtil as du

from scipy.sparse import *
from scipy import *

import numpy as np
import logging
import operator
import math, random, sys, csv

_ML_WORDS = u'数据挖掘-datamining-dm-机器学习-machinelearing-ml-自然语言处理-natuallanguageprocess-nlp-模式识别-patternrecognization-信息检索-informationretrieval-统计学习-statisticsstudy-CTR-人脸识别-facerecognization-模型优化-modeloptimization-社交网络-socialnetwork-搜索引擎-searchengine-rank-数据分析-dataanlysis-机器翻译-个性化推荐-推荐系统-recommendsystem-大数据-bigdata-计算机视觉-文本挖掘-textmining'

class TimeBasedRank:

    def __init__(self, graph, topic_words=_ML_WORDS, limit=40):
        self.graph = graph
        self.topic_words = set(topic_words.lower().split("-"))
        self.limit = limit
        self.ranks = {}

    def rank(self):

        missing = []
        limit = self.limit
        nodes = self.graph.node

        for word in self.topic_words:
            if not self.graph.has_node(word):
                missing.append(word)
                continue

            for nei in self.graph.neighbors(word):
                if 'weibo'==nodes[nei]['tp'] and 'time' in nodes[nei]:
                    self.ranks[nei] = nodes[nei]['time']
                    limit -= 1
                    if limit<=0:
                        break
            if limit<=0:
                break
        logging.info("%s not found" % " ".join(missing))

    def test(self, verbose=False):
        sorted_r = sorted(self.ranks.iteritems(), key=operator.itemgetter(1), reverse=True)
        found=0; tot=0; cost=.0
        for w_id, weight in sorted_r:
            wb = Weibo.objects.get(w_id=w_id)
            tot += 1
            if wb.real_category==1:
                found += 1
                cost += math.log(tot-found+1)
            if verbose:
                logging.info("%s\t%s\t%s" % (wb.real_category, weight, wb.text[:30]))
        return cost



if __name__ == '__main__':

    if len(sys.argv)<2:
        print '''Expected input format: %s graph [-t topic] [-l limit]
                 graph: graph file path
                 -t: specify topic words
                 topic: topic words seperated by '-', default with ML words
                 -l: specify result limit
                 limit: result limit
              '''  % sys.argv[0]
        sys.exit(1)

    load_path = sys.argv[1]
    topic_words=_ML_WORDS
    limit = 100

    _id = 2
    while _id<len(sys.argv)-1:
        if sys.argv[_id]=='-t':
            topic_words = sys.argv[_id+1].decode('utf-8')
        elif sys.argv[_id]=='-l':
            limit = int(sys.argv[_id+1])
        _id += 2

    G = du.load_graph(load_path)
    tbr = TimeBasedRank(G, topic_words=topic_words, limit=limit)
    tbr.rank()
    cost = tbr.test()
    logging.info(cost)
