# !/usr/bin/python
# -*- coding: utf-8 -*-

'''
Weibo User Timeline Crawler

Created on Aug 29, 2013
@author: plex
'''
from ReadWeibo.account.models import Account
from ReadWeibo.mainapp.models import Weibo
from djangodb.CommentDao import CommentDao
from djangodb.WeiboDao import WeiboDao
from django.db.models import Count
from libweibo import weibo
from main import Config
from datetime import datetime, timedelta
from time import sleep
import traceback
import logging

wclient = weibo.APIClient(app_key = '3826768764',
                       app_secret = '7eb7e1c82280f31db8db14cbd0895505',
                       redirect_uri = 'http://42.121.117.9/atRec/callback.jsp')
wclient.set_access_token('2.00b6R5mBq3jyKE94bbf64dc40Z6k1J', '1394823602435')

_request_interval = 1.5 # secodes

def fetch_user_timeline(w_uid, append=True, max_count=1000):
    '''
    获取当前用户所发布的微博，需要授权
    '''
    try:
        user = Account.objects.get(w_uid=w_uid)
    except Exception:
        logging.error('no user found for id:%s' % w_uid)
        return

    #if user.oauth and not user.oauth.is_expired():
    #    wclient.set_access_token(user.oauth.access_token, user.oauth.expires_in)
    #else:
    #    logging.warn('OAuth(%s) Expired for %s' % (user.oauth, user))
    #    return

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

if __name__ == '__main__':
    for item in Weibo.objects.values('owner').annotate(cnt=Count('owner')):
        if item['cnt']>20:
            u = Account.objects.get(id=item['owner'])
            logging.info('fetching %s' % u)
            try:
                fetch_user_timeline(u.w_uid, append=True, max_count=1000)
            except Exception, e:
                logging.exception(e)
    pass
