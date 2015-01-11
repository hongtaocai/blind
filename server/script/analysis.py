__author__ = 'hcai'

from pymongo import MongoClient
import csv
from random import shuffle, sample

def convertOutcomeToClass(t, threshold):
  if t > threshold:
    return 1
  if t <= -threshold:
    return -1
  return 0

client = MongoClient('mongodb://hongtao.cai.loves.sixin.li:27017')

db = client.blind
col = db.gstocks

dateAndPrice = [];

historyLength = 30

for ti in col.find({ "t" : 'ALXN'}).sort("timestamp"):
  pr = ti['l_cur']
  if isinstance(pr, unicode) :
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
    cur.append([dateAndPrice[i][0], priceDelta*(1e2)/dateAndPrice[i-1][1]])

if len(cur)>0 :
  dateAndDeltaPrice.append(cur)

print len(dateAndDeltaPrice)
print [(len(t)) for t in dateAndDeltaPrice]

stay = []
down = []
up = []

for period in dateAndDeltaPrice:
  if (len(period) < historyLength+1):
    continue
  for start in range(len(period)-historyLength-1):
    p = period[start:(start+historyLength+1)]
    dataline = [t[1] for t in p]
    if( all(v==0 for v in dataline)) :
      continue
    c = convertOutcomeToClass(dataline[-1], 0)
    #print c
    dataline.append(c)
    #data.append(dataline)
    if c == 0 :
      stay.append(dataline)
    elif c== 1:
      up.append(dataline)
    elif c==-1:
      down.append(dataline)

#l = min(len(stay), len(up), len(down))
#stay = [ stay[i] for i in sorted(sample(xrange(len(stay)), l)) ]
l = min(len(up), len(down))
up = [ up[i] for i in sorted(sample(xrange(len(up)), l)) ]
down = [ down[i] for i in sorted(sample(xrange(len(down)), l)) ]


print len(stay), " ", len(up), " ", len(down)

data = []
data.extend(stay)
data.extend(up)
data.extend(down)
shuffle(data)

f = open("output.csv", "wb")
writer = csv.writer(f)
writer.writerow(range(len(data[0])))
writer.writerows(data)
