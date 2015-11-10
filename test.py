def userquery(userid):
    dsl = {
        "query" : {
            "match" : {
                "review/userId" : userid 
            }
        }
    }
    return dsl

# here to test the mongodb
@app.route('/review')
def show_review():
    online_users = mongo.db.reviews.find({'review/userId': 'A2F6FARSB1VL6Q'})
    for user in online_users:
        print user
    return "test"

# here to test the elasticsearch
@app.route("/estest")
def estest():
    res = elastic.search(index = "amazon", doc_type = "reviews", size = 10000, 
                        body = userquery("ALYU98KL3VUGF"))
    return json.dumps(res)
    
