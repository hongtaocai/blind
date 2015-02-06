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

eastern = timezone('US/Eastern')

def convertOutcomeToClass(t, threshold):
  if t > threshold:
    return 1
  if t > 0:
    return 2
  if t > -threshold:
    return 3
  return 4

def subarray(arr, n, pr):
  train = []
  test = []
  testprice = []
  ind = sample(xrange(len(arr)), n)
  for i in xrange(len(arr)):
    if i in ind:
      train.append(arr[i])
    else:
      test.append(arr[i])
      testprice.append(pr[i])
  return train, test, testprice

client = MongoClient('mongodb://hongtao.cai.loves.sixin.li:27017')

db = client.blind
col = db.gstocks

dateAndPrice = []

historyLength = 60
futureLength = 30
thth = 0.09
stocksymbol = 'CTSH'
oneWeekAgo = calendar.timegm(datetime.now(eastern).utctimetuple()) - 14*24*3600

for ti in col.find({ "t" : stocksymbol, "timestamp" : { "$gt" : oneWeekAgo, '$lt': oneWeekAgo + 14*24*3600}}).sort("timestamp"):
  pr = ti['l_cur']
  if isinstance(pr, unicode):
    pr = float(pr.replace(',', ''))
  dateAndPrice.append([ti['timestamp'], pr])

dateAndDeltaPrice = [];
cur = [];

for i in range(len(dateAndPrice)):
  if i == 0:
    continue
  timeDiff = dateAndPrice[i][0] - dateAndPrice[i-1][0]
  if timeDiff > 120:
    dateAndDeltaPrice.append(cur)
    cur = []
  else:
    priceDelta = dateAndPrice[i][1] - dateAndPrice[i-1][1]
    cur.append([dateAndPrice[i][0], priceDelta])

if len(cur)>0 :
  dateAndDeltaPrice.append(cur)

print len(dateAndDeltaPrice)
print [(len(t)) for t in dateAndDeltaPrice]

stay = []
down = []
up = []
stayp = []
downp = []
upp = []

data = []
price = []

for period in dateAndDeltaPrice:
  if (len(period) < historyLength+1):
    continue
  for start in range(len(period)-historyLength-futureLength):
    p = period[start:(start+historyLength)]
    cc = period[(start+historyLength+futureLength)][1] - period[(start+historyLength)][1]
    #print cc;
    dataline = [t[1] for t in p]
    if( all(v==0 for v in dataline)) :
      continue
    c = convertOutcomeToClass(cc, thth)
    #print c
    dataline.append((p[-1][0]+60)%86400)
    dataline.append(cc)
    dataline.append(c)
    data.append(dataline)
#     if c== 1:
#       up.append(dataline)
#       upp.append(cc)
#     elif c==-1:
#       down.append(dataline)
#       downp.append(cc)
#
# l = int(min(len(up), len(down))*0.5)
#
# up1, up1test, upprice = subarray(up, l, upp)
# down1, down1test, downprice = subarray(down, int(len(down)*0.5), downp)
#
# print "size of up and down", len(up), len(down)
#
# data1 = []
# data1.extend(up1)
# data1.extend(down1)
# shuffle(data1)
#
# X = []
# Y = []
# for d in data1:
#   X.append(d[:-1])
#   Y.append(d[-1])
#
# data = []
# data.extend(up1test)
# data.extend(down1test)
# price = []
# price.extend(upprice)
# price.extend(downprice)
#
XData = []
YData = []
for d in data:
  XData.append(d[:-2])
  YData.append(d[-1])

X_train, X_test, y_train, y_test = train_test_split(XData, YData, test_size=0.4, random_state=0)

clf = RandomForestClassifier(n_estimators=140)
clf.fit(X_train, y_train)

print clf.score(X_test, y_test)

YPro = clf.predict_proba(X_test)
print clf.classes_
print YPro

buyIndex = []

for i in range(len(YPro)):
  pp = YPro[i][0] * 0.25 + YPro[i][1] * 0.04 - YPro[i][2] * 0.04 - YPro[i][3] * 0.25
  if pp > 0.07:
    buyIndex.append(i);

print "buy index size:", len(buyIndex)

money = 0.0

for i in buyIndex:
  if y_test[i] == 1:
    money += 0.23
  elif y_test[i] == 2:
    money += 0.02
  elif y_test[i] == 3:
    money += -0.06
  elif y_test[i] == 4:
    money += -0.27

print "money:", money
#
# scores = cross_val_score(clf, X, Y)
# print scores.mean()
#
# YPre = clf.predict(XData)
#
# YPro = clf.predict_proba(XData)
# print YPro
#
# sum1 = 0.0;
# number = 0;
# trade = []
#
# for i in range(len(XData)):
#   if YPro[i][1] > 0.75:
#     trade.append(price[i])
#     sum1 += price[i]
#     number += 1;
#   #elif YPre[i] == -1:
#   #  sum -= price[i]
#
# print "sum:", sum1, " num:", number
# print trade
#
# cm = confusion_matrix(YData, YPre)
# #
# print cm
#
# plt.matshow(cm)
# plt.title('Confusion matrix')
# plt.colorbar()
# plt.ylabel('True label')
# plt.xlabel('Predicted label')
# plt.show()

f = open("output.csv", "wb")
writer = csv.writer(f)
writer.writerow(range(len(data[0])))
writer.writerows(data)

futureData = [ d[61] for d in data ]
futureData = sorted(futureData)
l = len(futureData)
print l
print futureData[int(l*0.25)], futureData[int(l*0.5)], futureData[int(l*0.75)], futureData[int(l-1)]

print sum(futureData[0:int(l*0.25)])/(l*0.25)
print sum(futureData[int(l*0.25):int(l*0.5)])/(l*0.25)
print sum(futureData[int(l*0.5):int(l*0.75)])/(l*0.25)
print sum(futureData[int(l*0.75):])/(l*0.25)
