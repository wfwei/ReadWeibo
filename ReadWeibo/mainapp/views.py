# !/usr/bin/python
# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count
from django.utils import simplejson

from ReadWeibo.account.models import Account
from ReadWeibo.mainapp.models import Weibo, Category

from main import Config
from libweibo import weibo
from time import sleep
import itertools
import datetime
import thread
import re
import logging

# global static variables
_DEBUG = True
_mimetype = u'application/javascript, charset=utf8'
wclient = weibo.APIClient(app_key=Config.weibo_app_key,
                    app_secret = Config.weibo_app_secret,
                    redirect_uri = Config.callback_url)
all_categories = Category.objects.all()
default_user = Account.objects.get(w_name='WeBless')

def home(request):
    return show_weibos(request,1)

def show_weibos(request, category_id=0):
    try:
        category = Category.objects.get(category_id=category_id)
    except:
        logging.warn('No category found')
        return HttpResponse('No category found for id:%s' % category_id)

    logging.info('current login user: %s, show %s' % (request.user, category))

    if request.user.is_authenticated() and not request.user.is_superuser:
        user = Account.objects.get(w_name=request.user.username)
    else:
        user = default_user

    # fetch new weibo
    # if category_id == 0:
    #       thread.start_new_thread(WeiboFetcher.FetchHomeTimeline,(user.w_uid, ))
    template_var = {}
    watch_weibo = user.watchweibo.filter(predict_category=category_id).filter(retweeted_status__exact=None)[:20]
    size = len(watch_weibo) / 2;
    template_var['watch_weibo_left'] = watch_weibo[:size]
    template_var['watch_weibo_right'] = watch_weibo[size:]
    template_var['cur_user'] = user
    template_var['category_id'] = category_id
    template_var['all_categories'] = all_categories
    template_var['authorize_url'] = wclient.get_authorize_url()

    return render_to_response("weibos.html", template_var,
                              context_instance=RequestContext(request))

def show_users(request, category_id=0):

    if request.user.is_authenticated() and not request.user.is_superuser:
        user = Account.objects.get(w_name=request.user.username)
        logging.info('Current Login user: %s' % user)
    else:
        logging.info('Anonymouse user, use default user:%s' % default_user)
        user = default_user

    try:
        category = Category.objects.get(category_id=category_id)
        logging.info('show users in category: %s' % category)
    except:
        logging.warn('No category found')
        return HttpResponse('No category found for id:%s' % category_id)

    template_var = {}
    template_var['category'] = category
    template_var['category_users'] = user.friends.filter(predict_category=category_id)
    template_var['all_categories'] = all_categories

    return render_to_response("users.html", template_var,
                              context_instance=RequestContext(request))

def set_weibo_category(request):
    if not request.is_ajax():
        return HttpResponse('ERROR:NOT AJAX REQUEST')
    post_data = simplejson.loads(request.raw_post_data)
    try:
        wb = Weibo.objects.get(w_id=post_data['w_id'])
        category_id = post_data['category']
        category = Category.objects.get(category_id=category_id)
        wb.real_category = category_id
        wb.save()
    except:
        logging.warn('post_data error:%s' % post_data)
        return HttpResponse(simplejson.dumps(False), _mimetype)
    return HttpResponse(simplejson.dumps(category.name), _mimetype)


def set_user_category(request):
    if not request.is_ajax():
        return HttpResponse('ERROR:NOT AJAX REQUEST')
    post_data = simplejson.loads(request.raw_post_data)
    try:
        user = Account.objects.get(w_uid=post_data['u_id'])
        category_id = post_data['category']
        category = Category.objects.get(category_id=category_id)
        user.real_category = category_id
        user.save()
    except:
        logging.warn('post_data error:%s' % post_data)
        return HttpResponse(simplejson.dumps(False), _mimetype)
    return HttpResponse(simplejson.dumps(category.name), _mimetype)

