# !/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2013-10-8
@author: plex
'''

from ReadWeibo.account.models import Account
from ReadWeibo.mainapp.models import Category, Weibo, Comment
from crawler import UserFetcher, TopicCrawler

import sys
import logging
import thread

class WeiboClassifer():

    ''' classify weibo'''

    def __init__(self, category_id):
        self.category_id = category_id
        self.category = Category.objects.get(category_id=category_id)
        self.keyword_set = set()
        for keyword in self.category.keywords.split():
            logging.info('Adding %s to %s' % (keyword, self.category))
            self.keyword_set.add(keyword)
        logging.info('Init WeiboClassifier Over, with %d keywords imported in category %s'
                    % (len(self.keyword_set), self.category))

    def label_by_content(self, reset_all=False):
        '''
        Label weibo by it's content
        '''

        import jieba
        jieba.load_userdict("/etc/jieba/jieba.dic")


        logging.info('Start labeling weibos by content')
        page_id=0; page_size = 1000; over = False; cnt = 0

        while not over:

            if reset_all:
                # fetch all original weibo
                weibos = Weibo.objects.filter(retweeted_status__exact=None)[page_id:page_id+page_size]
            else:
                # Only fetch original weibos have not been predicted before
                weibos = Weibo.objects.filter(retweeted_status__exact=None)\
                        .filter(predict_category=0)[page_id:page_id+page_size]

            logging.info('Fetched %d weibos for labeling' % len(weibos))

            if not weibos or len(weibos)<page_size:
                over = True
            else:
                page_id += len(weibos)

            for weibo in weibos:

                retweet_statuses = weibo.retweet_status.all()
                # consider comments

                weibo.predict_category = Category.NO_CATEGORY # reset category

                content = weibo.text
                for rwb in retweet_statuses:
                    rwb.predict_category = Category.NO_CATEGORY
                    content += rwb.text

                logging.info(u'predicting %s(with %d retweets) -- %s' % (weibo, len(retweet_statuses), weibo.text))

                for word in jieba.cut(content.lower()):
                    # find one keyword, and classify in this category
                    if word in self.keyword_set:
                        logging.info(u'%s Predict %s belongs to %s' % (cnt, weibo, self.category))
                        weibo.predict_category = self.category_id
                        for rwb in retweet_statuses:
                            rwb.predict_category = self.category_id
                        cnt += 1
                        break
                weibo.save()

        logging.info('Labeled %d new weibo in %s' % (cnt, self.category))

    def label_by_user(self, threshold=3, reset_all=False):
        '''
        Label Weibo By Users related
        '''

        logging.info('Start labeling weibos by users related to it')
        page_id=0; page_size = 1000; over = False; cnt = 0

        while not over:

            if reset_all:
                # fetch all original weibo
                weibos = Weibo.objects.filter(retweeted_status__exact=None)[page_id:page_id+page_size]
            else:
                # Only fetch original weibos have not been predicted before
                weibos = Weibo.objects.filter(retweeted_status__exact=None)\
                        .filter(predict_category=0)[page_id:page_id+page_size]

            # logging.info('Fetched %d weibos for labeling' % len(weibos))

            if not weibos or len(weibos)<page_size:
                over = True
            else:
                page_id += len(weibos)

            for weibo in weibos:

                logging.info("analyzing weibo:%s" % weibo)

                retweets = weibo.retweet_status.all()
                comments = weibo.comments.all()

                pos_cnt = 0; neg_cnt = 0
                for rt in (retweets+comments):
                    if rt.owner.predict_category == self.category_id:
                        pos_cnt += 1
                    else:
                        neg_cnt += 1

                logging.info("%d positive users, %d negtive users" % (pos_cnt, neg_cnt))

                if pos_cnt>threshold:
                    logging.info("predict it as postive")
                    weibo.predict_category = self.category_id
                else:
                    logging.info("predict it as negtive")
                    weibo.predict_category = Category.NO_CATEGORY # reset category

                weibo.save()

        logging.info('Labeled %d new weibo in %s' % (cnt, self.category))



    def learn(self):
        pass

if __name__ == '__main__':
    print Account.objects.count()
    print Category.NO_CATEGORY
    classifier = WeiboClassifer(category_id=1)
    classifier.label_by_user()
    pass

