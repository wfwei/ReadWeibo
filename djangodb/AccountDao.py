'''
Created on 2013-10-18

@author: plex
'''
from ReadWeibo.account.models import Account
from ReadWeibo.mainapp.models import Weibo, Comment
from datetime import datetime

class AccountDao:

    @staticmethod
    def create_or_update(weiboUserJson):

        uinfo=weiboUserJson
        account, created = Account.objects.get_or_create(w_uid=uinfo[u'id'])

        if created:
            account.w_name=uinfo['name']
            account.w_province=uinfo['province']
            account.w_city=uinfo['city']
            account.w_location=uinfo['location']
            account.w_url=uinfo['url']
            account.w_description=uinfo['description']
            account.w_profile_image=uinfo['profile_image_url']
            account.w_gender=uinfo['gender']
            account.w_created_at=datetime.strptime(uinfo['created_at'], "%a %b %d %H:%M:%S +0800 %Y")

        account.w_followers_count=uinfo['followers_count']
        account.w_friends_count=uinfo['friends_count']
        account.w_statuses_count=uinfo['statuses_count']
        account.w_favourites_count=uinfo['favourites_count']
        account.w_bi_followers_count=uinfo['bi_followers_count']
        account.w_verified=uinfo['verified']
        account.fetched_at=datetime.now()
        account.save()

        return account
