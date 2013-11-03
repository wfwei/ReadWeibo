# !/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin

from ReadWeibo.account.models import Account, UserOauth2

from datetime import datetime
import time

#Regist Account table
class AccountAdmin(admin.ModelAdmin):

    list_display = ['user_img', 'w_uid', 'w_name', 'real_category', 'predict_category', 'w_followers_count', 'w_friends_count', 'w_description']
    #, 'last_update_info', 'last_update_htl', 'last_update_utl', 'last_update_fri', 'last_update_fol']

    list_filter = ['real_category', 'predict_category']

    def user_img(self, obj):
        return u'<img src="%s" />' % obj.w_profile_image
    user_img.short_description = 'Image'
    user_img.allow_tags = True

admin.site.register(Account, AccountAdmin)


# Regist UserOauth2 table
class UserOauth2Admin(admin.ModelAdmin):

    list_display = ['w_uid', 'access_token' \
                    , 'format_time', 'expired']

    def expired(self, obj):
        return float(obj.expires_in) < time.time()

    def format_time(self, obj):
        return datetime.fromtimestamp(long(obj.expires_in)).strftime('%Y-%m-%d %H:%M:%S')
    format_time.short_description = 'expires_in'

admin.site.register(UserOauth2, UserOauth2Admin)
