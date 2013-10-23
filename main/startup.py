# !/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 2013-10-7

@author: plex
'''

from ReadWeibo.mainapp.models import Category
import logging

logging.info(u'Initializing categories')
# Add NULL category
category, created = Category.objects.get_or_create(category_id=0)
if created:
	category.name = u'未分类'
	category.keywords = u''
	category.save()
	logging.info(u'Create new category:%s' % category)

# Add ML category
category, created = Category.objects.get_or_create(category_id=1)
if created:
	category.name = u'机器学习'
	category.keywords = u'数据挖掘 datamining dm 机器学习 machinelearing ml 自然语言处理 natuallanguageprocess nlp 模式识别 patternrecognization 信息检索 informationretrieval 统计学习 statisticsstudy CTR 人脸识别 acerecognization 模型优化 modeloptimization 社交网络 socialnetwork 搜索引擎 searchengine rank 数据分析 dataanlysis 机器翻译 个性化推荐 推荐系统 recommendsystem 大数据 bigdata 计算机视觉 文本挖掘 textmining '
	category.save()
	logging.info(u'Create new category:%s' % category)

logging.info(u'Initialization done')
