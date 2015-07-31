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
db = client['hr_text']
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


# Read metadata file
df = pd.read_csv('../../data/report_info.csv')

last_call = time.time()
times = []
n_iter = df.shape[0]

for idx, row in df.iterrows():


    organization = row['Organization']
    year = row['Year']

    # Resolve the country name in the info df
    if not isinstance(row['Country'], float):
        country = countrycode(codes = row['Country'], origin='country_name',
                              target='country_name')
        code = countrycode(codes = row['Country'], origin='country_name',
                           target='iso3c')
    else:
        with open('log.txt', 'a') as logfile:
            message = '[%s]: NA in country info for: %s \n' %(str(datetime.now()), row['filename'])
            logfile.write(message)

    if code is None:
        with open('log.txt', 'a') as logfile:
            message = '[%s]: Could not resolve country: %s \n' %(str(datetime.now()), row['filename'])
            logfile.write(message)
            
    # Find matching document in databasen
    point = reports.find({'country_iso3c': code,
                          'organization': organization,
                          'year.0': year
                          })
    if point.count() == 0:
        error = 'No match for %s %s %s' %(organization, year, country)
        print error
        with open('log.txt', 'a') as logfile:
            message = '[%s]: %s \n' %(str(datetime.now()), error)
            logfile.write(message)
        continue

    elif point.count() > 1:
        for subdoc in point:
            subdoc.pop('raw_text')
            subdoc.pop('preprocessed_text')
            pprint(subdoc)
    
        error = 'multiple matches for %s %s %s \n' %(organization, year, country)
        with open('log.txt', 'a') as logfile:
            logfile.write(error)

        continue
    doc = next(point)
    
    doc['wordcount'] = row['word_count']
    doc['country_cow_code'] = row['country_cow']
    doc['attention'] = row['Attention']
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
    reports.update({'_id': doc['_id']}, doc)
    track_process(idx, 100, n_iter, timing = True)
