import os
import nltk
from pymongo import MongoClient
from pprint import pprint
import sys
from stanford_corenlp_pywrapper import CoreNLP
import time
import numpy as np
#import nltk.data



def track_process(idx, stepsize, tasksize, timing = True):
    global last_call
    global times

    iter_time = time.time() - last_call
    last_call = time.time()
    times.append(iter_time)

    if idx % stepsize == 0 and iter_time is not None:
        print "Finished %d of %d items. Average time per item: %fs" %(idx, tasksize, np.mean(times))
        times = []



# Named entity recognition on human rights reports

proc = CoreNLP("ner", corenlp_jars = ["/home/flinder/corenlp/stanford-corenlp-full-2015-04-20/*"])

# Connect to database
client = MongoClient('52.25.102.188', 27017)
db = client['hr_text']
reports = db['reports']

cursor = reports.find({'raw_text': {'$exists': True}, 'ner_count': {'$exists': False}})
n_docs = cursor.count()
print "Found %d reports to process" %n_docs


last_call = time.time()
times = []

i = 0
for document in cursor:

    i += 1
    track_process(i, 100, n_docs)
    
    # Parse the raw text
    print document['file_name']
    text = document['raw_text']
    text = text.encode('utf-8').decode('utf-8','ignore').encode('utf-8')
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

    if not ner_count:
        document['ner_count'] = ''
    else:
        document['ner_count'] = ner_count
    reports.update({"_id": document["_id"]}, document)


# for document in cursor:

#     text = document['raw_text']

#     count_ne(text)

#     break
