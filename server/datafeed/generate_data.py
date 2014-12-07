import yahoostockquote
from datetime import datetime
from pytz import timezone
import time
import json
import bStockConfig
import calendar
import pymongo
import deployConfig

__author__ = 'hongtaocai'

eastern = timezone('US/Eastern')
minuteDataReady = {}
timeNow = None
client  = pymongo.MongoClient(deployConfig.mongoHost, deployConfig.mongoPort);

def isTradingHour(timeNow):
    if(timeNow.weekday > 4 ):
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
    if(minuteDataReady[timeNow.minute]):
        return False
    minuteDataReady.clear()
    minuteDataReady[timeNow.minute] = True
    return True

def insertIntoDatabase(data):
    if (deployConfig.env == 'dev'):
        db = client.blindDev
        db.stocks.insert(data)
    if (deployConfig.env == 'prod'):
        db = client.blind
        db.stocks.insert(data)

def run():
    global eastern
    while(True):
        timeNow = datetime.now(eastern)
        if(not shouldCrawlNow(timeNow)):
            time.sleep(1);
        else:
            data = yahoostockquote.get_stock_realtime_data(bStockConfig.symbols, timeNow)
            print str(timeNow) + ' (EST) write to database..'
            insertIntoDatabase(data)
            #analyze();

if __name__ == "__main__":
    run()

# insertIntoDatabase(data)
  #
  # def run(self):
  #   while(True):
      # while(not the first second of a minute)
      #   print 'wait: current time is'+ time
      #   sleep(1s)
      # print time
      # print 'start to fetch data'
      # post request
      # synchronsly wait for response
      # get response
      # write to database
      # read all data from database
      # write back prediction
      # train self.random Forest Model
      # save the self.Model

  # def statistics(self):
  #   while(true):
      # while(not the 31st second of a minute)
      #   print 'wait: current time is'+ time
      #   sleep(1s)
      # print time
      # print 'start to fetch data'
      # track the latest time stamp
      # read new data from database
      # aggregate and check errorRate
      # write back errorRate
      # train self.random Forest Model
      # save the self.Model