from elasticsearch import Elasticsearch
from datetime import datetime 
from collections import Counter
import dev,dup,splist
es = Elasticsearch()

def userquery(searchquery):
    dsl = {
    		"query" : {
      		  "multi_match": {
          		  "query":       searchquery,
           		  "type":        "most_fields",
          		  "operator":    "and", 
          		  "fields":      [ "review/userId", "review/profileName", "review/text", "product/productId", "product/title" ]
      		  	   }
  		}
	   }
    return dsl



def search(query):
    # get review text
    res = es.search(index = "amazon_reviews", doc_type = "reviews", size = 100, 
                    body = userquery(query))["hits"]
    
    try:
        for result in res["hits"]:
            result["_source"]["metric"] = 0 
            try: 
                print "start try", result["_source"]["review/userId"]
                spammer_info = splist.spammer_info2(result["_source"]["review/userId"])
                print spammer_info
                if spammer_info["total"] <> 0:
                    result["_source"]["metric"] = dev.metrics2(spammer_info["hits"][0]["_source"])
                    print result["_source"]["metric"]                
            except (RuntimeError, TypeError, NameError):
                print "there is a problem 2"
    except (RuntimeError, TypeError, NameError):
        print "there is a problem 1"
    #print res
    return res

