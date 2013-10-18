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
from libweibo import weibo
from main import Config
from djangodb.AccountDao import AccountDao

from datetime import datetime

_DEBUG = True

wclient = weibo.APIClient(app_key=Config.weibo_app_key,
                    app_secret = Config.weibo_app_secret,
                    redirect_uri = Config.callback_url)

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
        account.save()
    else:
        account = Account.objects.get(w_uid=w_uid)

    account.user.backend = 'django.contrib.auth.backends.ModelBackend'
    auth_login(request, account.user)
    return HttpResponseRedirect('/')

def weibo_callback_rm(request):
    print u'TODO'
