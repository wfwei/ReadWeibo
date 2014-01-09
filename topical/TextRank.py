# !/usr/bin/python
# -*- coding: utf-8 -*-

from ReadWeibo.mainapp.models import Category, Weibo, Comment
from ReadWeibo.account.models import Account
from main import Config
import DataUtil as du

import logging
import operator
import math, random, sys, csv
import DataUtil as du
import Eva
import numpy as np
import math, random, operator, csv
import logging, sys, os, re


import jieba
import jieba.posseg as pseg
jieba.load_userdict(u"/etc/jieba/jieba.dic")

class TextRank:

    def __init__(self, graph, max_iter=20):
        self.max_iter = max_iter
        self.graph = graph
        self.V = len(self.graph)
        self.d = 0.85
        self.ranks = {}

    def rank(self):

        print 'init weights'
        for key in self.graph.nodes():
            self.ranks[key] = .0

        print 'convert to directed graph'
        DG = self.graph.to_directed()
        for key in DG:
            tot_w = 1.0
            for nei in DG[key]:
                tot_w += DG[key][nei]['weight']
            for nei in DG[key]:
                DG[key][nei]['weight'] /= tot_w

        for _iter in range(self.max_iter):
            print 'iter : %s' % _iter
            for key in DG:
                rank_sum = 0
                for nei in DG[key]:
                    rank_sum += DG[nei][key]['weight'] * self.ranks[nei]

                # actual page rank compution
                self.ranks[key] = ((1 - self.d) * (1/float(self.V))) + self.d*rank_sum


    def extract(self, text):

        text = re.sub("@[^\s@:]+", "", text)
        text = re.sub(u"http://t.cn[^ ]*", u"", text)
        text = re.sub(u"\[[^ ]{1,3}\]", u"", text)

        wdmap = {}

        for w in pseg.cut(text.lower()):
            if w.word in self.ranks:
                wdmap[w.word] = self.ranks[w.word]


        sorted_r = sorted(wdmap.iteritems(), key=operator.itemgetter(1), reverse=True)

        return [item[0] for item in sorted_r]


    def test(self, maxn=10):
        cnt = 0;
        _p=[.0]*maxn; _r=[.0]*maxn; _f=[.0]*maxn; _map=[.0]*maxn; _ndcg=[.0]*maxn
        for wb in Weibo.objects.filter(exp=2):
            sorted_r = wb.keywords.split()[:maxn]
            sorted_p = self.extract(wb.text)
            if len(sorted_p) and len(sorted_r):
                cnt += 1
                for n in range(maxn):
                    prf = Eva.prf(sorted_r, sorted_p, n+1)
                    _p[n] += prf[0]; _r[n] += prf[1]; _f[n] += prf[2]
                    _map[n] += Eva.ap(sorted_r, sorted_p, n+1)
                    _ndcg[n] += Eva.ndcg(sorted_r, sorted_p, n+1)

        for n in range(maxn):
            _p[n]/=cnt; _r[n]/=cnt; _f[n]/=cnt; _map[n]/=cnt; _ndcg[n]/=cnt
            print n, _p[n], _r[n], _f[n], _map[n], _ndcg[n]



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Expected input format: python pageRank.py <graph file path>'
        sys.exit(1)
    #G = du.gen_data(graph_path=u'%s/graph.yaml'%sys.argv[1], lda_path=u'%s/lda.train'%sys.argv[1], user_lim=150, user_wb_lim=200)
    G = du.load_graph(load_path=sys.argv[1])
    p = TextRank(G)
    p.rank()
    p.test()
