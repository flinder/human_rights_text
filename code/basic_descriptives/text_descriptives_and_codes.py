# Goes through the reports database and updates it with:
# - document length

from pymongo import MongoClient
import pandas as pd
import sys
import re
from datetime import datetime

# ssh -N -f -L localhost:7003:localhost:27017 ec2

# Establish database connection
client = MongoClient('mongodb://localhost:7003/')
db = client['human_rights_text']
reports = db['reports']

# Read metadata file
df = pd.read_csv('../../data/report_info.csv')

for idx, row in df.iterrows():

    organization = row['Organization']
    year = row['Year']

    try:
        country = row['Country'].lower()
        country = re.sub(' ', '_', country)
    except Exception as e:
        with open('log.txt', 'a') as logfile:
            message = 'Error in to lower for %s' %row['filename']
            logfile.write(message)

    # Find matching document in databasen
    point = reports.find({'organization': organization,
                          'year': year,
                          'country': country})
    if point.count() == 0:
        error = 'No match for %s %s %s' %(organization, year, country)
        with open('log.txt', 'a') as logfile:
            message = '[%s]: %s \n' %(str(datetime.now()), error)
            logfile.write(message)
        continue

    elif point.count() > 1:
        error = 'multiple matches for %s %s %s' %(organization, year, country)
        raise ValueError(error)


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
    doc['fariss'] = {'mean': row['latentmean'],
                     'std_deviation': row['latentsd']
                     }
    doc['n_characters'] = len(doc['raw_text'])
    reports.update({'_id': doc['_id']}, doc)

    print idx
