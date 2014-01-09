# !/usr/bin/python
# -*- coding: utf-8 -*-

from ReadWeibo.mainapp.models import Category, Weibo, Comment
from ReadWeibo.account.models import Account
from main import Config
import DataUtil as du

from scipy.sparse import *
import scipy.sparse.linalg as linalg

import numpy as np
import heapq
import logging
import operator
import math, random, sys, csv


class TriRank:

    def __init__(self, graph, K, alpha=1.0, beta=1.0, gamma=1.0):
        self.alpha, self.beta, self.gamma = alpha, beta, gamma
        self.graph = graph
        self.coor = {}
        self.K = K

    def _adj_mat(self, graph):
        '''
        build three bipartite graph between <weibo, user, keywords>
        '''

        # label id to each node
        wb_id, wd_id, u_id = 0, 0, 0
        for key, info in graph.nodes(data=True):
            if info['tp'] == 'weibo':
                graph.node[key]['id'] = wb_id
                wb_id += 1
            elif info['tp'] == 'word':
                graph.node[key]['id'] = wd_id
                wd_id += 1
            elif info['tp'] == 'user':
                graph.node[key]['id'] = u_id
                u_id += 1

        print 'user:%s\twb_id:%s\twd_id:%s' % (u_id, wb_id, wd_id)

        # make adj matrix
        R_ut = lil_matrix((u_id, wd_id))
        R_ud = lil_matrix((u_id, wb_id))
        R_td = lil_matrix((wd_id, wb_id))

        for nod1, nod2, info in G.edges_iter(data=True):
            info1 = G.node[nod1]
            info2 = G.node[nod2]
            if info1['tp']=='user':
                if info2['tp']=='weibo':
                    R_ud[info1['id'], info2['id']] = info['weight']
                elif info2['tp']=='word':
                    R_ut[info1['id'], info2['id']] = info['weight']
            elif info1['tp']=='weibo':
                if info2['tp']=='user':
                    R_ud[info2['id'], info1['id']] = info['weight']
                elif info2['tp']=='word':
                    R_td[info2['id'], info1['id']] = info['weight']
            if info1['tp']=='word':
                if info2['tp']=='weibo':
                    R_td[info1['id'], info2['id']] = info['weight']
                elif info2['tp']=='user':
                    R_ut[info2['id'], info1['id']] = info['weight']

        D_ut = lil_matrix((u_id, u_id))
        D_ud = lil_matrix((u_id, u_id))
        D_dt = lil_matrix((wb_id, wb_id))
        D_du = lil_matrix((wb_id, wb_id))
        D_td = lil_matrix((wd_id, wd_id))
        D_tu = lil_matrix((wd_id, wd_id))

        _sum_ut, _sum_ud = R_ut.sum(1), R_ud.sum(1)
        for _i in range(u_id):
            if _sum_ut[_i,0] != 0:
                D_ut[_i, _i] = _sum_ut[_i,0]
            if _sum_ud[_i,0] != 0:
                D_ud[_i, _i] = _sum_ud[_i,0]

        _sum_dt, _sum_du = R_td.sum(0).T, R_ud.sum(1)
        for _i in range(wb_id):
            if _sum_dt[_i,0] != 0:
                D_dt[_i, _i] = _sum_dt[_i,0]
            if _sum_du[_i,0] != 0:
                D_du[_i, _i] = _sum_du[_i,0]

        _sum_td, _sum_tu = R_td.sum(1), R_ut.sum(0).T
        for _i in range(wd_id):
            if _sum_td[_i,0] != 0:
                D_td[_i, _i] = _sum_td[_i,0]
            if _sum_tu[_i,0] != 0:
                D_tu[_i, _i] = _sum_tu[_i,0]

        return R_ut, R_ud, R_td, D_ut, D_ud, D_dt, D_du, D_td, D_tu

    def build_model(self):

        alpha, beta, gamma = self.alpha, self.beta, self.gamma
        R_ut, R_ud, R_td, D_ut, D_ud, D_dt, D_du, D_td, D_tu = self._adj_mat(self.graph)

        u_cnt = D_ud.shape[0]
        t_cnt = D_tu.shape[0]
        d_cnt = D_du.shape[0]

        u_mat = alpha*D_ut+gamma*D_ud
        t_mat = alpha*D_tu+beta*D_td
        d_mat = beta*D_dt+gamma*D_du

        print 'alpha:%s, beta:%s, gamma:%s' % (alpha, beta, gamma)

        print u_mat.shape, R_ut.shape, R_ud.shape
        print R_ut.T.shape, t_mat.shape, R_td.shape
        print R_ud.T.shape, R_td.T.shape, d_mat.shape

        L = bmat([ [u_mat, -alpha*R_ut, -gamma*R_ud],
                 [-alpha*R_ut.T, t_mat, -beta*R_td ],
                 [-gamma*R_ud.T, -beta*R_td.T, d_mat]])

        print 'L.shape:', L.shape

        D = block_diag((u_mat, t_mat, d_mat))

        print 'D.shape:', D.shape

        #TODO how to find smallest non-zero eigen vaues
        eigen_value, eigen_vec_r = linalg.eigs(L, k=min(self.K, L.shape[0]), M=D, sigma=0.05)

        print 'eigen_value.shape', eigen_value.shape
        print 'eigen_vec_r.shape', eigen_vec_r.shape
        print 'eigen_values:', eigen_value

        h = eigen_vec_r # secode small eigen value (-> eigen vector)
        print 'h.shape', h.shape

        for node, info in self.graph.nodes(data=True):
            if info['tp']=='user':
                offset = 0
            elif info['tp']=='word':
                offset = u_cnt
            elif info['tp']=='weibo':
                offset = u_cnt + t_cnt
            self.coor[node] = h[offset + info['id']]

    def test(self, query, topk=15, verbose=False):

        if query not in self.coor:
            logging.warn(u"query not found")
            return

        result = [(None, sys.float_info.min)]*topk
        coor = self.coor
        target = coor[query]

        for item in coor:
            heapq.heappushpop(result, (1.0/(1+np.linalg.norm(coor[item]-target)), item))

        logging.info(u"Query:%s" % query)
        sorted_r =  [heapq.heappop(result) for i in range(min(len(result), topk))]
        for weight, item in sorted_r:
            logging.info(u"weight:%s\titem:%s" % (weight, item))

        return result

if __name__ == '__main__':
    if len(sys.argv)<2:
        print '''Expected input format: %s graph query
                 graph: graph file path
                 query: query
              '''  % sys.argv[0]
        sys.exit(1)

    load_path = sys.argv[1]
    query = sys.argv[2].decode('utf-8')


    #G = du.gen_graph(load_path, start_idx=1000, max_cnt=500)
    G = du.load_graph(load_path)
    tr = TriRank(G, 19)
    tr.build_model()
    tr.test(query, topk=20)

