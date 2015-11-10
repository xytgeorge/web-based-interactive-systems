from elasticsearch import Elasticsearch
from datetime import datetime 
from collections import Counter
es = Elasticsearch()

# dsl generation for aggregation
def product_aggs(productid):
    dsl = {
        "query" : {
            "match" : {
                "product/productId" : productid
            }
        },
        "aggs" : {
            "avg_score" : {
                "avg" : {
                    "field" : "review/score"
                }
            },
            "earliest_post" : {
                "min" : {
                    "field" : "review/time"
                }
            }
        }
    }
    return dsl

def userquery(userid):
    dsl = {
        "query" : {
            "match" : {
                "review/userId" : userid 
            }
        }
    }
    return dsl

def spammer_detect(userid, min_post, early_constraint):
    # get all the reviews of the user
    res = es.search(index = "amazon_reviews", doc_type = "reviews", size = 10000, 
                    body = userquery(userid))

    # if the number user's reviews > min_post, start to judge 
    if int(res["hits"]["total"]) < min_post:
        print "unable to judge"
    else:
        seen = set()
        review_list = [review["_source"] for review in res["hits"]["hits"]  \
            if review["_source"]["product/productId"] not in seen \
            and not seen.add(review["_source"]["product/productId"])]
        #review_list = [review["_source"] for review in res["hits"]["hits"]]
        user_scores = [] # all the scores the user gave
        user_post_time = [] # list of review time of the user
        avg_score = [] # list of average scores of all the products the user reviewed 
        earliest_post = [] # list of earliest review time of all the products the user reviewed 
        for review in review_list:
            productid = review["product/productId"]
            result = es.search(index = "amazon_reviews", doc_type = "reviews", search_type = "count", 
                            body = product_aggs(productid))
            avg_score.append(result["aggregations"]["avg_score"]["value"])
            earliest_post.append(int(result["aggregations"]["earliest_post"]["value"]))
            user_scores.append(float(review["review/score"]))
            user_post_time.append(int(review["review/time"]))
        # print user_scores, user_post_time, avg_score, earliest_post
        deviation = sum(list(map(lambda x: abs(x[0]-x[1])/4.0, 
                                 zip(user_scores, avg_score))))/len(avg_score)
        early_rate = 1.0*sum(list(map(lambda x: 1 if x[0]-x[1]<early_constraint else 0, 
                              zip(user_post_time, earliest_post))))/len(user_post_time)
        # print "deviation: ", deviation
        # print "rate of early post: ", early_rate
        
        ## Reviewing Burstiness (BST): spammers are usually not longtime members of a site
        reviews_time = [review["review/time"] for review in review_list]
        latest = max(reviews_time)
        oldest = min(reviews_time)
        time_diff = int(latest) - int(oldest)
        # print latest, oldest, time_diff
        
        ## Maximum Number of Reviews (MNR): Posting many reviews in a single day
        reviews_date = [datetime.fromtimestamp(int(rev_time)).strftime('%Y-%m-%d') for rev_time in reviews_time]
        # print reviews_date
        reviews_count = Counter(reviews_date).most_common(1)
        # print reviews_count
        # print "This user posted at most", reviews_count[0][1], "reviews in a single day"
        
        ## Extreme Rating (EXT): spammers are likely to give extreme ratings (1 or 5). 
        reviews_rates = [review["review/score"] for review in review_list]
        reviews_score = dict(Counter(reviews_rates))
        score1_no = 0 # number of 1-star rates the user gave
        score5_no = 0 # number of 5-star rates the user gave
        if reviews_score.has_key(1.0):
            score1_no = float(reviews_score[1.0])
        if reviews_score.has_key(5.0):
            score5_no = float(reviews_score[5.0])
        #ext_rate = score1_no/res["hits"]["total"] + score5_no/res["hits"]["total"] 
        ext_rate = score1_no/len(review_list) + score5_no/len(review_list) 
        #print "scores: ", reviews_score, score1_no, score5_no
        #print "percentage of 1-rate and 5-rate: "
        #print score1_no/res["hits"]["total"], score5_no/res["hits"]["total"] 
        
        return {"deviation" : deviation, "early_rate" : early_rate, "time_diff" : time_diff, "ext_rate" : ext_rate, "reviews_count" : reviews_count[0][1]}
        

def metrics(detection_dict):
    metric = 0
    if detection_dict["dup_no"]> 5:
        metric += 1
    if detection_dict["ext_rate"]> 0.8 and detection_dict["reviews_count"]>5:
        metric += 1
    if detection_dict["time_diff"]< 3600*24*7 and detection_dict["reviews_count"]>5:
        metric += 1
    if detection_dict["early_rate"]> 0.8 and detection_dict["reviews_count"]>5:
        metric += 1
    if detection_dict["deviation"]> 0.5 and detection_dict["reviews_count"]>5:
        metric += 1
    return metric  

def metrics2(detection_dict):
    metric = 0
    if detection_dict["reviews_count"]>10:
        metric += 1
    if detection_dict["ext_rate"]> 0.8 and detection_dict["reviews_count"]>5:
        metric += 1
    if detection_dict["time_diff"]< 3600*24*7 and detection_dict["reviews_count"]>5:
        metric += 1
    if detection_dict["early_rate"]> 0.8 and detection_dict["reviews_count"]>5:
        metric += 1
    if detection_dict["deviation"]> 0.5 and detection_dict["reviews_count"]>5:
        metric += 1
    return metric 
