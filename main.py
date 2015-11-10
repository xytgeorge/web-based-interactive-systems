from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from flask.ext.pymongo import PyMongo
from flask.ext.elastic import Elastic
import json
import dup, dev, splist, search

app = Flask(__name__)
 

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/new_review")
def new_review():
    return render_template("detection.html")

@app.route("/detection_result", methods=['POST'])
def spammer_detection():
    # here to detect if the new review is a spam
    #return request.form["title"]
    min_score = 1
    dup_no = dup.dup(min_score, request.form["text"])
    # userid = "ALYU98KL3VUGF"/A1GLC0S9H532IU
    min_post = 1
    early_constraint = 3600*24*180 # (sec*min)*hours*days*months
    detection_dict = dev.spammer_detect(request.form["userid"], min_post, early_constraint)
    #return str(devnrep_dict["time_diff"])
    detection_dict["dup_no"] = dup_no
    detection_dict["metric"] = dev.metrics(detection_dict) 
    #print detection_dict
    return render_template("result.html", result = detection_dict)

@app.route("/search_review")
def review():
    return render_template("search.html")

@app.route("/search_result", methods=['POST'])
def search_result():
    search_dict = search.search(request.form["query"])
    #print request.form["query"]
    #print search_dict
    return render_template("searchresult.html", result = search_dict)

@app.route("/search_spammer", methods=['GET'])
def search_spammer():
    # here to detect if the new review is a spam
    #return request.form["title"]
    min_score = 1
    dup_no = dup.dup(min_score, request.args.get["text"])
    # userid = "ALYU98KL3VUGF"/A1GLC0S9H532IU
    min_post = 1
    early_constraint = 3600*24*180 # (sec*min)*hours*days*months
    detection_dict = dev.spammer_detect(request.args.get["userid"], min_post, early_constraint)
    #return str(devnrep_dict["time_diff"])
    detection_dict["dup_no"] = dup_no
    detection_dict["metric"] = dev.metrics(detection_dict) 
    #print detection_dict
    return render_template("result.html", result = detection_dict)

@app.route('/spammers')
def list_spammer():
    plist = splist.splist()
    return render_template('spammer.html',
                           spammers=plist['hits'])

@app.route("/spammer_detail", methods=['GET'])
def spammer_detail():
    spammer_id = request.args.get('id', '')
    # return results from elasticsearch
    spammer_info = splist.spammer_info(spammer_id)
    spammer_reviews = splist.spammer_reviews(spammer_id)
    #print spammer_reviews[0]["review/title"]
    spammer_info["spammer_reviews"] = spammer_reviews
    #print spammer_info["spammer_reviews"]
    return render_template('spammer_detail.html',
                           spammer_info = spammer_info)

if __name__ == "__main__":
    # configuration
    app.config.update(
        DEBUG = True,
        MONGO_DBNAME = "amazon_reviews"
    ) 
    elastic = Elastic(app)
    mongo = PyMongo(app)
    app.run()

