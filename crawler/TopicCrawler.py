# !/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2013-10-8

@author: plex
'''
from ReadWeibo.mainapp.models import Category, Weibo
from ReadWeibo.account.models import Account
from crawler import WeiboFetcher
from main import Config

from django.db.models import F
from datetime import datetime, timedelta
import logging
import time
import thread

def crawl_user_timeline(w_uid, sleep_interval=3600):
    ''' crawl user timeline '''

    user = Account.objects.get(w_uid=w_uid)
    logging.info('Start crawling %s\'s home timeline ' % user)
    if not user:
        logging.warn('User not found:%s' % user)
        return

    while True:

        start = time.time()
        WeiboFetcher.FetchHomeTimeline(w_uid) # crawl user home timeline
        end = time.time()

        sleep_len = sleep_interval - (end-start)
        logging.info('crawl user timeline one round time: %d seconds' % int(end-start))
        if sleep_len>0:
            logging.info('sleep for %d minutes' % int(sleep_len/60))
            time.sleep(sleep_len)
        else:
            logging.info('No need for sleep')

def crawl_comments(category_id, max_time=datetime.now()-timedelta(days=2), sleep_interval=3600*2):
    ''' crawl weibo comments in category '''

    category = Category.objects.get(category_id=category_id)
    logging.info('Start crawling comments in category: %s' % category)
    if not category:
        logging.warn('Category not found:%s' % category)
        return

    while True:
        start = time.time()
        target_users = Account.objects.filter(real_category=category_id)

        logging.info('There are %d users in category:%s' % (len(target_users), category))
        for user in target_users:

            weibos = user.ownweibo.filter(created_at__lt=max_time).\
                    filter(last_update_comments__lt=F('created_at')+ timedelta(days=1))

            logging.info('%d weibo from %s ' % (len(weibos), user))

            for weibo in weibos:
                WeiboFetcher.FetchComments(w_id=weibo.w_id)

        end = time.time()
        logging.info('crawl comments one round time: %d seconds' % int(end-start))
        sleep_len = sleep_interval - (end-start)
        if sleep_len>0:
            logging.info('sleep for %d minutes' % int(sleep_len/60))
            time.sleep(sleep_len)
        else:
            logging.info('No need for sleep')

if __name__ == '__main__':
    crawl_user_timeline(w_uid=1698863684)
    #crawl_comments(category_id=1, max_time=datetime.now()-timedelta(days=4))
