# !/usr/bin/python
# -*- coding: utf-8 -*-

from ReadWeibo.mainapp.models import Category, Weibo, Comment
from ReadWeibo.account.models import Account
from django.db.models import Count
from main import Config

import DataUtil as du
import numpy as np
import math, random, operator, csv
import logging, sys, os, re


import jieba
import jieba.posseg as pseg
jieba.load_userdict(u"/etc/jieba/jieba.dic")

class StatWords:
    def st_parse(self, text):

        wdmap = {}

        pos = 0
        for w in pseg.cut(text.lower()):
            pos += 1
            if w.word not in wdmap:
                wdmap[w.word] = [0]*4
            if wdmap[w.word][0]<2:
                wdmap[w.word][0] += 1 # frequence
            if pos < 5:
                wdmap[w.word][1] = 1 # position
            if len(w.word)>2:
                wdmap[w.word][3] = 1 # length

        for keytext in re.findall(u"(#.*?#)|(【.*?】)|(《.*?》)|(\".*?\")|(“.*?”)", text.lower()):
            for t in keytext:
                for w in pseg.cut(t):
                    wdmap[w.word][2] = 1 # environment

        return wdmap

    def test(self, limit=1000):
        st = np.array([0]*4)
        wdcnt = 0; wbcnt = 0
        for wb in Weibo.objects.filter(exp=2):
            text = re.sub("@[^\s@:]+", "", wb.text)
            text = re.sub(u"http://t.cn[^ ]*", u"", text)
            text = re.sub(u"\[[^ ]{1,3}\]", u"", text)
            res = self.st_parse(text)
            wbcnt += 1
            for wd in wb.keywords.split():
                wdcnt += 1
                if wd not in res:
                    continue
                st += res[wd]

        logging.info("weibo count:%s" % wbcnt)
        logging.info("word  count:%s" % wdcnt)
        logging.info("frequence:%s" % (st[0]))
        logging.info("position: %s" % (st[1]))
        logging.info("environment:%s" % (st[2]))
        logging.info("length:%s" % (st[3]))



if __name__ == '__main__':
    job = StatWords()
    job.test()

