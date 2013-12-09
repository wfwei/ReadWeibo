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

class ManifoldRank:

    def __init__(self, graph, topic_words=_ML_WORDS, alpha=0.15, max_iter=40):
        self.max_iter = max_iter
        self.alpha = alpha
        self.graph = graph
        self.N = len(graph)
        self.ranks = {}
        self.topic_words = set(topic_words.lower().split("-"))

    def _adj_mat(self, graph, topic_words):

        # label id to each node
        st = 0
        for key in graph.nodes():
            graph.node[key]['id'] = st
            st += 1

        # make adj matrix
        n = len(graph)
        W = lil_matrix((n, n))
        y = np.zeros((n, 1))

        for edge in graph.edges():

            nod0 = graph.node[edge[0]]
            nod1 = graph.node[edge[1]]
            W[nod0['id'],nod1['id']] = 1
            W[nod1['id'],nod0['id']] = 1

            if nod0['tp']=='word' and edge[0] in topic_words:
                y[nod0['id']] = 1
            if nod1['tp']=='word' and edge[1] in topic_words:
                y[nod1['id']] = 1

        return W, y

    def rank(self):

        W, y = self._adj_mat(self.graph, self.topic_words)
        logging.info("make adjacent matrix over, and labeled %d words" % y.sum())

        D = lil_matrix((self.N, self.N))
        _sum = W.sum(1)
        for _i in range(self.N):
            if _sum[_i,0] != 0:
                D[_i, _i] = _sum[_i,0]**(-0.5)

        S = D.dot(W).dot(D)
        f = np.zeros((self.N, 1))

        for _iter in range(self.max_iter):
            logging.info('iter : %d' % _iter)
            f = self.alpha*S.dot(f) + (1-self.alpha)*y

        for key, node in self.graph.nodes(data=True):
            self.ranks[key] = f[node['id']]

if __name__ == '__main__':
    if len(sys.argv)<2:
        print '''Expected input format: %s graph [-t topic] [-m max_iter]

                 graph: graph file path
                 -t: specify topic words
                 topic: topic words seperated by '-', default with ML words
                 -m: specify max iter count
                 max_iter: max iter count, default with 20
              '''  % sys.argv[0]
        sys.exit(1)

    load_path = sys.argv[1]
    topic_words=_ML_WORDS
    max_iter=20

    _id = 2
    while _id<len(sys.argv)-1:
        if sys.argv[_id]=='-t':
            topic_words = sys.argv[_id+1].decode('utf-8')
        elif sys.argv[_id]=='-m':
            max_iter = int(sys.argv[_id+1])
        _id += 2

    G = du.load_graph(load_path)
    mr = ManifoldRank(G, topic_words=topic_words, max_iter=max_iter)
    mr.rank()

    sorted_r = sorted(mr.ranks.iteritems(), key=operator.itemgetter(1), reverse=True)

    cnt = 100
    for key, weight in sorted_r:
        if not isinstance(key, unicode):
            if key<10000000000:
                _acc = Account.objects.get(w_uid=key)
                key = u'%s\t%s' % (_acc.real_category, _acc)
            else:
                _wb = Weibo.objects.get(w_id=key)
                key = u'%s\t%s' % (_wb.real_category, _wb.text[:25])
                cnt -= 1
        else:
            pass # word

        logging.info(u'%.6f\t%s' % (weight, key))
        if cnt<0:
            break
        else:
            pass
