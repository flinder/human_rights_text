# coding: utf-8
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.ensemble import RandomForestClassifier as rf
import os
import numpy as np
import scipy.sparse as ssp
from itertools import repeat
import math

def load_sparse_csr(filename):
    loader = np.load(filename)
    return ssp.csr_matrix((loader['data'], loader['indices'], loader['indptr']),
                       shape = loader['shape'])


# Load the full matix
wc_full = load_sparse_csr('../../data/analyses_plos/dtms/full_dtm.npz')

# Load the vocabulary
with open('../../data/analyses_plos/dtms/full_dtm_vocabulary.txt') as vocfile:
    voc_full = [x.strip('\n') for x in vocfile.readlines()]
    
# Load the reduced matix
wc_red = load_sparse_csr('../../data/analyses_plos/dtms/red_dtm.npz')

# Load the vocabulary
with open('../../data/analyses_plos/dtms/red_dtm_vocabulary.txt') as vocfile:
    voc_red = [x.strip('\n') for x in vocfile.readlines()]

# # ==============================================================================
# # Aggregate dt-matrix by human rights codings
# # ==============================================================================

# Function to make matrix for matrix multiply to aggregate
# documents in sparse dtm according to codings
# codefile contains one row for each document, with the colums for different
# coding schemes
# if org is set to one or more organizations in the codefile, reports by other
# organizations are excluded
def sum_mat(codefile, codename, remove_NA = True, org = None):
    D = codefile.shape[0]
    p = sorted(codefile[codename].unique())
    if org is not None:
        orgs = codefile['organization'].unique()
        excl = [x for x in orgs if x not in org]
        if len(excl) == 4:
            raise ValueError('All organizations excluded. Check spelling')
    col, lens = [], []
    for i in p:
        if remove_NA and i != i: # Exclude docs that are not coded
            continue
        idx = codefile[codefile[codename] == i].index.tolist()
        if org is not None:
            idx_not = codefile[codefile.organization.isin(excl)].index.tolist()
            idx = [x for x in idx if x not in idx_not]
        col.extend(idx)
        lens.append(len(idx))
    row = []
    for i in range(len(lens)):
        row.extend([i] * lens[i])
    dat = [1] * len(row)
    isd = [1 if x == x else 0 for x in p]
    out = ssp.csr_matrix((dat, (row, col)), shape = (sum(isd), D))
    return out

## =============================================================================
## Save matrices aggregated according to the schemes to disk (as .csv)
## For full and reduced dtm
## =============================================================================

## Get most important words with a random forest classifier
codings = pd.read_csv("../../data/analyses_plos/reports_metadata.csv")
codings.columns
## State
dtm_state = sum_mat(codings, 'state', org = 'State Department')  * wc_full
df_state = pd.DataFrame(dtm_state.toarray(), index = ['1', '2', '3', '4', '5'])
df_state.columns = voc_full
df_state.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_full_state.csv', encoding = 'utf-8',
                index_label = False, index = False)

dtm_state_red = sum_mat(codings, 'state', org = 'State Department')  * wc_red
df_state_red = pd.DataFrame(dtm_state_red.toarray(), index = ['1', '2', '3', '4', '5'])
df_state_red.columns = voc_red
df_state_red.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_red_state.csv', encoding = 'utf-8',
                index_label = False, index = False)

## Amnesty
dtm_amnesty = sum_mat(codings, 'amnesty', org = 'Amnesty International')  * wc_full
df_amnesty = pd.DataFrame(dtm_amnesty.toarray(), index = ['1', '2', '3', '4', '5'])
df_amnesty.columns = voc_full
df_amnesty.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_full_amnesty.csv', encoding = 'utf-8',
                index_label = False, index = False)

dtm_amnesty_red = sum_mat(codings, 'amnesty', org = 'Amnesty International')  * wc_red
df_amnesty_red = pd.DataFrame(dtm_amnesty_red.toarray(), index = ['1', '2', '3', '4', '5'])
df_amnesty_red.columns = voc_red
df_amnesty_red.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_red_amnesty.csv', encoding = 'utf-8',
                index_label = False, index = False)

## hathaway
dtm_hathaway = sum_mat(codings, 'hathaway', org = 'State Department')  * wc_full
df_hathaway = pd.DataFrame(dtm_hathaway.toarray(), index = ['1', '2', '3', '4', '5'])
df_hathaway.columns = voc_full
df_hathaway.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_full_hathaway.csv', encoding = 'utf-8',
                index_label = False, index = False)

dtm_hathaway_red = sum_mat(codings, 'hathaway', org = 'State Department')  * wc_red
df_hathaway_red = pd.DataFrame(dtm_hathaway_red.toarray(), index = ['1', '2', '3', '4', '5'])
df_hathaway_red.columns = voc_red
df_hathaway_red.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_red_hathaway.csv', encoding = 'utf-8',
                index_label = False, index = False)

## CIRI disap
dtm_disap = sum_mat(codings, 'CIRI_codings.physical_integrity.dissapearance', org = ['State Department', 'Amnesty International'])  * wc_full
df_disap = pd.DataFrame(dtm_disap.toarray(), index = ['0', '1', '2'])
df_disap.columns = voc_full
df_disap.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_full_disap.csv', encoding = 'utf-8',
                index_label = False, index = False)

dtm_disap_red = sum_mat(codings, 'CIRI_codings.physical_integrity.dissapearance', org = ['State Department', 'Amnesty International'])  * wc_red
df_disap_red = pd.DataFrame(dtm_disap_red.toarray(), index = ['0', '1', '2'])
df_disap_red.columns = voc_red
df_disap_red.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_red_disap.csv', encoding = 'utf-8',
                index_label = False, index = False)

## CIRI kill
dtm_kill = sum_mat(codings, 'CIRI_codings.physical_integrity.killing', org = ['State Department', 'Amnesty International'])  * wc_full
df_kill = pd.DataFrame(dtm_kill.toarray(), index = ['0', '1', '2'])
df_kill.columns = voc_full
df_kill.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_full_kill.csv', encoding = 'utf-8',
                index_label = False, index = False)

dtm_kill_red = sum_mat(codings, 'CIRI_codings.physical_integrity.killing', org = ['State Department', 'Amnesty International'])  * wc_red
df_kill_red = pd.DataFrame(dtm_kill_red.toarray(), index = ['0', '1', '2'])
df_kill_red.columns = voc_red
df_kill_red.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_red_kill.csv', encoding = 'utf-8',
                index_label = False, index = False)

## CIRI polpris
dtm_polpris = sum_mat(codings, 'CIRI_codings.physical_integrity.imprisonment', org = ['State Department', 'Amnesty International'])  * wc_full
df_polpris = pd.DataFrame(dtm_polpris.toarray(), index = ['0', '1', '2'])
df_polpris.columns = voc_full
df_polpris.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_full_polpris.csv', encoding = 'utf-8',
                index_label = False, index = False)

dtm_polpris_red = sum_mat(codings, 'CIRI_codings.physical_integrity.imprisonment', org = ['State Department', 'Amnesty International'])  * wc_red
df_polpris_red = pd.DataFrame(dtm_polpris_red.toarray(), index = ['0', '1', '2'])
df_polpris_red.columns = voc_red
df_polpris_red.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_red_polpris.csv', encoding = 'utf-8',
                index_label = False, index = False)

## CIRI tort
dtm_tort = sum_mat(codings, 'CIRI_codings.physical_integrity.torture', org = ['State Department', 'Amnesty International'])  * wc_full
df_tort = pd.DataFrame(dtm_tort.toarray(), index = ['0', '1', '2'])
df_tort.columns = voc_full
df_tort.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_full_tort.csv', encoding = 'utf-8',
                index_label = False, index = False)

dtm_tort_red = sum_mat(codings, 'CIRI_codings.physical_integrity.torture', org = ['State Department', 'Amnesty International'])  * wc_red
df_tort_red = pd.DataFrame(dtm_tort_red.toarray(), index = ['0', '1', '2'])
df_tort_red.columns = voc_red
df_tort_red.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_red_tort.csv', encoding = 'utf-8',
                index_label = False, index = False)

## CIRI assn
dtm_assn = sum_mat(codings, 'CIRI_codings.empowerment.assembly', org = ['State Department', 'Amnesty International'])  * wc_full
df_assn = pd.DataFrame(dtm_assn.toarray(), index = ['0', '1', '2'])
df_assn.columns = voc_full
df_assn.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_full_assn.csv', encoding = 'utf-8',
                index_label = False, index = False)

dtm_assn_red = sum_mat(codings, 'CIRI_codings.empowerment.assembly', org = ['State Department', 'Amnesty International'])  * wc_red
df_assn_red = pd.DataFrame(dtm_assn_red.toarray(), index = ['0', '1', '2'])
df_assn_red.columns = voc_red
df_assn_red.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_red_assn.csv', encoding = 'utf-8',
                index_label = False, index = False)

## CIRI FORMOV
dtm_formov = sum_mat(codings, 'CIRI_codings.empowerment.foreign_movement', org = ['State Department', 'Amnesty International'])  * wc_full
df_formov = pd.DataFrame(dtm_formov.toarray(), index = ['0', '1', '2'])
df_formov.columns = voc_full
df_formov.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_full_formov.csv', encoding = 'utf-8',
                index_label = False, index = False)

dtm_formov_red = sum_mat(codings, 'CIRI_codings.empowerment.foreign_movement', org = ['State Department', 'Amnesty International'])  * wc_red
df_formov_red = pd.DataFrame(dtm_formov_red.toarray(), index = ['0', '1', '2'])
df_formov_red.columns = voc_red
df_formov_red.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_red_formov.csv', encoding = 'utf-8',
                index_label = False, index = False)


## CIRI dommov
dtm_dommov = sum_mat(codings, 'CIRI_codings.empowerment.domestic_movement', org = ['State Department', 'Amnesty International'])  * wc_full
df_dommov = pd.DataFrame(dtm_dommov.toarray(), index = ['0', '1', '2'])
df_dommov.columns = voc_full
df_dommov.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_full_dommov.csv', encoding = 'utf-8',
                index_label = False, index = False)

dtm_dommov_red = sum_mat(codings, 'CIRI_codings.empowerment.domestic_movement', org = ['State Department', 'Amnesty International'])  * wc_red
df_dommov_red = pd.DataFrame(dtm_dommov_red.toarray(), index = ['0', '1', '2'])
df_dommov_red.columns = voc_red
df_dommov_red.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_red_dommov.csv', encoding = 'utf-8',
                index_label = False, index = False)

## CIRI speech
dtm_speech = sum_mat(codings, 'CIRI_codings.empowerment.speech', org = ['State Department', 'Amnesty International'])  * wc_full
df_speech = pd.DataFrame(dtm_speech.toarray(), index = ['0', '1', '2'])
df_speech.columns = voc_full
df_speech.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_full_speech.csv', encoding = 'utf-8',
                index_label = False, index = False)

dtm_speech_red = sum_mat(codings, 'CIRI_codings.empowerment.speech', org = ['State Department', 'Amnesty International'])  * wc_red
df_speech_red = pd.DataFrame(dtm_speech_red.toarray(), index = ['0', '1', '2'])
df_speech_red.columns = voc_red
df_speech_red.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_red_speech.csv', encoding = 'utf-8',
                index_label = False, index = False)

## CIRI elecsd
dtm_elecsd = sum_mat(codings, 'CIRI_codings.empowerment.electoral_rights', org = ['State Department', 'Amnesty International'])  * wc_full
df_elecsd = pd.DataFrame(dtm_elecsd.toarray(), index = ['0', '1', '2'])
df_elecsd.columns = voc_full
df_elecsd.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_full_elecsd.csv', encoding = 'utf-8',
                index_label = False, index = False)

dtm_elecsd_red = sum_mat(codings, 'CIRI_codings.empowerment.electoral_rights', org = ['State Department', 'Amnesty International'])  * wc_red
df_elecsd_red = pd.DataFrame(dtm_elecsd_red.toarray(), index = ['0', '1', '2'])
df_elecsd_red.columns = voc_red
df_elecsd_red.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_red_elecsd.csv', encoding = 'utf-8',
                index_label = False, index = False)

## CIRI new_relfre
dtm_new_relfre = sum_mat(codings, 'CIRI_codings.empowerment.religious_rights', org = ['State Department', 'Amnesty International'])  * wc_full
df_new_relfre = pd.DataFrame(dtm_new_relfre.toarray(), index = ['0', '1', '2'])
df_new_relfre.columns = voc_full
df_new_relfre.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_full_new_relfre.csv', encoding = 'utf-8',
                index_label = False, index = False)

dtm_new_relfre_red = sum_mat(codings, 'CIRI_codings.empowerment.religious_rights', org = ['State Department', 'Amnesty International'])  * wc_red
df_new_relfre_red = pd.DataFrame(dtm_new_relfre_red.toarray(), index = ['0', '1', '2'])
df_new_relfre_red.columns = voc_red
df_new_relfre_red.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_red_new_relfre.csv', encoding = 'utf-8',
                index_label = False, index = False)

## CIRI worker
dtm_worker = sum_mat(codings, 'CIRI_codings.empowerment.worker_rights', org = ['State Department', 'Amnesty International'])  * wc_full
df_worker = pd.DataFrame(dtm_worker.toarray(), index = ['0', '1', '2'])
df_worker.columns = voc_full
df_worker.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_full_worker.csv', encoding = 'utf-8',
                index_label = False, index = False)

dtm_worker_red = sum_mat(codings, 'CIRI_codings.empowerment.worker_rights', org = ['State Department', 'Amnesty International'])  * wc_red
df_worker_red = pd.DataFrame(dtm_worker_red.toarray(), index = ['0', '1', '2'])
df_worker_red.columns = voc_red
df_worker_red.to_csv(path_or_buf = '../../data/analyses_plos/dtms/aggregated/dtm_red_worker.csv', encoding = 'utf-8',
                index_label = False, index = False)
