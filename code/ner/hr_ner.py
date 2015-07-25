import os
import nltk
from pymongo import MongoClient
from pprint import pprint
import sys
from stanford_corenlp_pywrapper import CoreNLP
#import nltk.data

# Named entity recognition on human rights reports

proc = CoreNLP("ner", corenlp_jars = ["/home/flinder/corenlp/stanford-corenlp-full-2015-04-20/*"])

# Connect to database
client = MongoClient('52.25.102.188', 27017)
db = client['hr_text']
reports = db['reports']


cursor = reports.find({'raw_text': {'$exists': True}, 'year.0': 1979}).limit(20)


for document in cursor:
    print document['file_name']
    text = document['raw_text']
    proc.parse_doc(text)

# for document in cursor:

#     text = document['raw_text']

#     count_ne(text)

#     break
