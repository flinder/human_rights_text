# Extract the wordcounts, years and coutnry information fomr mongo db into csv file

mongoexport --db hr_text --collection reports --csv --fieldFile fields.txt --out ../../data/analyses_plos/all_reports.csv
