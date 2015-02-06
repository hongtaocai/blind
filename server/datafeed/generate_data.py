import yahoostockquote
from datetime import datetime
from pytz import timezone
import time
import json
import bStockConfig
import calendar
import pymongo
import deployConfig
import googlefinance
import endpoints
import sys

__author__ = 'hongtaocai'

# constants
eastern = timezone('US/Eastern')
historyLength = 30

# variables
minuteDataReady = {}
dayModeled = {}

clfs = {}


def isTradingHour(timeNow):
    #print timeNow.weekday();
    #print timeNow.hour;
    #print timeNow.minute;
    if(timeNow.weekday() > 4 ):
        return False
    if(timeNow.hour < 9):
        return False
    if(timeNow.hour >= 16):
        return False
    if(timeNow.hour == 9 and timeNow.minute < 30):
        return False
    return True

def shouldCrawlNow(timeNow):
    global eastern
    global minuteDataReady
    if not isTradingHour(timeNow):
        return False
    if(timeNow.minute in minuteDataReady):
        return False
    minuteDataReady.clear()
    minuteDataReady[timeNow.minute] = True
    return True

def shouldbuildModelNow(timeNow):
    global eastern
    global dayModeled
    if ( (not timeNow.day in dayModeled) and timeNow.hour == 0 and timeNow.minute == 0) :
      dayModeled.clear()
      dayModeled[timeNow.day] = True
      return True
    return False

def insertIntoDatabase(client, gdata, ydata):
    if (deployConfig.env == 'dev'):
        db = client.blindDev
        if(not ydata is None and len(ydata)>0):
            db.stocks.insert(ydata)
        if(not gdata is None and len(gdata)>0):
            db.gstocks.insert(gdata)
    if (deployConfig.env == 'prod'):
        db = client.blind
        if(not ydata is None and len(ydata)>0):
            db.stocks.insert(ydata)
        if(not gdata is None and len(gdata)>0):
            db.gstocks.insert(gdata)

def insertIntoDatabase(client, pp):
    if (deployConfig.env == 'dev'):
        db = client.predictedDev
        db.gstocks.insert(pp);
    if (deployConfig.env == 'prod'):
        db = client.predicted
        db.gstocks.insert(pp);

def generateHistoryPrice():
    historyPrice = {}
    for s in bStockConfig.symbols:
        historyPrice[s] = [];
    return historyPrice

def addToHistoryPrice(historyPrice, gdata):
    if gdata == None:
        return 0
    l = 0
    for gdataStock in gdata:
        sym = gdataStock[u't']
        historyPrice[sym].append(gdataStock)
        l = len(historyPrice[sym])
        if l > historyLength+1 :
            historyPrice[sym] = historyPrice[sym][:(historyLength+1)]
            l = historyLength+1
    return l

def predictPrice(historyPrice, timeNow, clfs):
    timestamp = calendar.timegm(timeNow.utctimetuple())
    predicted = {'timestamp': timestamp+60, 'predictedprices': {}}
    for s in historyPrice:
      f_diff = [j-i for i, j in zip(historyPrice[s][:-1], historyPrice[s][1:])];
      f_timeNow = (timestamp + 60)%86400
      f = f_diff;
      f.append(f_timeNow)
      predicted['predictedprices'][s] = clfs[s].predict(f)
    return predicted

def run():
    global eastern
    global clfs
    historyPrice = generateHistoryPrice()
    client  = pymongo.MongoClient(deployConfig.mongoHost, deployConfig.mongoPort);
    while(True):
        timeNow = datetime.now(eastern)
        if(shouldCrawlNow(timeNow)):
            googledata = None
            yahoodata = None
            try:
                googledata = googlefinance.get_stock_realtime_data(bStockConfig.symbols, timeNow)
            except:
                print "Google Error:" , sys.exc_info()[0]
                googledata = None
            try:
                yahoodata = yahoostockquote.get_stock_realtime_data(bStockConfig.symbols, timeNow)
            except:
                print "Yahoo Error:" , sys.exc_info()[0]
                yahoodata = None
            print str(timeNow) + ' (EST) write to database..'
            insertIntoDatabase(client=client, gdata=googledata, ydata=yahoodata);
            if addToHistoryPrice(historyPrice, googledata) == historyLength+1 and clfs != {}:
                pp = predictPrice(historyPrice, timeNow, clfs)
                insertIntoDatabase(client, pp)
        else:
            time.sleep(1);

if __name__ == "__main__":
    run()
