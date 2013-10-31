# !/usr/bin/python
# -*- coding: utf-8 -*-

'''
Weibo Crawler

Created on Aug 29, 2013
@author: plex
'''
from djangodb.WeiboDao import WeiboDao
from djangodb.CommentDao import CommentDao
from main import Config
from libweibo import weibo

WEIBO_API = Config.WEIBO_API_GGZZ
wclient = weibo.APIClient(app_key = WEIBO_API['app_key'],
                       app_secret = WEIBO_API['app_secret'],
                     redirect_uri = WEIBO_API['callback_url'])
wclient.set_access_token(
        WEIBO_API['default_access_token'],
        WEIBO_API['default_token_expire'])

from ReadWeibo.account.models import Account
from ReadWeibo.mainapp.models import Weibo
from datetime import datetime, timedelta
from time import sleep
import traceback
import logging

_request_interval = 4.5 # secodes

def FetchUserTimeline(w_uid, append=True, max_count=1000, max_interval=100):
    '''
    获取当前用户所发布的微博，需要授权
    '''
    try:
        user = Account.objects.get(w_uid=w_uid)
    except Exception:
        logging.error('no user found for id:%s' % w_uid)
        return

    if user.oauth and not user.oauth.is_expired():
        wclient.set_access_token(user.oauth.access_token, user.oauth.expires_in)
    else:
        logging.warn('OAuth(%s) Expired for %s' % (user.oauth, user))
        return

    if not user.need_update_utl():
        logging.info('No need to update user time line for %s (last update time: %s)'
                    % (user, user.last_update_utl))
        return

    tot_fetched = 0; page_size = 100; page_id = 1; over = False
    trim_user = 1 #返回值中user字段开关，0：返回完整user字段、1：user字段仅返回user_id，默认为0
    while not over:
        result = wclient.get.statuses__user_timeline(uid=w_uid,
                                                    count=page_size,
                                                    page = page_id,
                                                    trim_user=trim_user)
        if not result or not result['statuses']: #over
            logging.info('No more statuses in %s\'s timeline, total updated %d'
                         % (user, tot_fetched))
            break

        for status in result['statuses']:
            try:
                weibo = WeiboDao.create_or_update(status)
                logging.info('Fetched new status:%s' % weibo)
                if weibo.created_at < user.last_update_utl:
                    over = True
                    break
            except Exception:
                logging.warn('Fail to parse status: %s', status)
                logging.warn(traceback.format_exc())
            else:
                tot_fetched += 1

        if tot_fetched>max_count:
            over = True
        else:
            logging.info('Fetched %d statuses' % tot_fetched)
            page_id += 1
            sleep(_request_interval)

    if tot_fetched>0 or over:
        logging.info('Fetch over UserTimeLine for %s with %d new' % (user, tot_fetched))
        user.last_update_utl = datetime.now()
        user.save()
    else:
        logging.warn('No new statuses found in %s time line' % user)

def FetchComments(w_id, min_time, max_count=1000):
    ''' fetch comments of a status'''

    try:
        status = Weibo.objects.get(w_id=w_id)
    except Exception:
        logging.error('no status found for %s' % w_id)
        return
    else:
        logging.info('Start fetching comments of %s' % status)

    page_id = 1; page_size = 100; tot_fetched = 0; over = False
    while not over:
        result = wclient.get.comments__show(id=w_id,
                                            count=page_size,
                                            page=page_id)
        sleep(_request_interval)
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
            except Exception:
                logging.warn('Fail to parsing comment: %s' % cmt_json)
                logging.warn(traceback.format_exc())
            else:
                tot_fetched += 1

        if tot_fetched>max_count or over:
            break
        else:
            page_id += 1

    logging.info('Fetch over %s\'s comments with %d new' % (status, tot_fetched))
    return tot_fetched

def FetchReposts(w_id, min_time, max_count=1000):
    ''' fetch resposts of a status'''

    try:
        status = Weibo.objects.get(w_id=w_id)
    except Exception:
        logging.error('no status found for %s' % w_id)
        return
    else:
        logging.info('Start fetching reposts of %s' % status)

    page_id = 1; page_size = 200; tot_fetched = 0; over = False
    while not over:
        result = wclient.get.statuses__repost_timeline(id=w_id,
                                                        count=page_size,
                                                        page=page_id)
        sleep(_request_interval)
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
            except Exception:
                logging.warn('Fail to parsing repost: %s' % repost_json)
                logging.warn(traceback.format_exc())
            else:
                tot_fetched += 1

        if tot_fetched>max_count or over:
            break
        else:
            page_id += 1

    logging.info('Fetch over %s\'s reposts with %d new' % (status, tot_fetched))
    return tot_fetched

def FetchHomeTimeline(w_uid, max_count=5000):
    try:
        user = Account.objects.get(w_uid=w_uid)
    except Exception:
        logging.error('no user found for id:%s' % w_uid)
        return
    if not user.oauth or user.oauth.is_expired():
        logging.warn('OAuth(%s) Expired for %s' % (user.oauth, user))
        return
    else:
        wclient.set_access_token(user.oauth.access_token, user.oauth.expires_in)

    logging.info("Start fetching HomeTimeline for %s" % user)

    tot_fetched = 0; page_id = 1; page_size = 200; over=False
    while not over:
        result = wclient.get.statuses__home_timeline(uid=w_uid,
                                                    count=page_size,
                                                    page=page_id)
        sleep(_request_interval)
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
            except Exception:
                logging.warn("Fail to parse status: %s" % status)
                logging.warn(traceback.format_exc())
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

