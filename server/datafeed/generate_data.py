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

__author__ = 'hongtaocai'

eastern = timezone('US/Eastern')
secondDataReady = {}
timeNow = None

def isTradingHour(timeNow):
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
    if(timeNow.second in secondDataReady or timeNow.second%10 !=0):
        return False
    secondDataReady.clear()
    secondDataReady[timeNow.second] = True
    return True

def insertIntoDatabase(gdata, ydata, client):
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

def testShouldCrawlNow() :
    global eastern
    while(True) :
        timeNow = datetime.now(eastern)
        timeNow = timeNow.replace(year=2015, month=1, day=9, hour=10)
        assert(isTradingHour(timeNow))
        if not shouldCrawlNow(timeNow):
          print timeNow
          time.sleep(1);
        else:
          print "Database Operation"

def run():
    global eastern
    client  = pymongo.MongoClient(deployConfig.mongoHost, deployConfig.mongoPort);
    while(True):
        timeNow = datetime.now(eastern)
        if(not shouldCrawlNow(timeNow)):
            time.sleep(1);
        else:
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
            insertIntoDatabase(gdata=googledata, ydata=yahoodata, client = client);
            #analyze();

if __name__ == "__main__":
    run()
