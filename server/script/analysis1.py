__author__ = 'hcai'

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
import bStockConfig
import pickle

symbols = bStockConfig.symbols[20:]
eastern = timezone('US/Eastern')
historyLength = 60
futureLength = 20
buyInThreshold = 0.0005
periodDay = 9

offset = 0*24*3600
period = periodDay*24*3600
oneWeekAgo = calendar.timegm(datetime.now(eastern).utctimetuple()) - period - offset
now = oneWeekAgo + period

def refreshStocks(col):
  global symbols
  stocks = {}
  for s in symbols:
    stocks[s] = []
  print "refreshing stocks..."
  for ti in col.find({"t": { "$in" : symbols },  "timestamp" : { "$gt" : oneWeekAgo, '$lt': now}}).sort("timestamp"):
    s = ti['t']
    pr = ti['l_cur']
    if isinstance(pr, unicode) :
      pr = float(pr.replace(',', ''))
    stocks[s].append( [ti['timestamp'], pr] )
  return stocks, {}

def calPriceDelta(stocks):
  priceDelta = {}
  for s in stocks:
    dateAndPrice = stocks[s]
    dateAndDeltaPrice = []
    cur = []
    for i in range(len(dateAndPrice)):
      if i == 0:
        continue
      timeDiff = dateAndPrice[i][0] - dateAndPrice[i-1][0]
      if timeDiff > 120:
        dateAndDeltaPrice.append(cur)
        cur = [];
      else:
        priceDeltaFloat = dateAndPrice[i][1] - dateAndPrice[i-1][1]
        cur.append([dateAndPrice[i][0], float(priceDeltaFloat)])
    if len(cur)>0 :
      dateAndDeltaPrice.append(cur)
    print "size of continous period:", s, "->", len(dateAndDeltaPrice), [ len(dd) for dd in dateAndDeltaPrice]
    priceDelta[s] = dateAndDeltaPrice
  return priceDelta

def applyThreshold(t1, t2, t3, num): # t1<t2<t3
  if num >= t3:
    return 1
  if num >= t2:
    return 2
  if num >= t1:
    return 3
  return 4

def genTrainingData(priceDelta, stocks):
  th = {}
  train = {}
  test = {}
  trainAll = {}
  gain = {}
  for s in priceDelta:
    data = []
    dataLastPeriod = []
    dataAll = []
    dateAndDeltaPrice = priceDelta[s]

    for periodIndex in range(len(dateAndDeltaPrice)):
      period = dateAndDeltaPrice[periodIndex]
      if (len(period) < historyLength+1):
        continue
      for start in range(len(period)-historyLength-futureLength):
        p = period[start:(start+historyLength)]
        numericP = period[(start+historyLength+futureLength)][1] - period[(start+historyLength)][1]
        dataline = [t[1] for t in p]
        if( all(v==0 for v in dataline)) :
          continue
        dataline.append(p[-1][0]%86400)
        dataline.append(numericP)
        if periodIndex == len(dateAndDeltaPrice)-1:
          dataLastPeriod.append(dataline)
        else :
          data.append(dataline)
    # find thresholds
    numericPDis = sorted([d[-1] for d in data])
    length = len(numericPDis)
    l1 = int(length*0.25)
    l2 = int(length*0.5)
    l3 = int(length*0.75)
    t1 = numericPDis[l1]
    t2 = numericPDis[l2]
    t3 = numericPDis[l3]
    gain4 = sum(numericPDis[:l1]) / l1
    gain3 = sum(numericPDis[l1:l2]) / (l2-l1)
    gain2 = sum(numericPDis[l2:l3]) / (l3-l2)
    gain1 = sum(numericPDis[l3:]) / len(numericPDis[l3:])
    gain[s] = [gain1, gain2, gain3, gain4] # from high to low
    print gain[s]
    for d in data:
      d.append(applyThreshold( t1, t2, t3, d[-1]))
    for d in dataLastPeriod:
      d.append(applyThreshold( t1, t2, t3, d[-1]))

    trainAll[s] = dataAll
    trainX = [ d[:-2] for d in data]
    trainY = [ d[-1] for d in data]
    train[s] = {"x": trainX, "y": trainY}

    testX = [ d[0:-2] for d in dataLastPeriod ]
    testY = [ d[-1]   for d in dataLastPeriod ]
    testP = [ d[-2]   for d in dataLastPeriod ]
    test[s] = {"x": testX, "y": testY, "p": testP}

    trainAll[s] = {"x": trainX + testX, "y": trainY + testY}
  return train, test, trainAll, gain

def simulate(clf, testX, testP, pri, gain1, onlybuy = True):
  pY = clf.predict_proba(testX)
  sum = 0
  tNo = 0
  tstr = '';
  #print 'buy threshold ($):', buyInThreshold * pri;
  if pY.shape[1] != 4 or pri > 150:
    return 0,0
  i = 0
  while i < len(pY):
    if pY[i][0] * gain1[0] + pY[i][1] * gain1[1] + pY[i][2]* gain1[2] + pY[i][3]* gain1[3] > max(buyInThreshold * pri, 0.02):
      sum += (testP[i] - 0.02)
      tNo += 1
      tstr += '+'
      i += 1
      #print i
    else:
      tstr += '*'
      i += 1
  #print tstr
  return tNo, sum/pri*1e2

def getModels(train, trainAll, test, stocks, gain1):
  classifiers = {}
  g = {}
  onum = 0;
  for s in train:
    clf = RandomForestClassifier(n_estimators=150)
    clf.fit(train[s]["x"], train[s]["y"])
    number, gain = simulate(clf, test[s]["x"], test[s]["p"], stocks[s][0][1], gain1[s], True)
    g[s] = gain
    print s, "-> score: ", clf.score(test[s]["x"], test[s]["y"]), \
      " simulated rev lastDay (long): ", number, gain, \
      " price: ", stocks[s][0][1]
    onum += number;
    clf = RandomForestClassifier(n_estimators=150)
    clf.fit(trainAll[s]["x"], trainAll[s]["y"])
    classifiers[s] = clf
  #xx = sorted(g.items(), key=operator.itemgetter(1), reverse=True)
  #print xx
  print "total gain:" , sum(g.values()), "with operation:", onum
  return (classifiers, gain1), g, onum


def runAnalysis(stocks):
  priceDelta = calPriceDelta(stocks)
  train, test, trainAll, gain1 = genTrainingData(priceDelta, stocks)
  classifiers, g, onum = getModels(train, trainAll, test, stocks, gain1)
  if onum == 0:
    return 0, 0;
  return sum(g.values())/onum, onum, classifiers

def runExp():
  global historyLength
  global futureLength
  global buyInThreshold
  client = MongoClient('mongodb://hongtao.cai.loves.sixin.li:27017')
  db = client.blind
  col = db.gstocks
  stocks, stockvars = refreshStocks(col)
  hl = [30, 60, 90]
  fl = [10, 20, 30]
  bl = [0.0004, 0.0005, 0.006]
  result = [];
  for h in hl:
    for f in fl:
      for b in bl:
        historyLength = h
        futureLength = f
        buyInThreshold = b
        t0, n0, tmp = runAnalysis(stocks)
        t1, n1, tmp = runAnalysis(stocks)
        t2, n2, tmp = runAnalysis(stocks)
        t3, n3, tmp = runAnalysis(stocks)
        t = t0*n0 + t1*n1 + t2*n2 + t3*n3
        n = n0 + n1 + n2 + n3
        if n != 0:
          t /= n
        else:
          t = 0
        result.append((h, f, b, t, n));
        print result
        print '='*20
  result = sorted(result, key=operator.itemgetter(3), reverse=True)
  print result;

def runSingle():
  global historyLength
  global futureLength
  global buyInThreshold
  historyLength = 60
  futureLength = 30
  buyInThreshold = 0.0005
  client = MongoClient('mongodb://hongtao.cai.loves.sixin.li:27017')
  db = client.blind
  col = db.gstocks
  stocks, stockvars = refreshStocks(col)
  t, n, clf = runAnalysis(stocks)
  pickle.dump( clf, open( "clf.clf", "wb" ) )
  return t, n, clf

if __name__ == '__main__':
  runSingle()