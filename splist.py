from elasticsearch import Elasticsearch
es = Elasticsearch()

# duplication detection, return the number of duplicated items
def splist():
    dsl = {
        "query" : 
        {
            "range": {
                "reviews_count": { "gt" : 9  }
            }

        },
        "sort" : [
            { 
                "reviews_count": {"order": "desc"},
                "ext_rate" : {"order" : "desc"}
            }
        ]
    }
    return es.search(index="amazon_reviews", doc_type="spammers",
                     body= dsl, size = 150)["hits"]

def spammer_info(spammer_id):
    dsl = {
        "query" : 
        {
            "match": {
                "_id": spammer_id
            }
        }
    }
    res = es.search(index="amazon_reviews", doc_type="spammers",
                         body= dsl)["hits"]
    
    if res["total"] <> 0:
        return res["hits"][0]["_source"]
    else:
        print "there is dsl problem"
        return res
        
def spammer_info2(spammer_id):
    dsl = {
        "query" : 
        {
            "match": {
                "_id": spammer_id
            }
        }
    }
    return es.search(index="amazon_reviews", doc_type="spammers",
                         body= dsl)["hits"]
                     
def spammer_reviews(spammer_id):
    dsl = {
        "query" : 
        {
            "match": {
                "review/userId": spammer_id
            }
        }
    }
    seen = set()
    res = es.search(index="amazon_reviews", doc_type="reviews", size = 1000,
                     body= dsl)
    review_list = [review["_source"] for review in res["hits"]["hits"]  \
        if review["_source"]["product/productId"] not in seen \
        and not seen.add(review["_source"]["product/productId"])]
    return review_list
