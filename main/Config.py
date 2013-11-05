# !/usr/bin/python
# -*- coding: utf-8 -*-

'''
Over all configuration

Created on Aug 29, 2013
@author: plex
'''

# Logging config
import logging, sys, re
from datetime import datetime

logging.basicConfig(level=logging.INFO,
				format='%(asctime)s : %(name)-8s : %(levelname)s : %(message)s',
				datefmt='%Y-%m-%d %H:%M:%S',
				filename= '/var/log/readweibo/%s-%s.log' % (sys.argv[0].split()[0], datetime.now()),
				filemode='a+')

formatter = logging.Formatter('%(asctime)s : %(name)-8s: %(levelname)-8s %(message)s',
							'%Y-%m-%d %H:%M:%S')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
logging.info("running %s" % ' '.join(sys.argv))

WEIBO_API = {
        'app_key'              : u'3482624382',
        'app_secret'           : u'af44e0e7c3a7a55760d437cea207dd22',
        'site_url'             : u'http://115.28.165.49',
        'callback_url'         : u'http://115.28.165.49/weibo_callback',
        'callback_rm_url'      : u'http://115.28.165.49/weibo_callback_rm'}

if __name__=='__main__':
	logging.warn('a warn message')
	pass

