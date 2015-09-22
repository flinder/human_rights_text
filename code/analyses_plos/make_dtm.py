# Generate document term matrices from mongo db

from pymongo import MongoClient
from gensim import corpora
from gensim import matutils
from pprint import pprint

import numpy as np


def save_sparse_csc(filename,array):
        np.savez(filename,data = array.data ,indices=array.indices,
                             indptr =array.indptr, shape=array.shape )

def make_corpus(database, collection, query = {}):

    # Query documents
    connection = MongoClient()[database][collection]
    cursor = connection.find(query)

    # Initialize empty dictionary and corpus
    dictionary = corpora.Dictionary()
    corpus = []

    i = 1
    for doc in cursor:
        text = [item for sublist in doc['preprocessed_text'] for item in sublist]
        corpus.append(dictionary.doc2bow(text, allow_update = True))
        if i % 100 == 0:
            print i
        i += 1
    return dictionary, corpus


def store_matrix(dictionary, corpus, filename):
    sparse_matrix = matutils.corpus2csc(corpus)
    save_sparse_csc(filename, sparse_matrix)
    voc_file = filename + "_vocabulary.txt"
    with open(voc_file, "w+") as outfile:
        outfile.write("\n".join(dictionary.values()).encode("utf8"))

if __name__ == "__main__":
    dictionary, corpus = make_corpus("hr", "reports")
    store_matrix(dictionary, corpus, "../../data/analyses_plos/dtms/full_corpus")
