from pymongo import MongoClient

DB = "hr"
COLL = "reports"

connection = MongoClient()[DB][COLL]

cursor = connection.find()

for doc in cursor:
	outfile_name = "{}_{}_{}.txt".format(doc["organization"], 
					     doc["country_iso3c"],
					     doc["year"][0])
