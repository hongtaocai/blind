from flask import Flask, render_template
import pymongo

app = Flask(__name__)
client  = pymongo.MongoClient('blog.hcai.me', 27017);

@app.route("/")
def index():
  return render_template("base.html")

@app.route("/stocks")
def getStocks():
  return "Hello World"

@app.route("/isReady")
def isReady():
  client.count({})
  return True

if __name__ == "__main__":
  app.run()