# Goes through the reports database and updates it with:
# - document length

from pymongo import MongoClient
import pandas as pd
import sys
import re
from datetime import datetime
from countrycode import countrycode
from pprint import pprint
import time
import numpy as np

# Establish database connection
#client = MongoClient('52.25.102.188', 27017)
client = MongoClient()
db = client['hr']
reports = db['reports']

# Function to monitor loop progress
def track_process(idx, stepsize, tasksize, timing = True):
    global last_call
    global times

    iter_time = time.time() - last_call
    last_call = time.time()
    times.append(iter_time)
    
    if idx % stepsize == 0 and iter_time is not None:
        print "Finished %d of %d items. Average time per item: %fs" %(idx, tasksize, np.mean(times))
        times = []


def recursive_na_delete(doc):
    for key in doc.keys():
        if isinstance(doc[key], float):
            if np.isnan(doc[key]):
                del doc[key]
                
        elif isinstance(doc[key], dict):
            recursive_na_delete(doc[key])

        else:
            continue

    return doc


# Read metadata file
df = pd.read_csv('../../data/coding_files/hr_codings.csv')

last_call = time.time()
times = []
n_iter = df.shape[0]

for idx, row in df.iterrows():

    year = row['Year']
    code = row['country_iso3c']
    country = row['country_name']
    
    # Find matching document in database
    point = reports.find({'country_iso3c': code,
                          'year.0': year
                          })
    if point.count() == 0:
        error = 'No match for %s %s' %(year, country)
        print error
        with open('log.txt', 'a') as logfile:
            message = '[%s]: %s \n' %(str(datetime.now()), error)
            logfile.write(message)
        continue
    
    for doc in point:
        
        doc['country_cow_code'] = row['country_cow']
        doc['CIRI_codings'] = {'physical_integrity': {'killing': row['KILL'],
                                                      'dissapearance': row['DISAP'],
                                                      'imprisonment': row['POLPRIS'],
                                                      'torture': row['TORT']
                                                      },
                                'empowerment': {'assembly': row['ASSN'],
                                                'domestic_movement': row['DOMMOV'],
                                                'foreign_movement': row['FORMOV'],
                                                'speech': row['SPEECH'],
                                                'worker_rights': row['WORKER'],
                                                'electoral_rights': row['ELECSD'],
                                                'religious_rights': row['NEW_RELFRE']
                                                }                            
                               }
        doc['political_terror_scale'] = None
        doc['hathaway'] = row['hathaway']
        doc['state'] = row['State']
        doc['genocide'] = row['genocide']
        doc['rummel'] = row['rummel']
        doc['massive_repression'] = row['massive_repression']
        doc['amnesty'] = row['Amnesty']
        doc['fariss'] = {'mean': row['latentmean'],
                         'std_deviation': row['latentsd']
                         }


        doc = recursive_na_delete(doc)

        # Insert word count
        count = 0
        for el in doc['preprocessed_text']:
            count += len(el)
        
        doc['wordcount'] = count
        
        reports.update({'_id': doc['_id']}, doc)
        track_process(idx, 9000, n_iter, timing = True)
