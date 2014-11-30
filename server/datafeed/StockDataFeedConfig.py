__author__ = 'hcai'

class StockDataFeedConfig:
  #
  #
  #
  #
  def __init__(
      self,
      mongoDBUsername,
      mongoDBPassword,
      stockSymbolList,
      interval=20):
    self.mongoDBUsername = mongoDBUsername
    self.mongoDBPassword = mongoDBPassword
    self.stockSymbolList = stockSymbolList
    self.interval = interval