# !/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2013-10-8

@author: plex
'''

from ReadWeibo.mainapp.models import Category, Weibo
from ReadWeibo.account.models import Account
from djangodb.WeiboDao import WeiboDao
from libweibo import weibo
from main import Config

from django.db.models import F
from datetime import datetime, timedelta
import logging
import time


wclient = weibo.APIClient(app_key = Config.WEIBO_API['app_key'],
                       app_secret = Config.WEIBO_API['app_secret'],
                     redirect_uri = Config.WEIBO_API['callback_url'])

_request_interval = 4

def crawl_home_timeline(w_uid, sleep_interval=3600):
    ''' crawl user timeline '''

    while True:

        start = time.time()
        fetch_home_timeline(w_uid)
        end = time.time()

        sleep_len = sleep_interval - (end-start)
        logging.info('crawl user timeline one round time: %d seconds' % int(end-start))
        if sleep_len>0:
            logging.info('sleep for %d minutes' % int(sleep_len/60))
            time.sleep(sleep_len)
        else:
            logging.info('No need for sleep')

def fetch_home_timeline(w_uid, max_count=5000):

    try:
        user = Account.objects.get(w_uid=w_uid)
    except Exception:
        logging.warn('User not found:%s' % user)
        return
    else:
        logging.info('Start fetching %s\'s home timeline ' % user)


    if not user.oauth or user.oauth.is_expired():
        logging.warn('OAuth(%s) Expired for %s' % (user.oauth, user))
        return
    else:
        logging.info(user.oauth.access_token)
        wclient.set_access_token(user.oauth.access_token, user.oauth.expires_in)

    logging.info("Start fetching HomeTimeline for %s" % user)

    tot_fetched = 0; page_id = 1; page_size = 200; over=False
    while not over:
        result = wclient.get.statuses__home_timeline(uid=user.w_uid,
                                                    count=page_size,
                                                    page=page_id)
        time.sleep(_request_interval)
        if not result or not result[u'statuses']:
            logging.info('No more statuses in %s\'s home time line, total updated %d'
                         % (user, tot_fetched))
            break

        for status in result[u'statuses']:
            try:
                wb = WeiboDao.create_or_update(status)
                wb.watcher.add(user)
                wb.save()
                logging.info('Fetch new status: %s' % wb)
                if wb.created_at<=user.last_update_htl:
                    over = True
                    break
            except Exception, e:
                logging.warn("Fail to parse status: %s" % status)
                logging.exception(e)
            else:
                tot_fetched += 1

        if tot_fetched >= max_count or over:
            over = True
        else:
            logging.info('Fetched %d statuses' % tot_fetched)
            page_id += 1

    if tot_fetched>0:
        logging.info('Fetch over HomeTimeline for  %s Over with %d new' % (user, tot_fetched))
        user.last_update_htl = datetime.now()
        user.save()
    else:
        logging.warn('No new statuses found in %s home time line' % user)


if __name__ == '__main__':
    w_uid = 3887027625 # 1698863684
    fetch_home_timeline(w_uid)
    #crawl_home_timeline(w_uid)
