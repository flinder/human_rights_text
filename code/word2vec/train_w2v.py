from pymongo import MongoClient
from gensim.models import Word2Vec
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import os
from nltk.stem import PorterStemmer
import re
import sys

client = MongoClient()

db = client['hr']
reports = db['reports']

point = reports.find()

n_reports = point.count()

print '%d documents found in database' %n_reports

# Make a class with an iterator so the model can be trained sequentially and
# not all data has to be loaded to memory
class Sentences(object):

    def __init__(self, pointer):
        self.pointer = pointer
        self.n_doc = pointer.count()

    def __iter__(self):
        """
        Iterates over sentences in documents
        """
        i = 0
        for document in self.pointer:
            sentences = document['preprocessed_text']
            for sentence in sentences:
                yield sentence
            i += 1
            print 'Processed %d of %d documents' %(i, self.n_doc)


class Sentences_raw(object):
    
    def __init__(self, pointer):
        self.pointer = pointer
        self.n_doc = pointer.count()

    def __iter__(self):
        """
        Iterates over sentences in documents
        """
        
        exclude = re.compile('[^a-zA-Z0-9 ]')
        linebreaks = re.compile('\s')

        i = 0
        for document in self.pointer:
            text = document['raw_text'].lower()
            sentences_1 = sent_tokenize(text)
            for sentence in sentences_1:
                sentence = linebreaks.sub(' ', sentence)
                sentence = exclude.sub('', sentence)
                tokens = word_tokenize(sentence)
                yield tokens

            i += 1
            print 'Processed %d of %d documents' %(i, self.n_doc)
                        
sentences = Sentences_raw(point)
model = Word2Vec(sentences)
model.save('models/all_reports')


