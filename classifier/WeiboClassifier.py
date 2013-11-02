# !/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2013-10-8
@author: plex
'''

from ReadWeibo.account.models import Account
from ReadWeibo.mainapp.models import Category
from crawler import UserFetcher, TopicCrawler

import sys
import logging
import thread
import jieba

class WeiboClassifer():
    ''' classify weibo'''

    def __init__(self, category_id):
        pass

    def auto_label_weibo(self):

        logging.info('Start auto labeling weibos watched by %s' % self.user)

        offset=0; page_size=100; cnt=0
        while True:
            wbs = self.user.watchweibo.filter(predict_category=0)[offset:offset+page_size]

            if not wbs : break # Over

            logging.info('Get %d weibo to auto-label' % len(wbs))
            for wb in wbs:
                wb.predict_category = 0 # reset
                found_words = []
                for word in jieba.cut(wb.text.lower()):
                    if len(word)>3 and word in self.keyword_set:
                        found_words.append(word)
                    if len(found_words)>2:
                        logging.info(u'Predicting %s belongs to %s by words:%s' % (wb, self.category, ','.join( wd for wd in found_words)))
                        wb.predict_category = self.category_id
                        cnt += 1
                        break
                wb.save()
            offset += page_size

        logging.info('Auto Labeled %d weibo in %s' % (cnt, self.category))

    def learn(self):
        logging.warn('Not implemented yet...')
        pass

if __name__ == '__main__':
    pass

