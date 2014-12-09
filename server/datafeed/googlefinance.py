from urllib2 import Request, urlopen
import json
import calendar


'''
{'c': '-2.20',  # change
 'c_fix': '-2.20', # fixed change
 'ccol': 'chr',
 'cp': '-5.72', # change in percent
 'cp_fix': '-5.72', # change in percent fix
 'div': '',
 'e': 'NYSE',  #exchange
 'ec': '0.00',
 'ec_fix': '0.00',
 'eccol': 'chb',
 'ecp': '0.00',
 'ecp_fix': '0.00',
 'el': '36.29',
 'el_cur': '36.29',
 'el_fix': '36.29', # last trade price fix
 'elt': 'Dec 8, 7:59PM EST',
 'id': '32086821185414',
 'l': '36.29', # last trade price
 'l_cur': '36.29', # last trade price current
 'l_fix': '36.29', # last trade price current
 'lt': 'Dec 8, 4:00PM EST', # last trade price
 'lt_dts': '2014-12-08T16:00:08Z',
 'ltt': '4:00PM EST',
 'pcls_fix': '38.49', # previous close
 's': '2',
 't': 'TWTR',
 'yld': ''}
'''

def _build_url(symbols):
    symbol_list = ','.join([symbol for symbol in symbols])
    return 'http://finance.google.com/finance/info?client=ig&q=' \
        + symbol_list

def _request(symbols):
    url = _build_url(symbols)
    req = Request(url)
    resp = urlopen(req)
    content = resp.read().decode().strip()
    content = content[3:]
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
    quotes = content;
    addTimeStamp(quotes, timeStamp)
    return convertStrValToNumberList(quotes)
