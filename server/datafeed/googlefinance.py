from urllib2 import Request, urlopen
import json
import calendar

def _build_url(symbols):
    symbol_list = ','.join(['%22'+symbol+'%22' for symbol in symbols])
    return 'https://query.yahooapis.com/v1/public/yql?' \
        + 'q=select%20*%20from%20yahoo.finance.quotes%20' \
        + 'where%20symbol%20in%20(' \
        + symbol_list \
        + ')&format=json&diagnostics=true&' \
        + 'env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback='

def _request(symbols):
    url = _build_url(symbols)
    req = Request(url)
    resp = urlopen(req)
    content = resp.read().decode().strip()
    return content

def strToNumber(s):
    try:
        if (s==None):
            return s;
        f = float(s)
        return f
    except ValueError:
        return s

def convertStrValToNumber(obj):
    objNew = {}
    for key, val in obj.iteritems():
        objNew[key] = strToNumber(val)
    return objNew

def convertStrValToNumberList(objlist):
    objlistNew = [];
    for obj in objlist:
        objlistNew.append(convertStrValToNumber(obj))
    return objlistNew

def addTimeStamp(objList, timeStamp):
    for obj in objList:
        obj['hour'] = timeStamp.hour
        obj['minute'] = timeStamp.minute
        obj['day'] = timeStamp.day
        obj['month'] = timeStamp.month
        obj['year'] = timeStamp.year
        obj['weekday'] = timeStamp.weekday()
        obj['timestamp'] = calendar.timegm(timeStamp.utctimetuple())

def get_stock_realtime_data(symbols, timeStamp ):
    content = json.loads(_request(symbols))
    quotes = content['query']['results']['quote'];
    addTimeStamp(quotes, timeStamp)
    return convertStrValToNumberList(quotes)
