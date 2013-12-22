# !/usr/bin/python
# -*- coding: utf-8 -*-

from ReadWeibo.mainapp.models import Category, Weibo, Comment
from ReadWeibo.account.models import Account
from django.db.models import Count
from main import Config

import DataUtil as du
import math, random, operator, csv
import logging, sys, os, re


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
                wdmap[w.word] = sum(self.model[w.word])
        sorted_r = sorted(wdmap.iteritems(), key=operator.itemgetter(1), reverse=True)
        return ' '.join([item[0] for item in sorted_r])

    def test(self):
        for item in Weibo.objects.values('owner').annotate(cnt=Count('owner')):
            if item['cnt']<=450:
                continue
            user = Account.objects.get(id=item['owner'])
            for wb in user.ownweibo.order_by("-created_at").all()[:5]:
                logging.info(wb.text)
                logging.info(self.extract(re.sub(u'@.*?[:\s]', '', wb.text)))
                raw_input()

def tpr_test(fdir):
    model = du.load_tpr_model(u'%s/result.txt' % fdir)
    job = WordExtract(model)
    job.test()


def lda_test(fdir, ntopics):
    model = du.load_lda_model(fdir, ntopics)
    job = WordExtract(model)
    job.test()



if __name__ == '__main__':
    tpr_test(sys.argv[1])
    lda_test(sys.argv[1], int(sys.argv[2]))

