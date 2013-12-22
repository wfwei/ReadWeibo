# !/usr/bin/python
# -*- coding: utf-8 -*-

from ReadWeibo.mainapp.models import *
from ReadWeibo.account.models import *
from django.db.models import Count
from main import Config

import networkx as nx
import numpy as np
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
    ldaf.write("%d\n" % user_lim)
    ucnt = 0
    for item in Weibo.objects.values('owner').annotate(cnt=Count('owner')):
        if item['cnt']>450:
            user = Account.objects.get(id=item['owner'])
            logging.info(u'%5d Dealing with %s' % (ucnt, user))
            logging.info(u'Current graph:%d nodes and %d edges' % (G.number_of_nodes(), G.number_of_edges()))
            user_words = []
            for wb in user.ownweibo.order_by("-created_at").all()[:user_wb_lim]:
                #filter(retweeted_status__exact=None).all():
                text = wb.text.lower()
                #if wb.retweeted_status:
                #   text = w.retweeted_status.text.lower() + text
                for word in re.findall("【.+?】|#.+?#|《.+?》|“.+?”|\".+?\"", text):
                    for w in pseg.cut(word):
                        if len(w.word)<2 or w.word in STOP_WORDS or 'n' not in w.flag:
                            continue
                        wd = w.word.encode('utf-8')
                        if G.has_node(wd) and 'weight' in G.node[wd]:
                            G.node[wd]['weight'] += 1.0
                        else:
                            G.add_node(wd, weight=1.0)

                wb_words = []
                for w in pseg.cut(text):
                    if len(w.word)>1 and 'n' in w.flag and w.word not in STOP_WORDS:
                        wb_words.append(w.word.encode('utf-8'))
                if not wb_words:
                    continue
                for w1, w2, w3 in zip(wb_words[:-2], wb_words[1:-1], wb_words[2:]):
                    if not G.has_edge(w1, w2):
                        G.add_edge(w1, w2, weight=1.0)
                    else:
                        G[w1][w2]['weight'] += 1.0
                    if not G.has_edge(w1, w3):
                        G.add_edge(w1, w3, weight=1.0)
                    else:
                        G[w1][w3]['weight'] += 1.0
                user_words.extend(wb_words)

            if not user_words:
                continue
            ldaf.write(' '.join(user_words)+'\n')
            ucnt += 1
            if ucnt>=user_lim:
                break

    if ucnt<user_lim:
        logging.error("no enough docs, %d/%d" % (ucnt, user_lim))

    if graph_path:
        nx.write_yaml(G, graph_path, encoding='UTF-8')
    ldaf.close()

    return G

def load_graph(load_path, encoding='UTF-8'):
    logging.info('Loading graph from file:%s' % load_path)
    G=nx.read_yaml(load_path)
    logging.info('Loaded %d nodes and %d edges' % (G.number_of_nodes(), G.number_of_edges()))
    return G

def load_lda_model(load_path, ntopics, encoding='UTF-8'):
    logging.info('Loading lda model from dir:%s' % load_path)
    wdict = {}

    with open("%s/wordmap.txt" % load_path, "r") as wmf:
        words = [None]*int(wmf.readline())
        for line in wmf:
            word, idx = line.split()
            words[int(idx)] = word.decode('utf-8')
            wdict[word.decode('utf-8')] = np.array([.0]*ntopics)

    with open("%s/model-final.phi" % load_path, "r") as phif:
        for t in range(ntopics):
            weights = [float(w) for w in phif.readline().split()]
            for word, weight in zip(words, weights):
                wdict[word][t] = weight
            print 'loaded %d topics' % t

    logging.info('Loaded %d words' % len(words))
    return wdict

def load_tpr_model(load_path, encoding='UTF-8'):
    logging.info('Loading topical pagerank model from file:%s' % load_path)
    wdict = {}; cnt=0
    with open(load_path, 'r') as inf:
        for line in inf:
            val = line.split("\t", 1)
            wdict[val[0].decode('utf-8')] = eval(val[1])
            cnt += 1
            if cnt%1000 == 0:
                print 'loaded %d words' % cnt
    logging.info('Loaded %d words' % cnt)
    return wdict


if __name__ == '__main__':
    gen_data(graph_path=u'%s/graph.yaml'%sys.argv[1], lda_path=u'%s/lda.train'%sys.argv[1], user_lim=200, user_wb_lim=200)
    pass


