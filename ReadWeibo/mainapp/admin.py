# !/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin

from ReadWeibo.mainapp.models import Category, Weibo, Comment

from datetime import datetime
import time

#Regist Category Admin
class CategoryAdmin(admin.ModelAdmin):

    list_display = ['category_id', 'name', 'keywords',]

admin.site.register(Category, CategoryAdmin)

#Regist Weibo Admin
class WeiboAdmin(admin.ModelAdmin):

    list_display = ['w_id', 'predict_category', 'real_category', 'format_created_at', 'reposts_count', 'comments_count', 'text']

    def format_created_at(self, obj):
        return obj.format_created_at()
    format_created_at.short_description = 'created_at'

    list_filter = ['predict_category', 'real_category']

admin.site.register(Weibo, WeiboAdmin)

#Regist Comment Admin
class CommentAdmin(admin.ModelAdmin):

    list_display = ['c_id', 'format_created_at', 'text']

    def format_created_at(self, obj):
        return obj.format_created_at()
    format_created_at.short_description = 'created_at'

admin.site.register(Comment, CommentAdmin)
