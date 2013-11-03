# !/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from ReadWeibo.account.models import Account, UserOauth2
from ReadWeibo.mainapp.models import Weibo, Category
from libweibo import weibo
from main import Config

from datetime import datetime
from time import sleep
import itertools
import logging
import thread
import re

# global static variables
_DEBUG = True
_mimetype = u'application/javascript, charset=utf8'
wclient = weibo.APIClient(app_key=Config.weibo_app_key,
                    app_secret = Config.weibo_app_secret,
                    redirect_uri = Config.callback_url)
all_categories = Category.objects.exclude(category_id=0)

def show_users_predict(request, category_id=0, show_predict=True):
    return show_users(request, category_id, show_predict)

def show_users(request, category_id=0, show_predict=False, max_count=200):

    try:
        category = Category.objects.get(category_id=category_id)
        logging.info('show users in category: %s' % category)
    except:
        logging.warn('No category found')
        return HttpResponse('No category found for id:%s' % category_id)

    logging.info('current login user: %s, show %s' % (request.user, category))

    template_var = {}
    template_var['category'] = category

    if show_predict:
        category_users = Account.objects.filter(predict_category=category_id)[:max_count]
        messages = 'Predict view:'
    else:
        category_users = Account.objects.filter(real_category=category_id)[:max_count]
        messages = 'Non-Predict view:'

    template_var['category_users'] = category_users
    template_var['all_categories'] = all_categories

    template_var['messages'] = messages + '%d users in category:%s' % \
            (len(category_users), category.name)

    logging.info('category users count:%d' % len(template_var['category_users']))

    return render_to_response("users.html", template_var,
                              context_instance=RequestContext(request))

def show_user_weibos(request, w_uid=0, category_id=0, show_predict=False):
    ''' display user weibos '''

    logging.info('w_uid:%s, type:%s' % (w_uid, type(w_uid)))

    try:
        user = Account.objects.get(w_uid=w_uid)
    except:
        logging.warn('No user found for id:%s' % w_uid)
        return HttpResponse('No user found for id:%s' % w_uid)

    logging.info('current login user: %s, show %s\' weibos' % (request.user, user))

    template_var = {}
    watch_weibo = user.ownweibo.filter(real_category=category_id)[:40]
    template_var['weibo_list'] = watch_weibo
    template_var['all_categories'] = all_categories
    template_var['messages'] = 'show %s\'s weibos %d/%d' % \
            (user.w_name, len(watch_weibo), user.ownweibo.count())

    logging.info('%s weibos count:%d' % (user, len(watch_weibo)))

    return render_to_response("weibos.html", template_var,
                              context_instance=RequestContext(request))

def set_user_category(request):
    if not request.user.is_authenticated() or not request.user.is_superuser:
        return HttpResponse(simplejson.dumps(False), _mimetype)
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

def weibo_callback(request):

    # 获取code和授权信息
    code = request.GET.get('code')
    _r = wclient.request_access_token(code)
    w_uid = _r.uid
    access_token = _r.access_token
    expires_in = _r.expires_in

    # 保存或更新授权信息
    try:
        oauth = UserOauth2.objects.get(w_uid = w_uid)
        oauth.access_token = access_token
        oauth.expires_in = expires_in
        is_new = False
    except ObjectDoesNotExist:
        oauth = UserOauth2.objects.create(w_uid=w_uid, access_token=access_token, expires_in=expires_in)
        is_new = True

    if is_new:

        wclient.set_access_token(access_token, expires_in)
        uinfo = wclient.get.users__show(uid=w_uid)

        account = AccountDao.create_or_update(uinfo)
        if not account.user:
            #create django.contrib.auth.models.User
            user, ucreated = User.objects.get_or_create(username=uinfo[u'name'], password=w_uid)
            if not ucreated: #微博名字有重复
                user, ucreated = User.objects.get_or_create(username=uinfo['name']+w_uid, password=w_uid)
            account.user = user

        account.oauth=oauth
    else:
        account = Account.objects.get(w_uid=w_uid)

    account.save()

    account.user.backend = 'django.contrib.auth.backends.ModelBackend'
    auth_login(request, account.user)
    return HttpResponseRedirect('/')

def weibo_callback_rm(request):
    print u'TODO'
