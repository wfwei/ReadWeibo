# !/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on Oct 12, 2012

@author: plex
'''

from django.db import models

from ReadWeibo.account.models import Account
from datetime import datetime

class Category(models.Model):

    category_id = models.BigIntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=10, blank=True)
    keywords = models.TextField(blank=True)
    model = models.TextField(blank=True)

    def __unicode__(self):
        return u'{type:category, category_id:%s, name:%s}' % (self.category_id, self.name)

class Weibo(models.Model):

    created_at = models.DateTimeField(default=datetime.now, db_index=True)
    fetched_at = models.DateTimeField(default=datetime.now, db_index=True)
    w_id = models.BigIntegerField(unique=True, db_index=True)
    text = models.CharField(max_length=500, blank=True)
    source = models.CharField(max_length=500, blank=True)
    thumbnail_pic = models.CharField(max_length=500, blank=True)
    bmiddle_pic = models.CharField(max_length=500, blank=True)
    original_pic = models.CharField(max_length=500, blank=True)
    reposts_count = models.IntegerField(default=0, blank=True)
    comments_count = models.IntegerField(default=0, blank=True)
    attitudes_count =  models.IntegerField(default=0, blank=True)
    retweeted_status = models.ForeignKey("self", related_name='retweet_status', blank=True, null=True)

    predict_category = models.IntegerField(default=0, blank=True)
    real_category  =  models.IntegerField(default=0, blank=True)

    owner = models.ForeignKey(Account, related_name='ownweibo', blank=True, null=True, on_delete=models.SET_NULL) #owner
    watcher = models.ManyToManyField(Account, related_name='watchweibo', blank=True, null=True) # TODO REMOVE who can see this

    # last update comments
    last_update_comments = models.DateTimeField(default='1000-09-04 19:01:08')

    def need_update_comments(self):
        # 微博刚发布或更新不久的，不急于更新评论
        return (datetime.now()-self.last_update_comments).seconds > 10000 # more than 2 hours

    def __unicode__(self):
        return u'{type:weibo, w_id:%s}' % self.w_id

    class Meta:
        ordering = ["-w_id"]


class Comment(models.Model):

    created_at = models.DateTimeField(default=datetime.now, db_index=True)
    fetched_at = models.DateTimeField(default=datetime.now, db_index=True)
    c_id = models.BigIntegerField(unique=True, db_index=True)
    text = models.CharField(max_length=500, blank=True)
    source = models.CharField(max_length=500, blank=True)

    owner = models.ForeignKey(Account, related_name='owncomments', blank=True, null=True) #owner
    commented_status = models.ForeignKey(Weibo, related_name='comments', blank=True, null=True)
    reply_comment = models.ForeignKey("self", related_name='replied_comments', blank=True, null=True)

    def __unicode__(self):
        return u'{type:comments, c_id:%s}' % self.c_id

    class Meta:
        ordering = ["-c_id"]

