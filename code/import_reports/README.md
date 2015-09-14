# Import Reports

This script imports the raw human rights reports from text files into the mongodb. It extracts meta data from the filenames and stores it along with the raw text and the stemmed and cleaned text. It also augments the reports in the database with annotations from common human rights coding schemes (`merge_coding_files.R` generates the master file containing the codes)

In order for the country resolution to work properly, install the `countrycode` package from binstar `conda install --channel https://conda.anaconda.org/travis countrycode`. I added (fake) iso3 codes for German Democratic Republic (GDR), Kosovo (KOS) and Yugoslavia (YUG) in `~/anaconda/lib/python2.7/site-packages/countrycode/data/countrycode_data.csv`.
