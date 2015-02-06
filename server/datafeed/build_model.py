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
import pickle

#constant
eastern = timezone('US/Eastern')

#variable
dayModeled = {}

def shouldBuildModelNow(timeNow):
  global eastern
  global dayModeled
  if ((not timeNow.day in dayModeled)) :
    dayModeled.clear()
    dayModeled[timeNow.day] = True
    return True
  return False

def insertIntoDatabase(client, pp):
  if (deployConfig.env == 'dev'):
    db = client.simulatedGain
    db.gstocks.insert(pp);
  if (deployConfig.env == 'prod'):
    db = client.simulatedGain
    db.gstocks.insert(pp);

def run():
  client = pymongo.MongoClient(deployConfig.mongoHost, deployConfig.mongoPort);
  while True:
    timeNow = datetime.now(eastern)
    if shouldBuildModelNow(timeNow):
      clfs, gain = endpoints.trainClassifiers(client);
      insertIntoDatabase(client, {'date': timeNow.strftime('%Y%m%d'), 'gain': gain})
      pickle.dump(clfs, open("models/" + timeNow.strftime('%Y%m%d') + ".clf", "wb" ))
    else :
      time.sleep(1)
