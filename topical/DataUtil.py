# !/usr/bin/python
# -*- coding: utf-8 -*-

from ReadWeibo.mainapp.models import *
from ReadWeibo.account.models import *
from django.db.models import Count
from main import Config

import networkx as nx
import sys, re, logging

STOP_WORDS = frozenset(('a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'can',
                        'for', 'from', 'have', 'if', 'in', 'is', 'it', 'may',
                        'not', 'of', 'on', 'or', 'tbd', 'that', 'the', 'this',
                        'to', 'us', 'we', 'when', 'will', 'with', 'yet','out',
                        'you', 'your', 'cn', 'ok', 'com', 'via', 'but', 'has',
                        'what', 'no', 'how', 'very', 'like', 'still', 'more',
                        'now', u'转发',u'微博', u'回复', u'呵呵', u'偷笑',
                        'http', 'he', 'so', 'the', 'all', 'well', '__'))

def gen_data(graph_path, lda_path, user_lim=200, user_wb_lim=200):

    import jieba
    import jieba.posseg as pseg
    jieba.load_userdict(u"/etc/jieba/jieba.dic")

    G = nx.Graph()
    ldaf = open(lda_path, 'w')
    ucnt = 0
    for item in Weibo.objects.values('owner').annotate(cnt=Count('owner')):
        if item['cnt']>500:
            user = Account.objects.get(id=item['owner'])
            logging.info(u'%5d Dealing with %s' % (ucnt, user))
            logging.info(u'Current graph:%d nodes and %d edges' % (G.number_of_nodes(), G.number_of_edges()))
            user_words = []
            for wb in user.ownweibo.order_by("-created_at").all()[:user_wb_lim]:
                #filter(retweeted_status__exact=None).all():
                wb_words = []
                for w in pseg.cut(wb.text.lower()):
                    if len(w.word)>1 and ('n' in w.flag or 'x' in w.flag or 'v' in w.flag) and (w.word not in STOP_WORDS):
                        wb_words.append(w.word.encode('utf-8'))
                if not wb_words:
                    continue
                for w1, w2 in zip(wb_words[:-1], wb_words[1:]):
                    if not G.has_edge(w1, w2):
                        G.add_edge(w1, w2, weight=1.0)
                    else:
                        G[w1][w2]['weight'] += 1.0
                user_words.extend(wb_words)

            if not user_words:
                continue
            ldaf.write(' '.join(user_words)+'\n')
            ucnt += 1
            if ucnt>user_lim:
                break

    if graph_path:
        nx.write_yaml(G, graph_path, encoding='UTF-8')
    ldaf.close()

    return G

def load_graph(load_path, encoding='UTF-8'):
    logging.info('Loading graph from file:%s' % load_path)
    G=nx.read_yaml(load_path)
    logging.info('Loaded %d nodes and %d edges' % (G.number_of_nodes(), G.number_of_edges()))
    return G

def load_model(load_path, encoding='UTF-8'):
    logging.info('Loading word weights model from file:%s' % load_path)
    wdset = {}; cnt=0
    with open(load_path, 'r') as inf:
        for line in inf:
            val = line.split("\t", 1)
            wdset[val[0]] = eval(val[1])
            cnt += 1
            if cnt%1000 == 0:
                print 'loaded %d words' % cnt
    logging.info('Loaded %d words' % cnt)
    return wdset

if __name__ == '__main__':
    gen_data(graph_path=u'%s/graph.yaml'%sys.argv[1], lda_path=u'%s/lda_small.train'%sys.argv[1], user_lim=200, user_wb_lim=200)
    pass


