from mrjob.job import MRJob
import re
import dev
from pymongo import MongoClient


WORD_RE = re.compile(r"[\w']+")

class MRWordFrequencyCount(MRJob):
    def mapper(self, _, line):
        for word in WORD_RE.findall(line):
            yield word, 1

    def reducer(self, key, values):
        result = dev.spammer_detect(key, 3, 3600*24*180)
        result["_id"] = key
        users.insert(result)
        yield key, result
        
if __name__ == '__main__':
    client = MongoClient()
    users = client.amazon_reviews.spammers
    MRWordFrequencyCount.run()
