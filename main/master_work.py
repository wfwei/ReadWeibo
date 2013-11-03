# !/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2013-11-3

@author: plex
'''

from django.db.models import Q

from ReadWeibo.mainapp.models import Weibo, Category
from ReadWeibo.account.models import Account
from libweibo import weibo
from main import Config

from time import sleep
import traceback
import datetime
import logging

master = Account.objects.get(w_uid=3887027625) #underfitting
target_category = Category.objects.get(category_id=1)

wclient = weibo.APIClient(app_key=Config.weibo_app_key,
                    app_secret = Config.weibo_app_secret,
                    redirect_uri = Config.callback_url)
wclient.set_access_token(master.oauth.access_token, master.oauth.expires_in)

def follow_others():

    users_to_follow = Account.objects.filter(predict_category=target_category.category_id)

    logging.info(u'Start following others(%d)' % len(users_to_follow))

    for user in users_to_follow:
        if user in master.friends.all():
            logging.info(u'already following %s' % user)
            continue
        try:
            wclient.post.friendships__create(uid=user.w_uid)
        except weibo.APIError, e:
            logging.warn(u'fail to follow %s' % user)
            if e.error_code == 10024:
                logging.info(u'sleep for an hour')
                sleep(60*60)
            else:
                logging.error(traceback.format_exc())
                break
        else:
            master.friends.add(user)
            master.save() # if necessary?
            logging.info(u'follow up %s' % user)
            sleep(60) # every minute

if __name__=='__main__':
    follow_others()
