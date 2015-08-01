# Preprocess and import human rights reports into mongoDB

# Arguments (in order):
# filedir: Directory containing the original reports
# logfile
# database: name of database
# collection: name of collection
python import_reports.py ../../data/original_reports/ import_reports_log.txt hr_text reports
