# !/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2013-10-8
@author: plex
'''

from django.db.models import Count

from ReadWeibo.account.models import Account
from ReadWeibo.mainapp.models import Category, Weibo
from crawler import UserFetcher, TopicCrawler

import sys
import logging
import thread
import jieba

class UserClassifer():
    ''' Classify Users '''

    def __init__(self, category_id):
        self.category_id = category_id
        self.category = Category.objects.get(category_id=category_id)
        self.keyword_set = set()
        for keyword in self.category.keywords.split():
            logging.info('Adding %s to %s' % (keyword, self.category))
            self.keyword_set.add(keyword)
        logging.info('Init UserClassifier Over, with %d keywords imported in category %s'
                    % (len(self.keyword_set), self.category))

    def label_by_desc(self, reset_all=False):
        '''
        Label User By Keywords In Description

        This will find many potential users, but part of them may not be active
        '''

        logging.info('Start labeling users by her/his description')
        page_id=0; page_size = 1000; over = False; cnt = 0

        while not over:

            if reset_all:
                # fetch all users
                users = Account.objects.all()[page_id:page_id+page_size]
            else:
                # Only fetch users have not been predicted before
                users = Account.objects.filter(predict_category=0)[page_id:page_id+page_size]

            logging.info('Fetched %d users for labeling' % len(users))

            if not users or len(users)<page_size:
                over = True
            else:
                page_id += len(users)

            for user in users:
                user.pridict_category = Category.NO_CATEGORY # reset category
                desc = user.w_description + user.w_name
                logging.info(u'%s -- %s' % (user, desc))
                for word in jieba.cut(desc.lower()):
                    # find one keyword, and classify in this category
                    if word in self.keyword_set:
                        logging.info(u'%s Predict %s belongs to %s' % (cnt, user, self.category))
                        user.predict_category = self.category_id
                        cnt += 1
                        break
                user.save()

        logging.info('Labeled %d new user in %s' % (cnt, self.category))

    def label_by_weibo(self, reset_all=False):
        '''
        Label User By Weibos Posted Before

        This method will filter many active user in category
        '''

        logging.info('Start labeling users by her/his weibo')

        if reset_all:
            Account.objects.all().update(predict_category=Category.NO_CATEGORY)
            logging.info('Reset all users\'s predict_category=No_CATEGORY')

        rel_user_cnt= Weibo.objects.filter(real_category=1).values('owner').annotate(cnt=Count('owner')).order_by('-cnt')
        logging.info('There are %d users who have posted weibo in %s' % (len(rel_user_cnt), self.category))

        cnt = 0; limit=4
        for item in rel_user_cnt:
            if item['cnt']<limit: break # TODO consider percentage
            user = Account.objects.get(id=item['owner'])
            user.predict_category = self.category_id
            user.save()
            cnt += 1
            logging.info('%s Predict %s as %s' % (cnt, user, self.category))

        logging.info('Labeled %d new user in %s' % (cnt, self.category))

    def learn(self):
        pass

if __name__ == '__main__':
    classifier = UserClassifer(category_id=1)

    #classifier.label_by_desc(reset_all=True)
    classifier.label_by_weibo(reset_all=True)
    pass

