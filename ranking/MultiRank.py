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


class MultiRank:

    def __init__(self, graph, topic_words=Config._ML_WORDS,
                alpha=.0, beta=0.05, mu=0.3, eta=0.15, max_iter=40):
        self.max_iter = max_iter
        self.alpha = alpha
        self.beta = beta
        self.mu = mu
        self.eta = eta
        self.graph = graph
        self.ranks = {}
        self.topic_words = set(topic_words.lower().split("-"))

    def _adj_mat(self, graph, topic_words):
        '''
        build weibo ajd matrix by user activity
        build bipartite graph between weibo and keywords
        '''

        # label id to each node
        wb_id = 0; wd_id = 0
        for key, info in graph.nodes(data=True):
            if info['tp'] == 'weibo':
                graph.node[key]['id'] = wb_id
                wb_id += 1
            elif info['tp'] == 'word':
                graph.node[key]['id'] = wd_id
                wd_id += 1


        # make adj matrix
        W = lil_matrix((wb_id, wb_id))
        R = lil_matrix((wb_id, wd_id))
        y_wb = np.zeros((wb_id, 1))
        y_wd = np.zeros((wd_id, 1))

        print 'wb_id:%s\twd_id:%s' % (wb_id, wd_id)
        for key, info in graph.nodes(data=True):
            if info['tp'] == 'weibo':
                continue

            if info['tp'] == 'user':
                weight = 1.0
                neis = graph.neighbors(key)
                for i in range(len(neis)):
                    for j in range(len(neis))[i+1:]:
                        nod1 = graph.node[neis[i]]
                        nod2 = graph.node[neis[j]]
                        if nod1['tp']=='weibo' and nod2['tp']=='weibo':
                            W[nod1['id'], nod2['id']] += weight
                            W[nod2['id'], nod1['id']] += weight
            elif info['tp'] == 'word':
                for nod in graph.neighbors(key):
                    if graph.node[nod]['tp'] == 'weibo':
                        id1 = graph.node[nod]['id']
                        id2 = info['id']
                        R[id1, id2] += 1.0

                if key in topic_words:
                    y_wd[graph.node[key]['id'], 0] = 1.0

        return W, R, y_wb, y_wd

    def rank(self):

        W, R, y_wb, y_wd = self._adj_mat(self.graph, self.topic_words)
        logging.info("make adjacent matrix over, and labeled %d words" % y_wd.sum())

        D = lil_matrix(W.shape)
        D_d = lil_matrix((R.shape[0], R.shape[0]))
        D_t = lil_matrix((R.shape[1], R.shape[1]))

        _sum = W.sum(1)
        for _i in range(W.shape[0]):
            if _sum[_i,0] != 0:
                D[_i, _i] = _sum[_i,0]**(-0.5)
        _sum = R.sum(1)
        for _i in range(R.shape[0]):
            if _sum[_i,0] != 0:
                D_d[_i, _i] = _sum[_i,0]**(-0.5)
        _sum = R.sum(0)
        for _i in range(R.shape[1]):
            if _sum[0, _i] != 0:
                D_t[_i, _i] = _sum[0,_i]**(-0.5)

        Sw = D.dot(W).dot(D)
        Sr = D_d.dot(R).dot(D_t)

        f = np.zeros(y_wb.shape)
        alpha, beta, mu, eta = self.alpha, self.beta, self.mu, self.eta

        for _iter in range(self.max_iter):
            logging.info('iter : %d' % _iter)
            f = (1.0/(1-beta))*(mu*Sw+eta*eta/(beta+eta)*Sr.dot(Sr.T)).dot(f) \
                + alpha/(1-beta)*y_wb + beta*eta/(1-beta)/(beta+eta)*Sr.dot(y_wd)

        for key, node in self.graph.nodes(data=True):
            if node['tp'] == 'weibo':
                self.ranks[key] = f[node['id']]

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

    for mu, eta, beta in [(.1,.1,.8), (.1,.3,.6), (.3,.1,.6), (.2,.4,.4), (.4,.2,.4)]:
        mr = MultiRank(G, topic_words=topic_words, max_iter=max_iter,
                    alpha=.0, beta=beta, mu=mu, eta=eta)
        mr.rank()
        cost = mr.test(verbose=False)
        logging.info("cost=%s \t mu=%s, eta=%s, beta=%s" % (cost, mu, eta, beta))

