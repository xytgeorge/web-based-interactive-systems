from elasticsearch import Elasticsearch
es = Elasticsearch()

# duplication detection, return the number of duplicated items
def dup(min_score, review_text):
    dsl = {
        "min_score": min_score,
        "query" : {
            "match" : {
                "review/text" : review_text,
            }
        } 
    }
    return es.search(index="amazon_reviews", doc_type="reviews",
                body= dsl)["hits"]["total"]
