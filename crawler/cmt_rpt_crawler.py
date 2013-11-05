# !/usr/bin/python
# -*- coding: utf-8 -*-
'''
Weibo Comments and repots crawler

Created on 2013-10-8
@author: plex
'''
from ReadWeibo.mainapp.models import Category, Weibo
from ReadWeibo.account.models import Account
from djangodb.WeiboDao import WeiboDao
from djangodb.CommentDao import CommentDao
from libweibo import weibo
from main import Config

from django.db.models import F
from datetime import datetime, timedelta
import logging
import time

# use ggzz's app key and auth
wclient = weibo.APIClient(app_key = '3233912973',
                       app_secret = '289ae4ee3da84d8c4c359312dc2ca17d')
wclient.set_access_token(u'2.00l9nr_DfUKrWDf655d3279arZgVvD', u'1539839324')

_request_interval = 4.5 # secodes

def crawl_cmt_repost(category_id, update_interval=timedelta(days=2), sleep_interval=3600*2):
    ''' crawl weibo comments and reposts in category '''

    try:
        category = Category.objects.get(category_id=category_id)
    except Exception:
        logging.warn('Category not found:%s' % category)
        return
    else:
        logging.info('Start crawling comments in category: %s' % category)

    while True:
        start = time.time()
        target_users = Account.objects.filter(real_category=category_id)

        logging.info('There are %d users in category:%s' % (len(target_users), category))
        for user in target_users:
            # fetched weibo that needs update comments and reposts
            weibos = user.ownweibo.filter(created_at__lt=datetime.now()-update_interval).\
                    filter(last_update_cmt_repost__lt=F('created_at')+ update_interval)

            logging.info('%d weibo from %s ' % (len(weibos), user))

            for weibo in weibos:
                cmt_fetched = fetch_comments(weibo, min_time=weibo.last_update_cmt_repost)
                repost_fetched = fetch_reposts(weibo, min_time=weibo.last_update_cmt_repost)
                weibo.last_update_cmt_repost = datetime.now()
                weibo.save()

        end = time.time()
        logging.info('crawl comments and resposts one round time: %d seconds' % int(end-start))
        sleep_len = sleep_interval - (end-start)
        if sleep_len>0:
            logging.info('sleep for %d minutes' % int(sleep_len/60))
            time.sleep(sleep_len)
        else:
            logging.info('No need for sleep')

def fetch_comments(weibo, min_time, max_count=1000):
    ''' fetch comments of a weibo'''

    logging.info('Start fetching comments of %s' % weibo)

    page_id = 1; page_size = 100; tot_fetched = 0; over = False
    while not over:
        result = wclient.get.comments__show(id=weibo.w_id,
                                            count=page_size,
                                            page=page_id)
        time.sleep(_request_interval)
        if not result or not result[u'comments']:
            logging.info('No comments found')
            break

        for cmt_json in result[u'comments']:
            try:
                cmt = CommentDao.create_or_update(cmt_json)
                logging.info('Fetched new comments:%s' % cmt)
                if cmt.created_at<min_time:
                    over = True
                    break
            except Exception, e:
                logging.warn('Fail to parsing comment: %s' % cmt_json)
                logging.exception(e)
            else:
                tot_fetched += 1

        if tot_fetched>max_count or over:
            break
        else:
            page_id += 1

    logging.info('Fetch over %s\'s comments with %d new' % (weibo, tot_fetched))
    return tot_fetched

def fetch_reposts(weibo, min_time, max_count=1000):
    ''' fetch resposts of a weibo'''

    page_id = 1; page_size = 200; tot_fetched = 0; over = False
    while not over:
        result = wclient.get.statuses__repost_timeline(id=weibo.w_id,
                                                        count=page_size,
                                                        page=page_id)
        time.sleep(_request_interval)
        if not result or not result[u'reposts']:
            logging.info('No reposts found: %s' % result)
            break

        for repost_json in result[u'reposts']:
            try:
                repost = WeiboDao.create_or_update(repost_json)
                logging.info('Fetched new repost:%s' % repost)
                if repost.created_at<min_time:
                    over = True
                    break
            except Exception, e:
                logging.warn('Fail to parsing repost: %s' % repost_json)
                logging.exception(e)
            else:
                tot_fetched += 1

        if tot_fetched>max_count or over:
            break
        else:
            page_id += 1

    logging.info('Fetch over %s\'s reposts with %d new' % (weibo, tot_fetched))
    return tot_fetched

if __name__ == '__main__':
    crawl_cmt_repost(category_id=1)
