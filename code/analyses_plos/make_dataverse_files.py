# Write raw text of all documents stored in db to files with clean filenames
# for sharing

from pymongo import MongoClient
import re
import os
import codecs

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONFIG
DB = "hr"
COLL = "reports"
OUTPATH = "../../data/analyses_plos/dataverse/"
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 

connection = MongoClient()[DB][COLL]
cursor = connection.find()

for doc in cursor:
    organization = doc["organization"]
    year = doc["year"]
    country = doc["country_iso3c"]
    # Substitute the raw report name for the ones that did not get resolved
    if len(country) > 3:
        country = doc["report_name"]
    outfile_name = "{}_{}_{}.txt".format(organization, year, country)
    outfile_name = re.sub(" ", "_", outfile_name)
    outfile_name = os.path.join(OUTPATH, outfile_name) 

    with codecs.open(outfile_name, "w+", "utf-8") as outfile:
        outfile.write(unicode(doc["raw_text"]))
