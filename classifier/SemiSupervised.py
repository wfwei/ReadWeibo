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

class UserClassifer():

    def __init__(self, from_uid, category_id):
        self.uid = from_uid
        self.user = Account.objects.get(w_uid=from_uid)
        self.category_id = category_id
        self.category = Category.objects.get(category_id=category_id)
        self.keyword_set = set()
        for keyword in self.category.keywords.split():
            logging.info('Adding %s to %s' % (keyword, self.category))
            self.keyword_set.add(keyword)
        logging.info('Init UserClassifier Over, with %d keywords imported in category %s'
                    % (len(self.keyword_set), self.category))

    def auto_lable_user(self):
        logging.info('Start auto labeling user friend %s' % self.user)
        cnt = 0
        for friend in self.user.friends.all():
            friend.predict_category = 0 # reset predict category
            desc = friend.w_description + friend.w_name
            logging.info(u'Predicting %s -- %s' % (friend, desc))
            for word in jieba.cut(desc.lower()):
                if word in self.keyword_set:
                    logging.info(u'%s Predicting %s belongs to %s' % (cnt, friend, self.category))
                    friend.predict_category = self.category_id
                    cnt += 1
                    break
            friend.save()
        logging.info('Auto Labeled %d new user in %s' % (cnt, self.category))

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
    user_work = UserClassifer(from_uid=1698863684, category_id=1)
    # user_work.auto_lable_user()
    user_work.auto_label_weibo()
    # user_work.learn()
    pass

