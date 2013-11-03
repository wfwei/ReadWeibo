# !/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2013-9-2

@author: plex
'''
from ReadWeibo.mainapp.models import Weibo
from ReadWeibo.account.models import Account
from djangodb.WeiboDao import WeiboDao
from datetime import datetime
from sets import Set
import numpy as np
import re

import jieba
jieba.load_userdict("/etc/jieba/jieba.dic")

DIC_FILE = "../data/dic/weibo.dic"
TRAIN_FILE = "../data/train/weibo_vec.tr"

#TODO 去停用词 规范化单词 添加词典http://www.sogou.com/labs/dl/w.html
def generate_user_dict(dic_file=DIC_FILE):
	wbs = Weibo.objects.all()[:5000]
	wordset = Set()

	print 'Generating dict with %d weibo' % len(wbs)

	for wb in wbs:
		for word in jieba.cut(wb.text.encode('utf-8','ignore')):
			if len(word)>6: #TODO filter by Cixing
				wordset.add(word.lower().strip())

	with open(dic_file, "w") as f:
		for word in wordset:
			f.write("%s\n" % word)

def load_dict(dic_file=DIC_FILE):
	print 'loading dict from ', DIC_FILE
	dict = {}
	with open(dic_file, "r") as f:
		id = 0
		for word in f:
			dict[word.strip().encode("utf-8", "ignore")] = id
			id += 1
	return dict

def generate_feature(wb, dict):
 	fea = [0]*len(dict)
	# 微博文本
	for wd in jieba.cut(wb.text.encode('utf-8','ignore')):
		word_count = 0
		wd = wd.lower().strip()
 		if len(wd)>3 and wd in dict:
 			fea[dict[wd]] += 1
 			word_count += 1
# 		print 'found %d word in a weibo' % word_count
	# add user features
	owner = wb.owner
	fea.append(int(owner.w_province))
	fea.append(int(owner.w_city))
	if owner.w_url:
		fea.append(1)
	else:
		fea.append(0)
	fea.append(len(owner.w_description))
	if 'm' in owner.w_gender:
		fea.append(1)
	else:
		fea.append(0)

	fea.append(int(owner.w_followers_count))
	fea.append(int(owner.w_friends_count))
	fea.append(int(owner.w_statuses_count))
	fea.append(int(owner.w_favourites_count))
	fea.append(int(owner.w_bi_followers_count))
	fea.append((datetime.now()-owner.w_created_at).days/100)
	if owner.w_verified:
		fea.append(1)
	else:
		fea.append(0)


	# add weibo features
	fea.append(int(wb.reposts_count))
	fea.append(int(wb.comments_count))
	fea.append(int(wb.attitudes_count))
	if re.search("#.*?#", wb.text):
		fea.append(1)
	else:
		fea.append(0)

	fea.append(len(wb.text))
	own_text = re.search("(.*?)//@", wb.text)
	if own_text:
		fea.append(len(own_text.group(1)))
	else:
		fea.append(len(wb.text))
	#TODO 对source归类
	fea.append(len(wb.source))

	if wb.retweeted_status:
		fea.append(0)
	else:
		fea.append(1)

	if wb.thumbnail_pic:
		fea.append(1)
	else:
		fea.append(0)
	fea.append(wb.created_at.hour)
	fea.append(wb.created_at.weekday())
	# TODO 计算微博转发评论的衰减公式

	return fea

def generate_train_file():

	print 'Generating train file...'

	wbs = Weibo.objects.filter(real_category__gt=0)
	word_dic = load_dict()

	print 'Train set size: %d, dic size:%d' % (len(wbs), len(word_dic))

	with open(TRAIN_FILE, "w") as train_file:
		for wb in wbs:
			for fea in generate_feature(wb, word_dic):
				train_file.write("%s\t" % fea)
			train_file.write("%s\n" % wb.real_category)

def get_weibo_to_predict(count=1000):

	wbs = Weibo.objects.filter(real_category__exact = 0)[:count]
	word_dic = load_dict()
	wb_feas_list = list()
	for wb in wbs:
		try:
			wb_feas_list.append((wb, [1.0] + generate_feature(wb, word_dic)));
		except:
			print 'generate feature fail for weibo:', wb.w_id

	return wb_feas_list

if __name__ == '__main__':
	generate_user_dict()
	generate_train_file()
# 	print generate_feature(Weibo.objects.get(w_id=3617663458268921),{})
	pass
