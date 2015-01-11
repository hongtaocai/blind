__author__ = 'hcai'

from pymongo import MongoClient
import csv
from bStockConfig import symbols
import scipy

def convertOutcomeToClass(t, threshold):
  if t > threshold:
    return 1
  if t <= -threshold:
    return -1
  return 0

client = MongoClient('mongodb://hongtao.cai.loves.sixin.li:27017')
db = client.blind
col = db.gstocks

historyLength = 30

v_d_list = [];

for symbol in symbols:
  dateAndPrice = [];
  for ti in col.find({ "t" : symbol}).sort("timestamp"):
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
      cur.append([dateAndPrice[i][0], (float(priceDelta) / dateAndPrice[i-1][1])])

  if len(cur)>0 :
    dateAndDeltaPrice.append(cur)

  #print len(dateAndDeltaPrice)
  #print [(len(t)) for t in dateAndDeltaPrice]

  data = []

  for period in dateAndDeltaPrice:
    if (len(period) < historyLength+1):
      continue
    for start in range(len(period)-historyLength-1):
      p = period[start:(start+historyLength+1)]
      dataline = [t[1] for t in p]
      if( all(v==0 for v in dataline)) :
        continue
      #dataline.append(convertOutcomeToClass(dataline[-1], 0.01))
      data.append(dataline)

  vd = [ d[-1] for d in data]
  print symbol, "\t", scipy.var(vd)
  v_d_list.append((symbol, scipy.var(vd)))

  #print (len(data))
  #print (len(data[0]))

v_d_list = sorted(v_d_list, key=lambda x: x[1])
print v_d_list

# f = open("output.csv", "wb")
# writer = csv.writer(f)
# writer.writerow(range(len(data[0])))
# writer.writerows(data)
