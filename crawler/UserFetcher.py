# !/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2013-10-7

@author: plex
'''
from ReadWeibo.account.models import Account
from djangodb.AccountDao import AccountDao
from libweibo import weibo
from main import Config

from datetime import datetime
from time import sleep
import logging

wclient = weibo.APIClient(app_key = Config.WEIBO_API['app_key'],
                       app_secret = Config.WEIBO_API['app_secret'],
                     redirect_uri = Config.WEIBO_API['callback_url'])

def FetchFriends(w_uid, max_count=500):
	'''
	抓取当前用户的friends列表，需要用户授权，默认抓取最新的500的好友
	'''

	user = Account.objects.get(w_uid=w_uid)

	if not user.need_update_fri():
		logging.info('No need to update friend list for %s (last update time: %s)'
					% (user, user.last_update_fri))
		return

	if user.oauth.is_expired():
		logging.warn('OAuth(%s) Expired for %s' % (user.oauth, user))
		return
	else:
		wclient.set_access_token(user.oauth.access_token, user.oauth.expires_in)

	page_size = 200 # fast the fist time
	cursor = 0 # 返回结果的游标，下一页用返回值里的next_cursor，上一页用previous_cursor，默认为0。
	trim_status = 1 # 0：返回完整status字段、1：status字段仅返回status_id，默认为1。
	while True:
		friends = wclient.get.friendships__friends(uid=w_uid,
		                                    count=page_size,
		                                    cursor=cursor,
		                                    trim_status=trim_status)
		if not friends or not friends['users']:
			logging.info('No more friends for %s, total fetched %d ' % (user, cursor))
			break # over
		for friend in friends['users']:
			try:
				friend_acc = AccountDao.create_or_update(friend)
				if friend_acc.is_zombie():
					logging.info('zombie user:%s' % friend_acc)
					friend_acc.delete()
				else:
					logging.info('new friend:%s' % friend_acc)
					user.friends.add(friend_acc)
			except Exception, e:
				logging.warn('Fail to parse friend:%s', friend)
                logging.exception(e)
		user.save()
		cursor = int(friends['next_cursor'])

		logging.info('Fetched %d friends' % cursor)
		if cursor>max_count or cursor==0:
			break
		else:
			sleep(0.5)

	user.last_update_fri = datetime.now()
	user.save()

def FetchFollowers(w_uid, max_count=1000):
	'''
	抓取当前用户的friends列表，需要用户授权，默认抓取最新的500的好友 TODO 貌似只能爬取一部分？？
	'''

	user = Account.objects.get(w_uid=w_uid)

	if not user.need_update_fol():
		logging.info('No need to update follower list for %s (last update time: %s)'
					% (user, user.last_update_fol))
		return

	if user.oauth.is_expired():
		logging.warn('OAuth(%s) Expired for %s' % (user.oauth, user))
		return
	else:
		wclient.set_access_token(user.oauth.access_token, user.oauth.expires_in)

	page_size = 200
	cursor = 0 # 返回结果的游标，下一页用返回值里的next_cursor，上一页用previous_cursor，默认为0。
	trim_status = 1 # 0：返回完整status字段、1：status字段仅返回status_id，默认为1。
	while True:
		followers = wclient.get.friendships__followers(uid=w_uid,
		                                    count=page_size,
		                                    cursor=cursor,
		                                    trim_status=trim_status)
		if not followers or not followers['users']:
			logging.info('No more followers for %s, total fetched %d ' % (user, cursor))
			break # over
		for follower in followers['users']:
			try:
				follower_acc = AccountDao.create_or_update(follower)
				if follower_acc.is_zombie():
					logging.info('zombie user:%s' % follower_acc)
					follower_acc.delete()
				else:
					logging.info('new user:%s' % follower_acc)
					follower_acc.friends.add(user)
					follower_acc.save()
			except Exception, e:
				logging.warn('Fail to parse follower:%s', follower)
                logging.exception(e)
		cursor = int(followers['next_cursor'])

		logging.info('Fetched %d followers' % cursor)
		if cursor>max_count or cursor==0:
			break;
		else:
			sleep(0.5)

	user.last_update_fol = datetime.now()
	user.save()


if __name__ == '__main__':
	FetchFriends(w_uid=1698863684)
# 	FetchFollowers(w_uid=1698863684)
