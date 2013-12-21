# !/usr/bin/python
# -*- coding: utf-8 -*-

from ReadWeibo.mainapp.models import Category, Weibo, Comment
from ReadWeibo.account.models import Account
from main import Config

import DataUtil as du
import math, random, operator, csv
import logging, sys, os

import jieba
import jieba.posseg as pseg
jieba.load_userdict(u"/etc/jieba/jieba.dic")

class WordExtract:

    def __init__(self, model):
        self.model = model

    def extract(self, text):
        wdmap= {}
        for w in pseg.cut(text.lower()):
            if w.word in self.model:
                wdmap[w.word] = max(self.model[w.word])
        sorted_r = sorted(wdmap.iteritems(), key=operator.itemgetter(1), reverse=True)
        return ' '.join(sorted_r)

    def test():

        for item in Weibo.objects.values('owner').annotate(cnt=Count('owner')):
            if item['cnt']<=500:
                continue
            user = Account.objects.get(id=item['owner'])
            for wb in user.ownweibo.order_by("-created_at").all()[:100]:
                logging.info(wb.text)
                logging.info(self.extract(wb.text))

if __name__ == '__main__':

    model = du.load_model(sys.argv[1])
    #for key in model:
    #    print key, model[key]

    job = WordExtract(model)
    job.test()


