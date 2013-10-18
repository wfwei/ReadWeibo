#!/usr/bin/python
# coding:utf-8
'''
Created on 2013-9-3

@author: plex
'''

from classifier import DataProcess as dp
from ReadWeibo.mainapp.models import Category
import numpy as np


MODEL_FILE = "../data/model/logreg.mdl"

class LogReg():
	'''
	逻辑回归
	'''
	def __init__(self):
		
		self.train_data = []
		self.train_label = []
		self.test_data = []
		self.test_label = []
		
		self.weight = []
		self.alpha = 0.15
		self.max_iter = 1000
		
		pass

	def load_dataset(self, trainf, testf):
		
		with open(trainf, "r") as fr:
			for line in fr.readlines():
				line_val = [float(val) for val in line.strip().split()]
				self.train_data.append([1.0] + line_val[0:-1])
				self.train_label.append(line_val[-1])
		
		with open(trainf, "r") as fr:
			for line in fr.readlines():
				line_val = [float(val) for val in line.strip().split()]
				self.test_data.append([1.0] + line_val[0:-1])
				self.test_label.append(line_val[-1])
		pass
	
	# TODO add 正则项
	def train(self, feature_id):
		
		x = LogReg.normalization(np.mat(self.train_data))
		y = np.mat(map(lambda x:1 if x==feature_id else 0, self.train_label)).transpose()
		
		alpha = self.alpha
# 		self.weight = LogReg.batch_gradient_descent(x=x, y=y, alpha=alpha, maxIter=self.max_iter)
		self.weight = LogReg.stochastic_gradient_descent(x=x, y=y, alpha=alpha, maxIter=self.max_iter)
		
		return self.weight
		
	@staticmethod
	def batch_gradient_descent(x, y, alpha=0.1, alpha_decay=0.99, maxIter=1000):
		w = np.zeros((x.shape[1], 1))
		
		for i in range(maxIter):
			p = LogReg.sigmoid(x * w) # p stands for predict value
			err = y - p
			w += alpha * x.transpose() * err
			alpha *= alpha_decay
			print 'batch_gradient_descent - iteration %5d with sum error %d' % (i, err.sum())
		
		return w.tolist()
	
	@staticmethod
	def stochastic_gradient_descent(x, y, alpha=0.1, alpha_decay=0.99, maxIter=1000):
		w = np.zeros((x.shape[1], 1))
		err = np.zeros((x.shape[0], 1))
		
		for iter in range(maxIter):
			for i in range(x.shape[0]):
				(w, err[i]) = LogReg.update_weight(x[i], y[i], w, alpha) # TODO python中都是传引用，不适应
			alpha *= alpha_decay
			sum_err = np.sum(err**2)
			if alpha < 0.0001: # TODO opt stop condition
				break
			print 'stochastic_gradient_descent - iteration %5d with alpha %f sum error %f' % (iter, alpha, sum_err)
		
		return w.tolist()
	
	@staticmethod
	def update_weight(x_i, y_i, w, alpha=0.995):
		p = LogReg.sigmoid(x_i * w) # p stands for predict value
		err_i = y_i - p
		w += alpha * x_i.transpose() * err_i
		return w, err_i.sum()
		
	@staticmethod
	def normalization(data_mat):
		# (val-min)/(max-min)
		row_min = data_mat.min(axis=0)
		row_max = data_mat.max(axis=0)
		res = (data_mat-row_min + 0.000000001)/(row_max-row_min + 0.000000001)
		return res
		
	@staticmethod
	def sigmoid(val):
		return 1 / (1 + np.exp(-val))
	
	def test(self, feature_id):
		x = LogReg.normalization(np.mat(self.test_data))
		y = np.mat(map(lambda x:1 if x==feature_id else 0, self.test_label)).transpose()
		w = np.mat(self.weight)
		
		p = LogReg.sigmoid(x * w)
		
		err_count = 0
		for err in np.abs(y-p):
			if err>0.5:
				err_count += 1
		
		print 'error rate is %s' % (1.0 * err_count / x.shape[0])
		return err_count

	@staticmethod
	def get_model():
		models = []
		for category in Category.objects.all():
			if category.category_id > 0:
				arr = np.fromstring(category.model[1:-1], sep=' ')
				models.append((category.category_id, np.mat(arr).T))
		return models
	
	@staticmethod
	def generate_model():
		dp.generate_user_dict()
		dp.generate_train_file()
		lr = LogReg()
		lr.load_dataset(dp.TRAIN_FILE, dp.TRAIN_FILE)
		models = {}
		for category_id in range(Category.objects.count()-1):
			category_id += 1
			category_weight = lr.train(category_id)
			print 'Error rate on test set:', lr.test(category_id)
			models[category_id] = category_weight
			#TODO save model to file
			category = Category.objects.get(category_id=category_id)
			category.model = np.squeeze(np.asarray(category_weight))
			category.save()
		return models
	
	@staticmethod
	def predict(models, wb_vec):
		best_category = (0,0)
		for (category_id, model) in models:
			x = LogReg.normalization(np.mat(wb_vec))
			w = np.mat(model)
			print x.shape, w.shape
			predict_confidence = LogReg.sigmoid(x*w)
			if predict_confidence>best_category[1]:
				best_category = (category_id, predict_confidence)
					
		if best_category[1]>0.5:
			print 'predict category:%s with confidence:%s' % best_category
			return best_category[0]
		else:
			print 'warn: no category predicted out'
			return 0
		pass	
		
	@staticmethod
	def predict_all():
		
		models = LogReg.get_model()
		
		wb_feas_list = dp.get_weibo_to_predict(count=50)
		for (wb, feature) in wb_feas_list:
			predict_category = LogReg.predict(models, feature)
			if predict_category>0:
				wb.predict_category = predict_category
				wb.save()
			
		pass
	
def testOnSimpleSet():
	lr = LogReg()
	lr.load_dataset("../data/testSet.txt", "../data/testSet.txt");
	lr.train(1)
	lr.test(1)
	
if __name__ == '__main__':
	
		LogReg.generate_model()
		LogReg.predict_all()
		import re
		re.search('a', r'b')
	# Test on simple dataset
# 	testOnSimpleSet()
	
	
	