# !/usr/bin/python
# -*- coding: utf-8 -*-

from ReadWeibo.mainapp.models import Category, Weibo, Comment
from ReadWeibo.account.models import Account
from crawler import WeiboFetcher
from main import Config

from datetime import datetime, timedelta
import logging
import time

def CollectData():

    user_maps = [{},{},{},{},{},{},{},{},{},{}]

    user_idx = 0; page_size = 1000
    wb_f = open(u'data/Weibo2ID', u'w')
    user_f = open(u'data/User2ID', u'w')
    wb_user_f = open(u'data/Weibo2User', u'w')

    # Collect weibos
    wb_idx = 0
    wb_cnt = Weibo.objects.count()
    while wb_idx<wb_cnt:

        logging.info('Collected %d of %d weibos' % (wb_idx, wb_cnt))
        time.sleep(1)

        wb_list = Weibo.objects.all()[wb_idx:wb_idx+page_size]
        for wb in wb_list:

            w_id = wb.w_id
            if not wb.owner:
                logging.warn('no owner for %s' % wb)
                wb.delete()
                wb_cnt -= 1
                continue
            w_uid = wb.owner.w_uid

            if not w_uid in user_maps[w_uid%10]:
                user_maps[w_uid%10][w_uid] = user_idx
                user_f.write(u'%s %s\n'%(w_uid, user_idx))
                user_idx += 1

            if wb.retweeted_status:
                typ = 1
            else:
                typ = 0

            wb_f.write(u'%s %s\n' % (w_id, wb_idx))
            wb_user_f.write(u'%s %s %s\n' % (wb_idx, user_maps[w_uid%10][w_uid], typ))
            wb_idx += 1


    # Collect Comments
    comm_idx = 0
    comm_cnt = Comment.objects.count()

    while comm_idx<comm_cnt:

        logging.info('Collected %d of %d comments' % (comm_idx, comm_cnt))
        time.sleep(1)

        st = time.time()
        comm_list= Comment.objects.all()[comm_idx:comm_idx+page_size]
        logging.info('Fetch %d comments with time:%s' % (len(comm_list), time.time()-st))

        totime = 0
        for comm in comm_list:


            if not comm.owner:
                logging.warn('no owner for %s' % comm)
                comm.delete()
                comm_cnt -= 1
                continue

            c_id = comm.c_id
            c_uid = comm.owner.w_uid


            st = time.time()
            if not c_uid in user_maps[c_uid%10]:
                user_maps[c_uid%10][c_uid] = user_idx
                user_f.write(u'%s %s\n' % (c_uid, user_idx))
                user_idx += 1

            typ = 3 # comment type
            wb_f.write(u'%s %s\n' % (c_id, comm_idx+wb_idx))
            wb_user_f.write(u'%s %s %s\n' % (comm_idx+wb_idx, user_maps[c_uid%10][c_uid], typ))
            comm_idx += 1

            totime += time.time()-st

        logging.info('process time:%s' % totime)

    user_f.close()
    wb_f.close()
    wb_user_f.close()

if __name__ == '__main__':
    CollectData()
