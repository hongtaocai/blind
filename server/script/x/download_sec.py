import os
from urllib2 import urlopen, URLError, HTTPError

secSymbols = ['XLY',  # XLY Consumer Discrectionary SPDR Fund
             'XLF',  # XLF Financial SPDR Fund
             'XLK',  # XLK Technology SPDR Fund
             'XLE',  # XLE Energy SPDR Fund
             'XLV',  # XLV Health Care SPRD Fund
             'XLI',  # XLI Industrial SPDR Fund
             'XLP',  # XLP Consumer Staples SPDR Fund
             'XLB',  # XLB Materials SPDR Fund
             'XLU']  # XLU Utilities SPRD Fund

def buildYahooURL(symbol):
  return 'http://ichart.yahoo.com/table.csv?s=' + symbol + '&a=0&b=1&c=2013&d=0&e=15&f=2015&g=d&ignore=.csv'

def dlfile(symbol):
  # Open the url
  url = buildYahooURL(symbol)
  try:
    f = urlopen(url)
    print "downloading " + url

    # Open our local file for writing
    with open(symbol + '.csv', "wb") as local_file:
      local_file.write(f.read())

    #handle errors
  except HTTPError, e:
    print "HTTP Error:", e.code, url
  except URLError, e:
    print "URL Error:", e.reason, url

def dlAll():
  for s in secSymbols:
    dlfile(s)


if __name__ == '__main__':
  dlAll()


