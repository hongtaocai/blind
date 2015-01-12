__author__ = 'hcai'

from bStockConfig import symbols
from pymongo import MongoClient
from pytz import timezone
from datetime import datetime
import calendar
import numpy as np
import operator
from random import sample, shuffle
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import cross_val_score

#symbols = ['ALXN']
eastern = timezone('US/Eastern')
historyLength = 30
topNStocks = 10
thresholdPercent = 0.2 # %

clfs = {}

def getThreshold(symbol, stocks):
  return stocks[symbol][0][1] * thresholdPercent / 100.0

def convertNumericToNorm(t, threshold):
  if t > threshold:
    return 1
  if t <= -threshold:
    return -1
  return 0

def refreshStocks(col):
  timeNow = datetime.now(eastern)
  oneWeekAgo = calendar.timegm(timeNow.utctimetuple()) - 7*24*3600
  stocks = {}
  stockvars = {}
  for s in symbols:
    stock = []
    stockpr = []
    for ti in col.find({ "t" : s, "timestamp" : { "$gt" : oneWeekAgo, '$lt': oneWeekAgo + 7*24*3600}}).sort("timestamp"):
      pr = ti['l_cur']
      if isinstance(pr, unicode) :
        pr = float(pr.replace(',', ''))
      stock.append( [ti['timestamp'], pr] )
      stockpr.append(pr)
    stocks[s] = stock
    stockvars[s] = np.std(stockpr)/stockpr[0]
    print 'var:', s ,':', stockvars[s]
  return stocks, stockvars

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

def extractDataOfSameLength(data) :
  l = min(len(data[0]) , len(data[1]), len(data[-1]))
  sampleData = sample(data[0], l) + sample(data[1], l) + sample(data[-1], l)
  shuffle(sampleData)
  X = [ d[0:-2] for d in sampleData]
  Y = [ d[-2]   for d in sampleData]
  P = [ d[-1]   for d in sampleData]
  return {"x": X, "y": Y, "p": P}

def genTrainingData(priceDelta, stocks):
  th = {}
  train = {}
  test = {}
  trainAll = {}
  for s in priceDelta:
    data = {1: [], -1:[], 0:[]}
    dataLastPeriod = []
    dataAll = {1: [], -1:[], 0:[]}
    dateAndDeltaPrice = priceDelta[s]
    th[s] = getThreshold(s, stocks)
    for periodIndex in range(len(dateAndDeltaPrice)):
      period = dateAndDeltaPrice[periodIndex]
      if (len(period) < historyLength+1):
        continue
      for start in range(len(period)-historyLength-1):
        p = period[start:(start+historyLength+1)]
        dataline = [t[1] for t in p]
        if( all(v==0 for v in dataline)) :
          continue
        numericP = dataline[-1];
        c = convertNumericToNorm(numericP, th[s])
        dataline[-1] = (p[-1][0]%86400)
        dataline.append(c)
        dataline.append(numericP)
        if periodIndex == len(dateAndDeltaPrice)-1:
          dataLastPeriod.append(dataline)
        else :
          data[c].append(dataline)
        dataAll[c].append(dataline)
    train[s] = extractDataOfSameLength(data)
    trainAll[s] = extractDataOfSameLength(dataAll)
    testX = [ d[0:-2] for d in dataLastPeriod ]
    testY = [ d[-2]   for d in dataLastPeriod ]
    testP = [ d[-1]   for d in dataLastPeriod ]
    test[s] = {"x": testX, "y": testY, "p": testP}
  return train, test, trainAll, th

def simulate(clf, testX, testP, pri, onlybuy = True):
  pY = clf.predict(testX)
  sum = 0
  tNo = 0
  for i in range(len(pY)):
    if pY[i] == 1:
      sum += testP[i]
      tNo += 1
    elif pY[i] == -1 and not onlybuy:
      sum -= testP[i]
      tNo += 1
  return tNo, sum/pri*1e2

def getModels(train, trainAll, test, stocks):
  classifiers = {}
  for s in train:
    if len(train[s]['x']) == 0 :
      continue
    clf = RandomForestClassifier(n_estimators=150)
    clf.fit(train[s]["x"], train[s]["y"])
    print s, "-> score: ", clf.score(test[s]["x"], test[s]["y"]), \
      " simulated rev lastDay (long): ", simulate(clf, test[s]["x"], test[s]["p"], stocks[s][0][1], True), \
      " (long&short): ", simulate(clf, test[s]["x"], test[s]["p"], stocks[s][0][1], False), \
      " price: ", stocks[s][0][1]
    clf = RandomForestClassifier(n_estimators=150)
    clf.fit(trainAll[s]["x"], trainAll[s]["y"])
    classifiers[s] = clf
  return classifiers

def run():
  global clfs
  client = MongoClient('mongodb://hongtao.cai.loves.sixin.li:27017')
  db = client.blind
  col = db.gstocks
  stocks, stockvars = refreshStocks(col)
  topKHightVarStocks = sorted(stockvars.items(), key=operator.itemgetter(1))
  topKHightVarStocks = topKHightVarStocks[-topNStocks:-1]
  print topKHightVarStocks
  priceDelta = calPriceDelta(stocks)
  train, test, trainAll, th = genTrainingData(priceDelta, stocks)
  clfs = getModels(train, trainAll, test, stocks)

run()
