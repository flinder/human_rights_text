mkdir dtms
cd dtms/
wget https://dataverse.harvard.edu/api/access/datafile/2711137?gbrecs=true
mv 2711137\?gbrecs\=true full_dtm.npz
wget https://dataverse.harvard.edu/api/access/datafile/2711136?gbrecs=true
mv 2711136\?gbrecs\=true red_dtm.npz
wget https://dataverse.harvard.edu/api/access/datafile/2711140?gbrecs=true
mv 2711140\?gbrecs\=true full_dtm_vocabulary.txt
wget https://dataverse.harvard.edu/api/access/datafile/2711138?gbrecs=true
mv 2711138\?gbrecs\=true red_dtm_vocabulary.txt
wget https://dataverse.harvard.edu/api/access/datafile/2709416?gbrecs=true
mv 2709416\?gbrecs\=true reports_metadata.csv
mkdir aggregated/
cd ..
python aggregate_dtms.py
Rscript fighting_words.R
