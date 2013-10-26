# !/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2013-10-8

@author: plex
'''
from ReadWeibo.mainapp.models import Category, Weibo
from ReadWeibo.account.models import Account
from crawler import WeiboFetcher

from datetime import datetime, timedelta
from main import Config
import logging
import time

mcui = timedelta(days=100) #max_comments_update_interval

def crawl_by_user(w_uid, category_id, min_interval=3600):
    user = Account.objects.get(w_uid=w_uid)
    category = Category.objects.get(category_id=category_id)
    logging.info('Start crawling %s in %s' % (user, category))
    if not user or not category:
        logging.warn('User or Category not found (%s, %s)' % (user, category))
        return
    while True:
        start = time.time()
        # crawl user home timeline
        logging.info('Start fetching home time line of %s' % user)
        WeiboFetcher.FetchHomeTimeline(w_uid)
        # crawl comments of weibo(in this category)
        weibos = Weibo.objects.filter(real_category=category_id).filter(created_at__gt=datetime.now()-mcui)
        logging.info('There are %d statues in this category that needs updating comments' % len(weibos))
        for weibo in weibos:
            logging.info('Prepare to crawl %s \'s comments' % weibo)
            WeiboFetcher.FetchComments(w_id=weibo.w_id)
            time.sleep(1)
        end = time.time()

        sleep_len = min_interval - (end-start)
        logging.info('crawl by user one round time: %d seconds' % int(end-start))
        if sleep_len>0:
            logging.info('sleep for %d minutes' % int(10000/60))
            time.sleep(sleep_len)
        else:
            logging.info('No need for sleep')

if __name__ == '__main__':
    crawl_by_user(1698863684, 1)
