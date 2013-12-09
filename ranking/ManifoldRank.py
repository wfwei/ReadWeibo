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

    def __init__(self, graph, alpha=0.15, max_iter=20):
        self.max_iter = max_iter
        self.alpha = alpha
        self.graph = graph
        self.N = len(graph)
        self.ranks = {}

    def _adj_mat(self, graph):

        # label id to each node
        st = 0
        for key in graph.nodes():
            graph.node[key]['id'] = st
            st += 1

        # make adj matrix
        n = len(graph)
        W = csr_matrix((n, n))
        y = np.zeros((n, 1))

        label_set = set()
        for edge in graph.edges():

            nod0 = graph.node[edge[0]]
            nod1 = graph.node[edge[1]]
            W[nod0['id'],nod1['id']] = 1
            W[nod1['id'],nod0['id']] = 1

            if len(label_set)<20:
                if 'category' in nod0 and nod0['category']==1 and nod0['tp']=='weibo':
                    y[nod0['id']] = 1
                    label_set.add(nod0['id'])
                if 'category' in nod1 and nod1['category']==1 and nod1['tp']=='weibo':
                    y[nod1['id']] = 1
                    label_set.add(nod1['id'])

        return W, y

    def rank(self):

        f = np.zeros((self.N, 1))
        W, y = self._adj_mat(self.graph)

        D = csr_matrix((self.N, self.N))
        _sum = W.sum(1)
        for _i in range(self.N):
            if _sum[_i,0] != 0:
                D[_i, _i] = _sum[_i,0]**(-0.5)

        S = D.dot(W).dot(D)

        for _iter in range(self.max_iter):
            print 'iter : %d' % _iter
            f = self.alpha*S.dot(f) + (1-self.alpha)*y

        for key, node in self.graph.nodes(data=True):
            self.ranks[key] = f[node['id']]

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Expected input format: %s <graph file path>'  % sys.argv[0]
        sys.exit(1)

    G = du.load_graph(load_path=sys.argv[1])
    mr = ManifoldRank(G)
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
                key = u'%s\t%s' % (_wb.real_category, _wb.text[:20])
                logging.info(u'%.6f\t%s' % (weight, key))
                cnt -= 1
        else:
            pass # word

        if cnt<0:
            break
        else:
            pass
