# !/usr/bin/python
# -*- coding: utf-8 -*-

from ReadWeibo.mainapp.models import Category, Weibo, Comment
from ReadWeibo.account.models import Account
from main import Config

import DataUtil as du
import networkx as nx
import numpy as np
import math, random, operator, csv
import logging, sys, os
import copy

class TopicalWordRank:

    def __init__(self, graph, max_iter=20):
        self.max_iter = max_iter
        self.graph = graph
        self.ntopics = 25
        self.ranks = dict()
        self.p = dict()

    def gibbs_lda(self, fdir, ntopics=25, niters=1000, savestep=500, twords=20):
        self.ntopics = ntopics

        logging.info("lda topic modeling")
        cmd = ["/home/plex/wksp/projects/GibbsLDA++-0.2/src/lda -est", " -ntopics %s " % ntopics,
              " -niters %s " % niters, "-savestep %s " % savestep,
              "-twords %s " % twords, "-dfile %s/lda.train" % fdir]
        logging.info(u''.join(cmd))
        os.system(u''.join(cmd))

        logging.info("Loading lda result")
        self.p = du.load_lda_model(fdir, ntopics)
        self.ranks = copy.deepcopy(self.p)

    def rank(self, lam=0.85):

        ntopics = self.ntopics
        graph = self.graph

        for _iter in range(self.max_iter):
            logging.info(u'TopicalWordRank iter : %s' % _iter)
            for key, node in graph.nodes(data=True):
                rank_sum = np.array([.0]*ntopics)
                for nei in graph[key]:
                    weight = graph[key][nei]['weight']
                    weight_sum = .0
                    for out in graph[nei]:
                        weight_sum += graph[nei][out]['weight']
                    if type(nei)==str:
                        nei = nei.decode('utf-8')
                    rank_sum += (weight / weight_sum) * self.ranks[nei]
                if type(key)==str:
                    key = key.decode('utf-8')
                self.ranks[key] = lam*rank_sum + (1 - lam)*self.p[key]

    def save(self, fpath, with_log=True):
        with open(fpath, 'w') as resf:
            for key in self.ranks:
                result = u"%s\t%s\n" % (key, [val for val in self.ranks[key]])
                if with_log:
                    logging.info(result)
                resf.write(result.encode('utf-8'))

if __name__ == '__main__':

    fdir = sys.argv[1]

    G = du.gen_data(graph_path=u'%s/graph.yaml' % fdir,
                    lda_path=u'%s/lda.train' % fdir,
                    user_lim=2, user_wb_lim=20)

    #G = du.gen_data(graph_path=u'%s/graph.yaml' % fdir,
    #                lda_path=u'%s/lda.train' % fdir,
    #                user_lim=200, user_wb_lim=200)
    #G = du.load_graph(u'%s/graph.yaml' % fdir)
    job = TopicalWordRank(G)
    #job.gibbs_lda(fdir, ntopics=50, niters=1000, savestep=1000, twords=20)
    job.gibbs_lda(fdir, ntopics=2, niters=10, savestep=10, twords=20)
    job.rank()
    job.save(u'%s/result.txt' % fdir)

    pass
