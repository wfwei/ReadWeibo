# !/usr/bin/python
# -*- coding: utf-8 -*-

from ReadWeibo.mainapp.models import Category, Weibo, Comment
from ReadWeibo.account.models import Account
from django.db.models import Count
from main import Config

import DataUtil as du
import Eva
import numpy as np
import math, random, operator, csv
import logging, sys, os, re


import jieba
import jieba.posseg as pseg
jieba.load_userdict(u"/etc/jieba/jieba.dic")

class WordExtract:

    def __init__(self, model):
        self.model = model

    def st_parse(self, text, freq=.15, pos=.25, env=.4, le=.2):

        wdmap = {}

        pos = 0
        for w in pseg.cut(text.lower()):
            pos += 1
            if w.word not in self.model:
                continue
            if w.word not in wdmap:
                wdmap[w.word] = [0]*4
            wdmap[w.word][0] += freq/2 # frequence
            if pos < 5:
                wdmap[w.word][1] = pos # position
            if len(w.word)>2:
                wdmap[w.word][3] = le # length

        for keytext in re.findall(u"(#.*?#)|(【.*?】)|(《.*?》)|(\".*?\")|(“.*?”)", text.lower()):
            for t in keytext:
                for w in pseg.cut(t):
                    if w.word not in self.model:
                        continue
                    wdmap[w.word][2] = env # environment

        return wdmap

    def extract(self, text, alpha=0.2):

        text = re.sub("@[^\s@:]+", "", text)
        text = re.sub(u"http://t.cn[^ ]*", u"", text)
        text = re.sub(u"\[[^ ]{1,3}\]", u"", text)

        st_wdmap = self.st_parse(text)

        wdmap= {}
        summ = np.array([0])
        for w in pseg.cut(text.lower()):
            if w.word in self.model:
                wdmap[w.word] = self.model[w.word]
                if summ.any():
                    summ += wdmap[w.word]
                else:
                    summ = np.array(wdmap[w.word])

        cnt = 10
        max_idx = np.argmax(summ)
        for word in wdmap:
            wdmap[word] = self.model[word][max_idx] * sum(st_wdmap[word])
            if cnt < 2:
                print (self.model[word][max_idx], st_wdmap[word])
                cnt += 1

        sorted_r = sorted(wdmap.iteritems(), key=operator.itemgetter(1), reverse=True)

        return [item[0] for item in sorted_r]


    def tf_extract(self, text, alpha=0.2):

        text = re.sub("@[^\s@:]+", "", text)
        text = re.sub(u"http://t.cn[^ ]*", u"", text)
        text = re.sub(u"\[[^ ]{1,3}\]", u"", text)

        st_wdmap = self.st_parse(text)
        for word in st_wdmap:
            st_wdmap[word] = st_wdmap[word][0]

        sorted_r = sorted(st_wdmap.iteritems(), key=operator.itemgetter(1), reverse=True)

        return [item[0] for item in sorted_r]

    def train(self, limit=1000):
        for user in Account.objects.filter(exp=1):
            for wb in user.ownweibo.order_by("-created_at").filter(retweeted_status__exact=None)[:10]:
                sorted_r = self.extract(wb.text)
                wb.keywords = ' '.join([item[0].encode('utf-8') for item in sorted_r])
                wb.save()
                limit -= 1
            if limit<=0:
                break

    def test1(self, maxn=10):
        cnt = 0;
        _p=[.0]*maxn; _r=[.0]*maxn; _f=[.0]*maxn; _map=[.0]*maxn; _ndcg=[.0]*maxn
        for wb in Weibo.objects.filter(exp=2):
            sorted_r = wb.keywords.split()[:maxn]
            #sorted_p = self.tf_extract(wb.text)
            sorted_p = self.extract(wb.text)
            cnt += 1
            if len(sorted_p) and len(sorted_r):
                for n in range(maxn):
                    prf = Eva.prf(sorted_r, sorted_p, n+1)
                    _p[n] += prf[0]; _r[n] += prf[1]; _f[n] += prf[2]
                    _map[n] += Eva.ap(sorted_r, sorted_p, n+1)
                    _ndcg[n] += Eva.ndcg(sorted_r, sorted_p, n+1)

        for n in range(maxn):
            _p[n]/=cnt; _r[n]/=cnt; _f[n]/=cnt; _map[n]/=cnt; _ndcg[n]/=cnt
            print n, _p[n], _r[n], _f[n], _map[n], _ndcg[n]

    def test2(self):
        cnt = 0; alpha = 0.1; maxn=11
        _p=[.0]*maxn; _r=[.0]*maxn; _f=[.0]*maxn; _map=[.0]*maxn; _ndcg=[.0]*maxn
        for wb in Weibo.objects.filter(exp=2):
            cnt += 1
            for n in range(11):
                sorted_r = wb.keywords.split()[:5]
                sorted_p = self.extract(wb.text, alpha*n)
                if len(sorted_p) and len(sorted_r):
                    prf = Eva.prf(sorted_r, sorted_p, 5)
                    _p[n] += prf[0]; _r[n] += prf[1]; _f[n] += prf[2]
                    _map[n] += Eva.ap(sorted_r, sorted_p, 5)
                    _ndcg[n] += Eva.ndcg(sorted_r, sorted_p, 5)

        for n in range(maxn):
            _p[n]/=cnt; _r[n]/=cnt; _f[n]/=cnt; _map[n]/=cnt; _ndcg[n]/=cnt
            print n, _p[n], _r[n], _f[n], _map[n], _ndcg[n]




if __name__ == '__main__':
    model = du.load_tpr_model(u'%s/result.txt' % sys.argv[1])
    job = WordExtract(model)
    job.test1()

