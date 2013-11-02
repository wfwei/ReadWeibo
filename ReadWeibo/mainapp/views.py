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
all_categories = Category.objects.exclude(category_id=0)
default_user = Account.objects.get(w_name='WeBless')

def home(request, category_id=1):
    ''' show statuses from users in category '''
    try:
        category = Category.objects.get(category_id=category_id)
    except:
        logging.warn('No category found')
        return HttpResponse('No category found for id:%s' % category_id)

    logging.info('current login user: %s, show statuses from users in %s' % (request.user, category))

    if request.user.is_authenticated() and not request.user.is_superuser:
        user = Account.objects.get(w_name=request.user.username)
    else:
        user = default_user

    template_var = {}

    weibo_list = Weibo.objects.filter(owner__in=Account.objects.filter(predict_category=category_id))\
                            .filter(real_category=0)[:40]

    messages = 'Latest Statuses from users in %s' % category

    size = len(weibo_list) / 2;
    template_var['weibo_list_left'] = weibo_list[:size]
    template_var['weibo_list_right'] = weibo_list[size:]
    template_var['cur_user'] = user
    template_var['category_id'] = category_id
    template_var['all_categories'] = all_categories
    template_var['authorize_url'] = wclient.get_authorize_url()

    #template_var['messages'] = messages

    return render_to_response("weibos.html", template_var,
                              context_instance=RequestContext(request))

    return show_weibos(request,1)

def show_weibos_predict(request, category_id=0, show_predict=True):
    return show_weibos(request, category_id, show_predict)

def show_weibos(request, category_id=0, show_predict=False):
    try:
        category = Category.objects.get(category_id=category_id)
    except:
        logging.warn('No category found')
        return HttpResponse('No category found for id:%s' % category_id)

    logging.info('current login user: %s, show %s' % (request.user, category))

    template_var = {}
    if show_predict:
        watch_weibo = Weibo.objects.filter(predict_category=category_id)[:40] #.filter(retweeted_status__exact=None)[:40]
        messages = 'Predict View: '
    else:
        watch_weibo = Weibo.objects.filter(real_category=category_id)[:40] #.filter(retweeted_status__exact=None)[:40]
        messages = 'Non-Predict View: '

    size = len(watch_weibo) / 2;
    template_var['weibo_list_left'] = watch_weibo[:size]
    template_var['weibo_list_right'] = watch_weibo[size:]
    template_var['cur_user'] = user
    template_var['category_id'] = category_id
    template_var['all_categories'] = all_categories
    template_var['authorize_url'] = wclient.get_authorize_url()

    template_var['messages'] = messages + '%d weibo in User:%s\' home timeline' % \
            (len(watch_weibo), user.w_name)

    logging.info('category weibos count:%d' % len(watch_weibo))

    return render_to_response("weibos.html", template_var,
                              context_instance=RequestContext(request))

def show_users_predict(request, category_id=0, show_predict=True):
    return show_users(request, category_id, show_predict)

def show_users(request, category_id=0, show_predict=False):

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
        category_users = Account.objects.filter(predict_category=category_id)
        messages = 'Predict view:'
    else:
        category_users = Account.objects.filter(real_category=category_id)
        messages = 'Non-Predict view:'

    template_var['category_users'] = category_users
    template_var['all_categories'] = all_categories

    template_var['messages'] = messages + '%d users in category:%s' % \
            (len(category_users), category.name)

    logging.info('category users count:%d' % len(template_var['category_users']))

    return render_to_response("users.html", template_var,
                              context_instance=RequestContext(request))

def show_user_weibos(request, w_uid=0, category_id=0, show_predict=False):
    logging.info('w_uid:%s, type:%s' % (w_uid, type(w_uid)))
    try:
        user = Account.objects.get(w_uid=w_uid)
    except:
        logging.warn('No user found for id:%s' % w_uid)
        return HttpResponse('No user found for id:%s' % w_uid)

    logging.info('current login user: %s, show %s\' weibos' % (request.user, user))

    template_var = {}
    watch_weibo = user.ownweibo.filter(real_category=category_id)[:40]
    size = len(watch_weibo) / 2;
    template_var['weibo_list_left'] = watch_weibo[:size]
    template_var['weibo_list_right'] = watch_weibo[size:]
    template_var['all_categories'] = all_categories
    template_var['messages'] = 'show %s\'s weibos %d/%d' % \
            (user.w_name, len(watch_weibo), user.ownweibo.count())

    logging.info('%s weibos count:%d' % (user, len(watch_weibo)))

    return render_to_response("weibos.html", template_var,
                              context_instance=RequestContext(request))



def set_weibo_category(request):
    if not request.user.is_authenticated() or not request.user.is_superuser:
        return HttpResponse(simplejson.dumps(False), _mimetype)
    if not request.is_ajax():
        return HttpResponse('ERROR:NOT AJAX REQUEST')
    post_data = simplejson.loads(request.raw_post_data)
    try:
        wb = Weibo.objects.get(w_id=post_data['w_id'])
        category_id = post_data['category']
        category = Category.objects.get(category_id=category_id)
        wb.real_category = category_id
        wb.save()

        if wb.retweeted_status:
            original_status = wb.retweeted_status
            original_status.real_category = category_id
            original_status.save()
            for retweet in original_status.retweet_status.all():
                retweet.real_category = category_id
                retweet.save()
    except:
        logging.warn('post_data error:%s' % post_data)
        return HttpResponse(simplejson.dumps(False), _mimetype)
    return HttpResponse(simplejson.dumps(category.name), _mimetype)


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

