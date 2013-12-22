# !/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2013-11-3

@author: plex
'''

from ReadWeibo.mainapp.models import Weibo, Category
from ReadWeibo.account.models import Account
from main import Config
from ranking import DataUtil as du
from ranking.ManifoldRank import ManifoldRank
from libweibo import weibo

from time import sleep
import traceback
import datetime
import logging

master = Account.objects.get(w_uid=3887027625) #underfitting
target_category = Category.objects.get(category_id=1)

wclient = weibo.APIClient(app_key = Config.WEIBO_API['app_key'],
                       app_secret = Config.WEIBO_API['app_secret'],
                     redirect_uri = Config.WEIBO_API['callback_url'])
wclient.set_access_token(master.oauth.access_token, master.oauth.expires_in)

def rank():
    G = du.gen_graph(save_path=None, max_cnt=500)
    mr = ManifoldRank(G)
    mr.rank()
    mr.classify(update=True)

def follow_others():

    users_to_follow = Account.objects.order_by("-relevance")[:10]

    logging.info(u'Start following others(%d)' % len(users_to_follow))

    for user in users_to_follow:
        if user in master.friends.all():
            logging.info(u'already following %s' % user)
            continue
        try:
            wclient.post.friendships__create(uid=user.w_uid)
        except weibo.APIError, e:
            logging.warn(u'fail to follow %s' % user)
            logging.error(u'weibo.APIError %s:%s' % (e.error_code, e.error))
            logging.info(u'sleep for 12 hours')
            sleep(60*60*12)
        else:
            master.friends.add(user)
            master.save() # if necessary?
            logging.info(u'follow up %s' % user)
            sleep(120) # every two minutes

if __name__=='__main__':
    while True:
        rank()
        sleep(3636)

    #follow_others()
