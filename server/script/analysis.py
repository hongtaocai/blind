__author__ = 'hcai'

from pymongo import MongoClient
import csv
from random import shuffle, sample
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import cross_val_score
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt

def convertOutcomeToClass(t, threshold):
  if t > threshold:
    return 1
  if t <= -threshold:
    return -1
  return 0

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

dateAndPrice = [];

historyLength = 20

for ti in col.find({ "t" : 'ALXN'}).sort("timestamp"):
  pr = ti['l_cur']
  if isinstance(pr, unicode):
    pr = float(pr.replace(',', ''))
  dateAndPrice.append([ti['timestamp'], pr])

#print dateAndPrice

dateAndDeltaPrice = [];
cur = [];

for i in range(len(dateAndPrice)):
  if i == 0:
    continue
  timeDiff = dateAndPrice[i][0] - dateAndPrice[i-1][0]
  if timeDiff > 120:
    dateAndDeltaPrice.append(cur)
    cur = [];
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
  for start in range(len(period)-historyLength-1):
    p = period[start:(start+historyLength+1)]
    dataline = [t[1] for t in p]
    if( all(v==0 for v in dataline)) :
      continue
    pp = dataline[-1]
    c = convertOutcomeToClass(dataline[-1], 0.2)
    #print c
    dataline[-1] = p[-1][0]%86400
    dataline.append(c)
    data.append(dataline)
    if c == 0 :
      stay.append(dataline)
      stayp.append(pp)
    elif c== 1:
      up.append(dataline)
      upp.append(pp)
    elif c==-1:
      down.append(dataline)
      downp.append(pp)

l = int(min(len(stay), len(up), len(down))*0.6)

stay1, stay1test, stayprice = subarray(stay, l, stayp)
up1, up1test, upprice = subarray(up, l, upp)
down1, down1test, downprice = subarray(down, l, downp)

print len(stay), " ", len(up), " ", len(down)

data1 = []
data1.extend(stay1)
data1.extend(up1)
data1.extend(down1)
shuffle(data1)

X = []
Y = []
for d in data1:
  X.append(d[:-1])
  Y.append(d[-1])

data = []
data.extend(stay1test)
data.extend(up1test)
data.extend(down1test)
price = []
price.extend(stayprice)
price.extend(upprice)
price.extend(downprice)

XData = []
YData = []
for d in data:
  XData.append(d[:-1])
  YData.append(d[-1])

clf = RandomForestClassifier(n_estimators=140)
clf.fit(X,Y)

scores = cross_val_score(clf, X, Y)
print scores.mean()

YPre = clf.predict(XData)

sum = 0.0;

for i in range(len(XData)):
  if YPre[i] == 1:
    sum += price[i]
  elif YPre[i] == -1:
    sum -= price[i]

print "sum:", sum

cm = confusion_matrix(YData, YPre)

print cm

plt.matshow(cm)
plt.title('Confusion matrix')
plt.colorbar()
plt.ylabel('True label')
plt.xlabel('Predicted label')
plt.show()


f = open("output.csv", "wb")
writer = csv.writer(f)
writer.writerow(range(len(data1[0])))
writer.writerows(data1)
