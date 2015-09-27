# Import Reports

This script imports the raw human rights reports from text files into the mongodb. It extracts meta data from the filenames and stores it along with the raw text and the stemmed and cleaned text. It also augments the reports in the database with annotations from common human rights coding schemes (`merge_coding_files.R` generates the master file containing the codes)

Some countries don't have iso3 codes so I added the cow codes in the iso3 column in the data file of the countrycode package. Those are: German Democratic Republic (GDR), Kosovo (KOS) and Yugoslavia (YUG) in `~/anaconda/lib/python2.7/site-packages/countrycode/data/countrycode_data.csv`.
