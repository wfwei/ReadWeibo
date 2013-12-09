# !/usr/bin/python
# -*- coding: utf-8 -*-

from ReadWeibo.mainapp.models import Category, Weibo, Comment
from ReadWeibo.account.models import Account
from main import Config
import DataUtil as du

import logging
import operator
import math, random, sys, csv

class PageRank:

    def __init__(self, graph, max_iter=20):
        self.max_iter = max_iter
        self.graph = graph
        self.V = len(self.graph)
        self.d = 0.85
        self.ranks = dict()

    def rank(self):

        for key, node in self.graph.nodes(data=True):
            if 'category' in node and node['category']=='1':
                self.ranks[key] = 1
            else:
                self.ranks[key] = 0

        for _iter in range(self.max_iter):
            print 'iter : %s' % _iter
            for key, node in self.graph.nodes(data=True):
                rank_sum = 0
                neighbors = self.graph[key]
                for n in neighbors:
                    if self.ranks[n] is not None:
                        outlinks = len(self.graph.neighbors(n))
                        rank_sum += (1 / float(outlinks)) * self.ranks[n]

                # actual page rank compution
                self.ranks[key] = ((1 - float(self.d)) * (1/float(self.V))) + self.d*rank_sum

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Expected input format: python pageRank.py <graph file path>'
        sys.exit(1)

    G = du.load_graph(load_path=sys.argv[1])
    p = PageRank(G)
    p.rank()
    sorted_r = sorted(p.ranks.iteritems(), key=operator.itemgetter(1), reverse=True)

    cnt = 100
    for key, weight in sorted_r:
        if not isinstance(key, unicode):
            if key<10000000000:
                _acc = Account.objects.get(w_uid=key)
                key = u'%s\t%s' % (_acc.real_category, _acc)
            else:
                _wb = Weibo.objects.get(w_id=key)
                key = u'%s\t%s' % (_wb.real_category, _wb.text[:20])
        else:
            pass # word
        print u'%.6f\t%s' % (weight, key)
        if cnt<0:
            break
        else:
            cnt -= 1
