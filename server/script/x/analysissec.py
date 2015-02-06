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
from sklearn.ensemble import RandomForestRegressor

symbols = secSymbols
eastern = timezone('US/Eastern')

historyLength = 10
futureLength = 5
buyInThreshold = 0.004

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
        stocks[s][i]['DayDelta'] = days_between(stocks[s][i]['Date'], stocks[s][i-1]['Date'])
      else:
        stocks[s][i]['DayDelta'] = 0
  return stocks

def extract_f(stocks):
  f = {}
  for s in symbols:
    f[s] = [];
  dateLen = len(stocks[symbols[0]])
  for i in range(dateLen - historyLength - futureLength):
    features = [];
    for s in symbols:
      priceds = [ st['PriceDelta'] for st in stocks[s][i:i+historyLength]]
      features.extend(priceds)
      features.extend([ float(st['Volume']) for st in stocks[s][i:i+historyLength] ])
      features.append(stocks[s][i+historyLength-1]['DayDelta'])
    for s in symbols:
      ff = [ xx for xx in features];
      ff.append( (float(stocks[s][i+historyLength+futureLength-1]['Close']) - float(stocks[s][i+historyLength-1]['Close'])) / float(stocks[s][i+historyLength-1]['Close']))
      #print ff
      f[s].append(ff)
  return f

def split(features, ratio): # train data ratio
  trainX = {}
  trainY = {}
  testX = {}
  testY = {}
  f_len = len(features[symbols[0]])
  trainLen = int(f_len-252);
  for s in symbols:
    trainX[s] = [f[:-1] for f in features[s][:trainLen]]
    trainY[s] = [f[-1] for f in features[s][:trainLen]]
    testX[s] = [f[:-1] for f in features[s][trainLen:]]
    testY[s] = [f[-1] for f in features[s][trainLen:]]
  return trainX, trainY, testX, testY

def runAnalysis():
  stocks = readDataFromCSV()
  #for ele in stocks['test'][:10]:
  #  print ele
  stocks = calPriceDelta(stocks)
  #print "="*30
  #for ele in stocks['test'][:10]:
  #  print ele
  f = extract_f(stocks)
  trainX, trainY, testX, testY = split(f, 0.66);
  days =len(testY['XLY'])
  print "len:", len(trainY), days
  trans = 0;
  predictedY = {}
  i = 0
  sum = 1.0
  while i < (days):
    print(i, "running clf for:"),
    for s in symbols:
      print(s),
      clf = RandomForestRegressor(n_estimators=200, n_jobs=-1);
      trainX[s] = trainX[s][-252:]
      trainY[s] = trainY[s][-252:]
      clf.fit(trainX[s], trainY[s]);
      predictedY[s] = clf.predict(testX[s][i]);
      predictedY[s] = predictedY[s][0];
      trainX[s].append(testX[s][i]);
      trainY[s].append(testY[s][i]);
    maxbuyS = '';
    maxP = buyInThreshold;
    print 'testY', np.sum([testY[s][i] for s in symbols])/9 ,
    for s in symbols:
      if predictedY[s] > maxP:
        maxP = predictedY[s]
        maxbuyS = s;
    if maxbuyS == '':
      i+=1
      print ""
      continue
    #print predictedY[maxbuyS][i], testY[maxbuyS][i],  "error:", abs(predictedY[maxbuyS][i] - testY[maxbuyS][i])/testY[maxbuyS][i] if testY[maxbuyS][i] else 0;
    sum *= (1 + testY[maxbuyS][i]);
    trans += 1
    i+= futureLength;
    for s in symbols:
      trainX[s].extend(testX[s][(i-futureLength+1):i])
      trainY[s].extend(testY[s][(i-futureLength+1):i])
    print "sum: ", sum
  print "\ngain:", sum, "in trans:",trans
  return sum, trans

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