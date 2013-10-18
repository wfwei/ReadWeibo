'''
Created on 2013-10-18

@author: plex
'''

from ReadWeibo.account.models import Account
from ReadWeibo.mainapp.models import Weibo, Comment
from datetime import datetime
from djangodb.AccountDao import AccountDao

class WeiboDao:

    @staticmethod
    def create_or_update(weiboJson):
        status = weiboJson
        wb, created = Weibo.objects.get_or_create(w_id=status[u'id'])

        if created:
            if status[u'created_at']:
                wb.created_at = datetime.strptime(status[u'created_at'], "%a %b %d %H:%M:%S +0800 %Y")
            wb.text = status[u'text']

            if u'source' in status:
                wb.source = status[u'source']

            if u'thumbnail_pic' in status:
                wb.thumbnail_pic = status[u'thumbnail_pic']
            if u'bmiddle_pic' in status:
                wb.bmiddle_pic = status[u'bmiddle_pic']
            if u'original_pic' in status:
                wb.original_pic = status[u'original_pic']
            
            if u'user' in status:
                wb.owner = AccountDao.create_or_update(status[u'user'])

            if u'retweeted_status' in status:
                wb.retweeted_status = WeiboDao.create_or_update(status[u'retweeted_status'])


        wb.reposts_count = status[u'reposts_count']
        wb.comments_count = status[u'comments_count']
        wb.attitudes_count = status[u'attitudes_count']
        wb.fetched_at = datetime.now()
        wb.save()

        return wb

    @staticmethod
    def get_weibo(weiboJson):
        status = weiboJson
        wb, created = Weibo.objects.get_or_create(w_id=status[u'id'])

        if created:
            if status[u'created_at']:
                wb.created_at = datetime.strptime(status[u'created_at'], "%a %b %d %H:%M:%S +0800 %Y")
            wb.text = status[u'text']

            if u'source' in status:
                wb.source = status[u'source']

            if u'thumbnail_pic' in status:
                wb.thumbnail_pic = status[u'thumbnail_pic']
            if u'bmiddle_pic' in status:
                wb.bmiddle_pic = status[u'bmiddle_pic']
            if u'original_pic' in status:
                wb.original_pic = status[u'original_pic']

            wb.owner = AccountDao.create_or_update(status[u'user'])

            if u'retweeted_status' in status:
                wb.retweeted_status = WeiboDao.create_or_update(status[u'retweeted_status'])
                wb.retweeted_status.watcher.add(wb.owner)


        wb.reposts_count = status[u'reposts_count']
        wb.comments_count = status[u'comments_count']
        wb.attitudes_count = status[u'attitudes_count']
        wb.fetched_at = datetime.now()
        wb.save()

        return wb
