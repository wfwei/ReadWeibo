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


class SimpleMultiRank:

    def __init__(self, graph, topic_words=Config._ML_WORDS, alpha=0.15, max_iter=40):
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



    def classify(self, update=False):

        sorted_r = sorted(self.ranks.iteritems(), key=operator.itemgetter(1), reverse=True)

        cnt = 0
        inner_edges = 0; outer_edges = 0
        for key, weight in sorted_r:

            for nei in self.graph[key]:
                if u'visited' in self.graph[key][nei]:
                    outer_edges -= 1
                    inner_edges += 1
                else:
                    outer_edges += 1
                    self.graph[key][nei]['visited'] = True


            if not isinstance(key, unicode):
                if key<10000000000:
                    _acc = Account.objects.get(w_uid=key)
                    key = u'%s\t%s' % (_acc.real_category, _acc)
                    if update:
                        _acc.relevance = weight
                        _acc.save()
                else:
                    _wb = Weibo.objects.get(w_id=key)
                    if update:
                        _wb.relevance = weight
                        _wb.save()
                    key = u'%s\t%s:%s' % (_wb.real_category, _wb, _wb.text[:25])
            else:
                pass # word

            cnt += 1
            logging.info(u'%.6f\t%s' % (weight, key))
            logging.info(u'%d\t%d\t%d' % (cnt, inner_edges, outer_edges))


    def test(self, verbose=False):
        sorted_r = sorted(self.ranks.iteritems(), key=operator.itemgetter(1), reverse=True)
        found=0; tot=0; cost=.0
        for w_id, weight in sorted_r:
            if isinstance(w_id, unicode) or w_id<10000000000:
                continue
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
    mr = SimpleMultiRank(G, topic_words=topic_words, max_iter=max_iter)
    mr.rank()
    cost = mr.test()
    logging.info(cost)
    #mr.classify()

