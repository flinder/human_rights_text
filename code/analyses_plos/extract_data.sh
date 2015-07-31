# Extract the wordcounts, years and coutnry information fomr mongo db into csv file

mongoexport --host 52.25.102.188 --port 27017 --db hr_text --collection reports --type=csv --fieldFile fields.txt --out ../../data/analyses_plos/all_reports.csv
