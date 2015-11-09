# Human Rights Text Data Repository

## About

This repository contains the data described in 

Fariss CJ, Linder FJ, Jones ZM, Crabtree CD, Biek MA, Ross A-SM, et al. (2015) Human Rights Texts: Converting Human Rights Primary Source Documents into Data. PLoS ONE 10(9): e0138935. doi:10.1371/journal.pone.0138935

All code related to this paper can be found on [github](https://github.com/flinder/human_rights_text/releases). 

## Content

### `reports_metadata.csv`

Contains all metadata available for the reports. Refer to the new_filename
column to match to the report textfiles.

Description of the variables:
* `file_name`: File name of the original report
* `new_filename`: New file name, corresponding to the report files in `report_files.zip`
* `country_iso3c`: ISO code for country if exists. If the report does not correspond to a specific country this variable is coded as `Not resolved`)
* `country_name`: Full country name (if not a country `Not resolved`)
* `report_name`: Original title of the report as in `file_name`
* `year.0`: Coverage year of the report. For Amnesty International reports before 1982 this variable refers to the first year of coverage (see note in section `report_files.zip`)
* `organization`: Organization that released the report
* `word_count`: Number of words in the report after some basic cleaning
* `hathaway`: 5 category, ordered variable for torture from the Hathaway (2002) article
* `state`: Rating by Political Terror Scale project, based on State Department reports
* `fariss.mean`: Mean of the latent variable described in Fariss (2014)
* `farss.std_deviation`: Standard deviation of latent variable described in Fariss (2014)
* `country_cow_code`: Correlates of war country identifier
* `CIRI_codings.empowerment.electoral_rights`: 3 category, ordered variable for electoral rights from the CIRI dataset
* `CIRI_codings.empowerment.assembly`: 3 category, ordered variable for freedom of assembly from the CIRI dataset
* `CIRI_codings.empowerment.domestic_movement`: 3 category, ordered variable for freedom of domestic movement from the CIRI dataset
* `CIRI_codings.empowerment.religious_rights`:3 category, ordered variable for religious freedom from the CIRI dataset
* `CIRI_codings.empowerment.speech`: 3 category, ordered variable for freedom of speech from the CIRI dataset
* `CIRI_codings.empowerment.foreign_movement`: 3 category, ordered variable for freedom of foreign movement from the CIRI dataset
* `CIRI_codings.empowerment.worker_rights`: 3 category, ordered variable for workers rights from the CIRI dataset
* `CIRI_codings.physical_integrity.dissapearance`: 3 category, ordered variable for disappearances from the CIRI datast
* `CIRI_codings.physical_integrity.imprisonment`: 3 category, ordered variable for political imprisonment from the CIRI dataset
* `CIRI_codings.physical_integrity.torture`: 3 category, ordered variable for torture from the CIRI dataset
* `CIRI_codings.physical_integrity.killing`: 3 category, ordered variable from extra-judical killing the CIRI dataset
* `genocide`: A binary variable for genocide from Harff's 2003 APSR article
* `amnesty`: Rating by Political Terror Scale project, based on Amnesty International reports

### `report_files.zip`

Contains all full text reports. The filenames are in the format, `[counntry iso3 code]_[coverage year]_[Organization].txt`.

Note: Until (including) 1981 Amnesty International Reports had a coverage periods that did not align with the calendar year, therefore these reports have two coverage years. 
### `small_dtm.csv`

Small version of the document term matrix. See the paper for details.

### `full_dtm.npz`, `red_dtm.npz`, `full_dtm_vocabulary.txt`, `red_dtm_vocabulary.txt`

Full and reduced document term matrices. See the paper for details. Files with
`.npz` extension contain the document term matrices in [scipy
csr](http://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.sparse.csr_matrix.html)
format. Files with `.txt` extension contain the respective vocabularies (i.e.
column names of the matrices). The marices and vocabulary can be loaded with:

```python
import numpy as np
import scipy.sparse as ssp

def laod_sparse_csr(filename):
    loader = np.load(filename)
    return ssp.csr_matrix((loader['data'], loader['indices'], loader['indptr']),
                          shape = loader['shape'])

dtm = load_sparse_csr('/dtm_file.npz')
with open('vocabulary_file', 'r') as vocfile:
    vocabulary = [x.strip('\n') for x in vocfile.readlines()
```
