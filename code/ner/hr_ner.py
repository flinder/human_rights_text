import os
import nltk
from pymongo import MongoClient
from pprint import pprint
import sys
from stanford_corenlp_pywrapper import CoreNLP
#import nltk.data

# Named entity recognition on human rights reports

proc = CoreNLP("ner", corenlp_jars = ["/home/ubuntu/corenlp/stanford-corenlp-full-2015-04-20/*"])
# proc = CoreNLP("ner", corenlp_jars = ["/home/flinder/corenlp/stanford-corenlp-full-2015-04-20/*"])

## Connect to database

# When not working from the server:
#client = MongoClient('52.25.102.188', 27017)

client = MongoClient()
db = client['hr_text']
reports = db['reports']

cursor = reports.find({'raw_text': {'$exists': True}, 'year.0': 1979}).limit(10)

for document in cursor:

    print document['file_name']

    # Parse the raw text
    text = document['raw_text']
    parsed_text = proc.parse_doc(text)

    # Count named entity types
    ner_count = {}
    for sentence in parsed_text['sentences']:
        ner = sentence['ner']
        for entity in ner:
            try:
                ner_count[entity] += 1
            except KeyError:
                ner_count[entity] = 1

    pprint(ner_count)


# for document in cursor:

#     text = document['raw_text']

#     count_ne(text)

#     break
