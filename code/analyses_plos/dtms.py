import numpy as np
import pandas as pd
import scipy.sparse as ssp
from pymongo import MongoClient
from gensim import corpora
from gensim import matutils
from pprint import pprint
import re


def load_sparse_csc(filename):
    loader = np.load(filename)
    return ssp.csc_matrix((loader['data'], loader['indices'], loader['indptr']), shape = loader['shape'])

def save_sparse_csc(filename, array):
    np.savez(filename, data = array.data, indices = array.indices, 
            indptr = array.indptr, shape = array.shape)

def make_corpus(database, collection, query = {}):

    # Query documents
    connection = MongoClient()[database][collection]
    cursor = connection.find(query)

    # Initialize empty dictionary and corpus
    dictionary = corpora.Dictionary()
    corpus = []
    hyap = re.compile(u"[-|']")

    i = 1
    for doc in cursor:
        text = [hyap.sub('', item) for sublist in doc['preprocessed_text'] for item in sublist]
        corpus.append(dictionary.doc2bow(text, allow_update = True))
        if i % 100 == 0:
            print i
        i += 1
    return dictionary, corpus

def store_matrix(vocabulary, sparse_matrix, filename):
    save_sparse_csc(filename, sparse_matrix)
    voc_file = filename + "_vocabulary.txt"
    with open(voc_file, "w+") as outfile:
        outfile.write("\n".join(vocabulary).encode("utf8"))

dictionary, corpus = make_corpus("hr", "reports")

wc_full = matutils.corpus2dense(corpus, num_terms = len(dictionary), dtype = int, num_docs = len(corpus))
sorted_dict = sorted(dictionary.items(), key=lambda tup: tup[0])
vocabulary_full = [el[1] for el in sorted_dict]

# Load the metadata file
metadata = pd.read_csv('../../data/analyses_plos/reports_metadata.csv')

# Calculate binary word occurence matrix
bin_full = wc_full.astype(bool).astype(int)


# Find the document frequency for each word
df = bin_full.sum(axis = 1)
bin_full = None

## Generate full output matrix
# remove words appearing in less than 2 docs 
drop = [i for i, x in enumerate(df) if x < 2]
print "Number of terms dropped with df <2: {}".format(len(drop))

# Delete rows to drop
full = np.delete(wc_full, drop, 0)
wc_full = None

vocab_out = [v for i, v in enumerate(vocabulary_full) if i not in drop]

# Save as sparse matrix
full_out = ssp.csc_matrix(full, dtype = int).transpose()
store_matrix(vocab_out, full_out, '../../data/analyses_plos/dtms/full_dtm')
print "done with full matrix"

## Generate reduced matrix
# Remove all words occuring in at least 95% of docs or in less than 5 docs

# Get doc frequencies and proportions again
bin_full = full.astype(bool).astype(int)
df = bin_full.sum(axis = 1)
prop = [(float(el) / float(bin_full.shape[1])) for el in df]
bin_full = None
drop = [index for index, (p, x) in enumerate(zip(prop, df)) if p > 0.95 or x < 5]
reduced = np.delete(full, drop, 0)
full = None
vocab_red = [v for i, v in enumerate(vocab_out) if i not in drop]

# Save the reduced one
red_out = ssp.csc_matrix(reduced, dtype = int).transpose()
store_matrix(vocab_red, red_out, '../../data/analyses_plos/dtms/red_dtm')

## Generate the small matrix
# Only the 1000 most frequent terms from the reduced matrix

# Calculate term frequency in reduced matrix
tf = reduced.sum(axis = 1)
keep = tf.argsort()[-100:]
drop = [i for i in range(len(tf)) if i not in keep]
small = np.delete(reduced, drop, 0)
vocab_small = [v for i, v in enumerate(vocab_red) if i not in drop] 

# save the small matrix to csv
small_out = pd.DataFrame(small, index = vocab_small, columns =
        metadata['new_filename'])
small_out = small_out.transpose()
small_out.to_csv('../../data/analyses_plos/dtms/small_dtm.csv')
