from pymongo import MongoClient
import re
import os
import codecs

DB = "hr"
COLL = "reports"
OUTPATH = "../../data/analyses_plos/dataverse/"

connection = MongoClient()[DB][COLL]

cursor = connection.find()

for doc in cursor:
    outfile_name = "{}_{}_{}.txt".format(doc["organization"],
                                         doc["country_iso3c"],
					 doc["year"][0])
    outfile_name = re.sub(" ", "_", outfile_name)
    outfile_name = os.path.join(OUTPATH, outfile_name) 

    with codecs.open(outfile_name, "w+", "utf-8") as outfile:
        outfile.write(unicode(doc["raw_text"]))
