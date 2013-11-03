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

from ReadWeibo.mainapp.models import Weibo, Category
from ReadWeibo.account.models import Account
from libweibo import weibo
from main import Config

from time import sleep
import itertools
import datetime
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
#default_user = Account.objects.get(w_name='WeBless')

def home(request, category_id=1):
    return show_weibo_for_labeling(request)

def show_weibo_for_labeling(request):
    ''' show statuses for labeling '''

    logging.info('show_weibo_for_labeling current login user: %s' % request.user)


    weibo_list = Weibo.objects.filter(real_category=0).filter(retweeted_status__exact=None).filter(owner__in=Account.objects.filter(predict_category=1))[:40]

    template_var = {}
    template_var['weibo_list'] = weibo_list
    template_var['all_categories'] = all_categories
    template_var['authorize_url'] = wclient.get_authorize_url()

    return render_to_response("weibos.html", template_var,
                              context_instance=RequestContext(request))

def show_weibos_predict(request, category_id=0, show_predict=True):
    return show_weibos(request, category_id, show_predict)

def show_weibos(request, original=True, category_id=0, show_predict=False):
    try:
        category = Category.objects.get(category_id=category_id)
    except:
        logging.warn('No category found')
        return HttpResponse('No category found for id:%s' % category_id)

    logging.info('current login user: %s, show %s' % (request.user, category))

    template_var = {}
    if show_predict:
        watch_weibo = Weibo.objects.filter(predict_category=category_id)
    else:
        watch_weibo = Weibo.objects.filter(real_category=category_id)

    if original:
        watch_weibo = watch_weibo.filter(retweeted_status__exact=None)[:40]
    else:
        watch_weibo = watch_weibo[:40]

    template_var['weibo_list'] = watch_weibo
    template_var['category_id'] = category_id
    template_var['all_categories'] = all_categories
    template_var['authorize_url'] = wclient.get_authorize_url()

    logging.info('category weibos count:%d' % len(watch_weibo))

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


