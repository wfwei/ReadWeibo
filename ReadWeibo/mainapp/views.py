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

# global static variables 
_DEBUG = True
_mimetype = u'application/javascript, charset=utf8'
wclient = weibo.APIClient(app_key=Config.weibo_app_key,
                    app_secret = Config.weibo_app_secret,
                    redirect_uri = Config.callback_url)
all_categories = Category.objects.all()

def home(request, category_id=0):
    template_var = {}
    print 'current login user: ', request.user
    
    if request.user.is_authenticated() and not request.user.is_superuser:
        user = Account.objects.get(w_name=request.user.username)

        # fetch new weibo
#         if category_id == 0:
#             thread.start_new_thread(WeiboFetcher.FetchHomeTimeline,(user.w_uid, ))
        watch_weibo = user.watchweibo.filter(real_category__exact=None).filter(retweeted_status__exact=None)[:10]
        size = len(watch_weibo) / 2;
        print len(watch_weibo)
        template_var['watch_weibo_left'] = watch_weibo[:size]
        template_var['watch_weibo_right'] = watch_weibo[size:]
        template_var['cur_user'] = user
        template_var['category_id'] = category_id
        template_var['all_categories'] = all_categories
    else:
        template_var['authorize_url'] = wclient.get_authorize_url()

    return render_to_response("home.html", template_var,
                              context_instance=RequestContext(request))

def set_category(request):
    if not request.is_ajax():
        return HttpResponse('ERROR:NOT AJAX REQUEST')
    post_data = simplejson.loads(request.raw_post_data)
    try:
        wb = Weibo.objects.get(w_id=post_data['w_id'])
        wb.real_category = post_data['category']
        wb.save()
    except:
        print 'post_data error...'
        return HttpResponse(simplejson.dumps(False), _mimetype)
    return HttpResponse(simplejson.dumps(True), _mimetype)










