__author__ = 'hcai'

from download_sec import secSymbols

from pymongo import MongoClient
import csv
from random import shuffle, sample
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import train_test_split
from sklearn.cross_validation import cross_val_score
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import numpy as np
import calendar
from datetime import datetime
from pytz import timezone
import operator
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import SVC
from sklearn.cross_validation import StratifiedKFold
from sklearn.grid_search import GridSearchCV
from sklearn import preprocessing

symbols = secSymbols
eastern = timezone('US/Eastern')

historyLength = 1
futureLength = 2
buyInThreshold = 0.02

def readDataFromCSV():
  stocks = {}
  for s in symbols:
    stocks[s] = []
    with open(s + '.csv') as csvfile:
      dataReader = csv.reader(csvfile, delimiter=',')
      index = 0
      for row in dataReader:
        if index > 0:
          stock = {}
          stock['Date'] = row[0]
          stock['Open'] = row[1]
          stock['High'] = row[2]
          stock['Low'] = row[3]
          stock['Close'] = row[4]
          stock['Volume'] = row[5]
          stock['PriceDelta'] = float(stock['Close']) - float(stock['Open']);
          stocks[s].append(stock)
        index += 1
      stocks[s].reverse()
  return stocks

def days_between(d1, d2):
  d1 = datetime.strptime(d1, "%Y-%m-%d")
  d2 = datetime.strptime(d2, "%Y-%m-%d")
  return abs((d2 - d1).days)

def calPriceDelta(stocks):
  for s in stocks:
    stock = stocks
    for i in range(len(stocks[s])):
      if i>0:
        stocks[s][i]['PriceDelta'] = float(stocks[s][i]['Close']) - float(stocks[s][i-1]['Close'])
        stocks[s][i]['DayDelta'] = days_between(stocks[s][i]['Date'], stocks[s][i-1]['Date'])
      else:
        stocks[s][i]['PriceDelta'] = 0
        stocks[s][i]['DayDelta'] = 0
  return stocks

def extract_f(stocks):
  f = []
  dateLen = len(stocks[symbols[0]])
  for i in range(dateLen - historyLength - futureLength):
    features = [];
    #for s in symbols:
      #priceds = [ st['PriceDelta'] for st in stocks[s][i:i+historyLength]]
      #features.extend(priceds)
      #features.extend([ float(st['Volume']) for st in stocks[s][i:i+historyLength] ])
      #features.append(stocks[s][i+historyLength-1]['DayDelta'])

    nxt = []
    for j in range(len(symbols)):
      s = symbols[j]
      nxt.append((float(stocks[s][i+historyLength+futureLength-1]['Close']) - float(stocks[s][i+historyLength-1]['Close']))/ float(stocks[s][i+historyLength-1]['Close']))
    nxt = np.array(nxt);
    maxs = nxt.argmax()
    features.append(maxs);
    f.append(features);
  print np.array(f[:10])
  print 'f size:', len(f), len(f[0])
  return f

def split(features, ratio): # train data ratio
  trainX = {}
  trainY = {}
  testX = {}
  testY = {}
  f_len = len(features)
  trainLen = int(f_len-252);
  trainX = [f[:-1] for f in features[:trainLen]]
  trainY = [f[-1] for f in features[:trainLen]]
  testX = [f[:-1] for f in features[trainLen:]]
  testY = [f[-1] for f in features[trainLen:]]
  return trainX, trainY, testX, testY

def runAnalysis():
  stocks = readDataFromCSV()
  stocks = calPriceDelta(stocks)
  f = extract_f(stocks)
  trainX, trainY, testX, testY = split(f, 0.66);
  min_max_scaler = preprocessing.MinMaxScaler()
  trainX = min_max_scaler.fit_transform(trainX);
  testX = min_max_scaler.transform(testX);
  sum = 0;
  trans = 0;
  cutoff = 0.002;
  predictedY = {}
  days = 0
  print("running clf"),
  #clf = RandomForestClassifier(n_estimators=100)
  # C_range = 10.0 ** np.arange(-2, 9)
  # gamma_range = 10.0 ** np.arange(-5, 4)
  # param_grid = dict(gamma=gamma_range, C=C_range)
  # cv = StratifiedKFold(y=trainY, n_folds=3)
  # grid = GridSearchCV(SVC(), param_grid=param_grid, cv=cv)
  # grid.fit(trainX, trainY);
  # clf = grid.best_estimator_
  # print grid.best_params_
  # print grid.best_score_
  clf = SVC(gamma=10, C=0.01)
  clf.fit(trainX, trainY)
  print trainX[:10]
  print testX[:10]
  predictedY = clf.predict(testX);
  print trainY
  print testY
  print predictedY
  print clf.score(testX, testY);
  # i = 0
  # sum = 1.0
  # while i < (days):
  #   maxbuyS = '';
  #   maxP = buyInThreshold;
  #   for s in symbols:
  #     if predictedY[s][i] > maxP:
  #       maxP = predictedY[s][i]
  #       maxbuyS = s;
  #   if maxbuyS == '':
  #     i+=1
  #     continue
  #   print maxbuyS, predictedY[maxbuyS][i], testY[maxbuyS][i]
  #   #print predictedY[maxbuyS][i], testY[maxbuyS][i],  "error:", abs(predictedY[maxbuyS][i] - testY[maxbuyS][i])/testY[maxbuyS][i] if testY[maxbuyS][i] else 0;
  #   sum *= (1 + testY[maxbuyS][i]);
  #   trans += 1
  #   i+= futureLength;
  # print "\ngain:", sum, "in days:",trans
  # return sum, trans

def runExp():
  global historyLength
  global futureLength
  global buyInThreshold
  hl = [5, 10, 15, 20, 25, 30]
  fl = [2, 3, 4, 5]
  bl = [0.004, 0.005, 0.006, 0.007]
  result = [];
  for h in hl:
    for f in fl:
      if f > h:
        continue
      for b in bl:
        print (h, f, b), "started"
        historyLength = h
        futureLength = f
        buyInThreshold = b
        sum0, n0 = runAnalysis()
        sum1, n1 = runAnalysis()
        sum2, n2 = runAnalysis()
        t = sum0 + sum1 + sum2;
        n = n0 + n1 + n2;
        result.append((h, f, b, t/3, n/3));
        print (h, f, b, t, n), "ended"
        print '='*20
  result = sorted(result, key=operator.itemgetter(3), reverse=True)
  print result;

if __name__ == '__main__':
  runAnalysis()
