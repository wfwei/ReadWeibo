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
        return ' '.join([item[0].encode('utf-8') for item in sorted_r])

    def test(self):
        for user in Account.objects.filter(exp=1):
            for wb in user.ownweibo.order_by("-created_at").filter(retweeted_status__exact=None)[:2]:
                text = re.sub("@[^\s@:]+", "", wb.text)
                text = re.sub(u"http://t.cn[^ ]*", u"", text)
                text = re.sub(u"\[[^ ]{1,3}\]", u"", text)
                wb.keywords = self.extract(text)
                wb.save()
                logging.info(wb.text)
                logging.info(wb.keywords)

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
    #lda_test(sys.argv[1], int(sys.argv[2]))

