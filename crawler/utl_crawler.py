# !/usr/bin/python
# -*- coding: utf-8 -*-

'''
Weibo User Timeline Crawler

Created on Aug 29, 2013
@author: plex
'''
from djangodb.WeiboDao import WeiboDao
from djangodb.CommentDao import CommentDao
from main import Config
from libweibo import weibo

_api = Config.WEIBO_API_GGZZ
wclient = weibo.APIClient(app_key = _api['app_key'],
                       app_secret = _api['app_secret'],
                     redirect_uri = _api['callback_url'])
wclient.set_access_token(
        _api['default_access_token'],
        _api['default_token_expire'])

from ReadWeibo.account.models import Account
from ReadWeibo.mainapp.models import Weibo
from datetime import datetime, timedelta
from time import sleep
import traceback
import logging

_request_interval = 4.5 # secodes


def fetch_user_timeline(w_uid, append=True, max_count=1000, max_interval=100):
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


