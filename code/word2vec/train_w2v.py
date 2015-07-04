from pymongo import MongoClient
from gensim.models import Word2Vec
from gensim.models import Doc2Vec

#connection = pm.Connection("52.26.27.169", 8892)
# In order to connect to the DB on the server a ssh tunnel has to be set up
# run on your local machine:
#  ssh -N -f -L localhost:[port to tunnel to (here 7002)]:localhost:27017 ec2

client = MongoClient('mongodb://localhost:7002/')

db = client['human_rights_text']
reports = db['reports']

point = reports.find({'year.0': {'$gt': 1979, '$lt': 1990},
                      'organization': 'State Department'})

print '%d documents found in database' %point.count()
# Make a class with an iterator so the model can be trained sequentially and
# not all data has to be loaded to memory

class Sentences(object):

    def __init__(self, pointer):
        self.pointer = pointer

    def __iter__(self):
        """
        Iterates over sentences in documents
        """
        for document in self.pointer:
            print 'Processed %s' %document['file_name']
            sentences = document['preprocessed_text']
            for sentence in sentences:
                yield sentence


sentences = Sentences(point)
model = Word2Vec(sentences)
model.save('models/w2v_test')
print model.most_similar(positive = ['tortur'])
