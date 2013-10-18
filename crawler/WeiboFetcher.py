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
wclient = weibo.APIClient(app_key=Config.weibo_app_key,
                    app_secret = Config.weibo_app_secret,
                    redirect_uri = Config.callback_url)
wclient.set_access_token(Config.default_access_token, Config.default_access_token_expires_in)

from ReadWeibo.account.models import Account
from ReadWeibo.mainapp.models import Weibo
from datetime import datetime, timedelta
from time import sleep
import traceback
import logging

def FetchUserTimeline(w_uid, append=True, max_count=1000, max_interval=100):
	'''
	获取当前用户所发布的微博，需要授权
	'''
	user = Account.objects.get(w_uid=w_uid)
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
		result = wclient.get.statuses__user_timeline(
																			uid=w_uid, 
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
	
	if tot_fetched>0 or over:
		logging.info('Crawl over UserTimeLine for %s with %d new' % (user, tot_fetched))
		user.last_update_utl = datetime.now()
		user.save()
	else:
		logging.warn('No new statuses found in %s time line' % user)
		

def FetchComments(w_id, max_count=1000):
	status = Weibo.objects.get(w_id=w_id)
	if not status:
		logging.error('no status found for %s' % w_id)
		return 
	if not status.need_update_comments():
		logging.info('Update comments recently, skip in this round')
		return
	
	page_id = 1; page_size = 100; 	tot_fetched = 0; over = False
	while not over:
		comments = wclient.get.comments__show(
																		id=w_id, 
																		count=page_size, 
																		page=page_id)
		if not comments or not comments[u'comments']:
			logging.info('No comments found')
			break
		
		for comment in comments[u'comments']:
			try:
				cmt = CommentDao.create_or_update(comment)
				logging.info('Fetched new comments:%s' % cmt)
				if cmt.created_at<status.last_update_comments:
					over = True
					break
			except Exception:
				logging.warn('Fail to parsing comment: %s', comment)
				logging.warn(traceback.format_exc())
			else:
				tot_fetched += 1
				
		if tot_fetched>max_count or over:
			logging.info('Crawl over %s\'s comments with %d new' % (status, tot_fetched))
			break
		else:
			page_id += 1
	
	if tot_fetched>0:
		logging.info('Crawl over Comments for  %s Over with %d new' % (status, tot_fetched))
		status.last_update_comments = datetime.now()
		status.save()
	else:
		logging.warn('No new comments found for %s' % status)
			
def FetchHomeTimeline(w_uid, max_count=5000):
	user = Account.objects.get(w_uid=w_uid)
	if not user.oauth or user.oauth.is_expired():
		logging.warn('OAuth(%s) Expired for %s' % (user.oauth, user))
		return
	else:
		wclient.set_access_token(user.oauth.access_token, user.oauth.expires_in)

	logging.info("Start crawling HomeTimeline for %s" % user)
	
	tot_fetched = 0;	page_id = 1; page_size = 200; over=False
	while not over:
		result = wclient.get.statuses__home_timeline(uid=w_uid,
                                        count=page_size,
                                        page=page_id)
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
			sleep(0.5)

	if tot_fetched>0:
		logging.info('Crawl over HomeTimeline for  %s Over with %d new' % (user, tot_fetched))
		user.last_update_htl = datetime.now()
		user.save()
	else:
		logging.warn('No new statuses found in %s home time line' % user)

if __name__ == '__main__':
# 	FetchHomeTimeline(1698863684)
# 	FetchUserTimeline(1698863684)
	FetchComments(3633787348598149)

