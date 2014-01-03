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


class ManifoldRank:

    def __init__(self, graph, topic_words=Config._ML_WORDS, alpha=0.15, max_iter=40):
        self.max_iter = max_iter
        self.alpha = alpha
        self.graph = graph
        self.ranks = {}
        self.topic_words = set(topic_words.lower().split("-"))

    def _adj_mat(self, graph, topic_words):

        # label id to each node
        nid = 0
        for key, info in graph.nodes(data=True):
            if info['tp'] == 'weibo':
                graph.node[key]['id'] = nid
                nid += 1

        # make adj matrix
        W = lil_matrix((nid, nid))
        y = np.zeros((nid, 1))

        for key, info in graph.nodes(data=True):
            if info['tp'] == 'weibo':
                continue

            if info['tp'] == 'word' and key in topic_words:
                label = True
                weight = 1.0
            else:
                label = False
                weight = 0.5


            neis = graph.neighbors(key)
            for i in range(len(neis)):
                for j in range(len(neis))[i+1:]:
                    nod1 = graph.node[neis[i]]
                    nod2 = graph.node[neis[j]]
                    if nod1['tp']=='weibo' and nod2['tp']=='weibo':
                        W[nod1['id'], nod2['id']] += weight
                        W[nod2['id'], nod1['id']] += weight

                        if label:
                            y[nod1['id']] = 1.0
                            y[nod2['id']] = 1.0

        logging.info(u"labeled %d weibo" % y.sum())

        return W, y

    def rank(self):

        W, y = self._adj_mat(self.graph, self.topic_words)
        logging.info("make adjacent matrix over, and labeled %d words" % y.sum())

        D = lil_matrix(W.shape)
        _sum = W.sum(1)
        for _i in range(D.shape[0]):
            if _sum[_i,0] != 0:
                D[_i, _i] = _sum[_i,0]**(-0.5)

        S = D.dot(W).dot(D)
        f = np.zeros(y.shape)

        for _iter in range(self.max_iter):
            logging.info('iter : %d' % _iter)
            f = self.alpha*S.dot(f) + (1-self.alpha)*y

        for nod, info in self.graph.nodes(data=True):
            if info['tp']=='weibo' and 'id' in info:
                self.ranks[nod] = f[info['id']]

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
        print '''Expected input format: %s graph [-t topic] [-m max_iter]
                 graph: graph file path
                 -t: specify topic words
                 topic: topic words seperated by '-', default with ML words
                 -m: specify max iter count
                 max_iter: max iter count, default with 20
              '''  % sys.argv[0]
        sys.exit(1)

    load_path = sys.argv[1]
    topic_words=Config._ML_WORDS
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
    cost = mr.test()
    logging.info(cost)

