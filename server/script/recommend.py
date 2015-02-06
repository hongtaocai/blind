import pickle

from sklearn.ensemble import RandomForestClassifier
from pymongo import MongoClient
import calendar
from datetime import datetime
from pytz import timezone
import operator
import bStockConfig
import pickle
import time
import pync

symbols = bStockConfig.symbols[20:]
eastern = timezone('US/Eastern')

historyLength = 60
futureLength = 30
buyInThreshold = 0.0005
year = datetime.now(eastern).year
month = datetime.now(eastern).month
today = datetime.now(eastern).day

def refreshStocks(col):
  global symbols
  stocks = {}
  for s in symbols:
    stocks[s] = []
  #print "refreshing stocks..."
  for ti in col.find({"t": { "$in" : symbols },  "day": today, "year": year, "month": month}).sort("timestamp"):
    s = ti['t']
    pr = ti['l_cur']
    if isinstance(pr, unicode) :
      pr = float(pr.replace(',', ''))
    stocks[s].append( [ti['timestamp'], pr] )
  return stocks

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
    #print "size of continous period:", s, "->", len(dateAndDeltaPrice), [ len(dd) for dd in dateAndDeltaPrice]
    priceDelta[s] = dateAndDeltaPrice
  return priceDelta

def predict(priceDelta, stocks, clf, gain):
  if len(priceDelta[symbols[0]]) < 1:
    return []
  if len(priceDelta[symbols[0]][0]) < historyLength:
    return []
  stBuy = []
  for s in symbols:
    if stocks[s][0][1] > 150:
      continue
    if s not in clf:
      continue
    if s not in gain:
      continue
    gain1 = gain[s]
    pd = priceDelta[s][0][-61:-1]
    #print pd
    features = [ st[1] for st in pd]
    features.append(pd[-1][0]%86400)
    Y = clf[s].predict_proba([features])
    pY = Y[0]
    if len(pY) != 4:
      continue
    if pY[0] * gain1[0] + pY[1] * gain1[1] + pY[2]* gain1[2] + pY[3]* gain1[3] > max(buyInThreshold * stocks[s][0][1], 0.02):
      stBuy.append(s)
  return stBuy

if __name__ == '__main__':
  print "loading classifier"
  clf, gain = pickle.load( open( "clf.clf", "rb" ) )
  #print gain
  client = MongoClient('mongodb://hongtao.cai.loves.sixin.li:27017')
  db = client.blind
  col = db.gstocks
  while True:
    stocks = refreshStocks(col)
    priceDelta = calPriceDelta(stocks)
    stBuy = predict(priceDelta, stocks, clf, gain)
    timenow = datetime.now(eastern).strftime("%D %H %M %S")
    print timenow, stBuy
    if len(stBuy)>0:
      pync.Notifier.notify('stocks:' + str(stBuy))
    time.sleep(15)
