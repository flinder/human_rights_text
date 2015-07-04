from gensim.models import Word2Vec
from scipy import spatial

model80 = Word2Vec.load('models/ai_raw_80s')
model90 = Word2Vec.load('models/ai_raw_90s')
model00 = Word2Vec.load('models/ai_raw_00s')

print '=' * 50

print len(model80.vocab)
print model80.most_similar('torture')

print "-" *20

print len(model90.vocab)
print model00.most_similar('torture')

print "Distance torture - torture:"
print spatial.distance.cosine(model80['torture'], model00['torture'])

print "Distance and - and:"
print spatial.distance.cosine(model80['and'], model00['and'])

print '=' * 50
