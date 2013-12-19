# !/usr/bin/python
# -*- coding: utf-8 -*-

from ReadWeibo.mainapp.models import *
from ReadWeibo.account.models import *
from django.db.models import Count

import sys

if len(sys.argv) < 2:
        print 'parameter error!\n\t one parameters needed: input_file'
        print 'current argument List:', str(sys.argv)
        sys.exit(1)

f = open(sys.argv[1], 'w')
limit = 10
for item in Weibo.objects.values('owner').annotate(cnt=Count('owner')):
    if item['cnt']>20:
        user = Account.objects.get(id=item['owner'])
        lid = 1
        for wb in user.ownweibo.all():
            f.write(wb.text.encode('utf-8'))
            lid += 1
            if lid>5:
                break
        f.write('\n')
        limit -= 1
        if limit<0:
            break

f.close()
