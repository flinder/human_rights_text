## Takes original human rights documents and transforms them into json docs

import re
import ntpath
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer
import sys
import os
import json
import pandas as pd
from datetime import datetime
sys.path.insert(1, '~/pycountrycode')
from countrycode import countrycode
from pymongo import MongoClient
from nltk.metrics import *
import codecs
import time
import numpy as np
from pprint import pprint

class Document(object):

    def __init__(self, path, typos):
        self.path = path
        self.fname = ntpath.basename(path)
        self.organization = self.get_organization()
        with open(path) as infile:
            self.raw_text = unicode(infile.read(), encoding = 'utf-8', errors = 'ignore')
        self.typos = typos
        
    def get_organization(self):
        if re.search('AI_', self.fname):
            return 'Amnesty International'
        elif re.search('Critique_', self.fname):
            return 'Lawyers Committee'
        elif re.search('hwr[0-9]{4}', self.fname):
            return 'Human Rights Watch'
        elif re.search('State_', self.fname):
            return 'State Department'
        else:
            error = 'Could not recognize organization. Unexpected filename: %s' %fname
            raise ValueError(error)

    def get_year(self):
        """
        Extracts the year from the document name.
        """
        
        year = re.findall('[0-9]{4}', self.fname)
        if len(year) < 1:
            error = 'Unexpected number of dates in filename: %s' %self.fname
            raise ValueError(error)
        return [int(year[0])]
    
    def get_country(self, regex):
        """
        Extract the country or special issue name from file name
        regex: A string containing a regular expression for everything that is
               not the country name (and to be excluded) but not the file extension
        """
        # Output doc
        out = {}

        fname_wo_extension = self.fname[:-4]
        country = re.sub(regex, '', fname_wo_extension)
        country = re.sub('( |-)', '_', country)
        country = country.lower()
	# Store raw report_name
	out['report_name'] = country
        country = re.sub('_', ' ', country)
       
	# Resolve country names and store iso3 codes 
        try:
            raw_name = countrycode(codes = country, origin='country_name',
                                   target='country_name')
            code = countrycode(codes = country, origin='country_name',
                               target='iso3c')

            # If no name match look in the typo file
            if code == raw_name:
                try:
                    raw_name = countrycode(codes = [self.typos[country]],
                                               origin='country_name',
                                               target='country_name')
                    code = countrycode(codes = [self.typos[country]],
                        	          origin= 'country_name',
                                          target= 'iso3c')
                    out['country_name'] = raw_name
                    out['country_code'] = code

                except KeyError:
                    print "Could not resolve country name for %s" %raw_name
                    out['country_name'] = "Not resolved"
                    out['country_code'] = "Not resolved"

            else:
                out['country_name'] = raw_name
                out['country_code'] = code
        except UnicodeEncodeError:
            print "Could not resolve country name for %s" %raw_name
            out['country_name'] = "Not resolved"
            out['country_code'] = "Not resolved"
        
	# Somehow countrycode returns list in some cases. Check and make string
	if isinstance(out['country_name'], list):
		out['country_name'] = out['country_name'][0]
	if isinstance(out['country_code'], list):
		out['country_code'] = out['country_code'][0]
	return out

    def extract_clean_sentences(self):
        """
        Extracts sentences from plain text. Also applies the following cleaning
        operations:
        - Exclude all characters not recognized by 'utf-8' encoding
        - Exclude all characters not contained in [a-zA-Z0-9 '-]
        - Exclude common stopwords
        """

        text = self.raw_text
        
        exclude = re.compile('[^a-zA-Z0-9 \'-]')
        linebreaks = re.compile('\s')
        excess_space = re.compile('\s+')
        stemmer = PorterStemmer()

        sentences = sent_tokenize(text)
        out = []
        for sentence in sentences:
            sentence = linebreaks.sub(' ', sentence)
            sentence = exclude.sub(' ', sentence)
            sentence = excess_space.sub(' ', sentence)
            tokens = word_tokenize(sentence)
            tokens = [stemmer.stem(t.lower()) for t in tokens]
            out.append(tokens)

        return out

    def export_dict(self):
        """
        Return the file content and metadata as a dictonary/json object
        """
        doc = {}
        doc['file_name'] = self.fname
        doc['organization'] = self.organization
        doc['country_name'] = self.country_name
        doc['country_iso3c'] = self.country_iso3c
	doc['report_name'] = self.report_name
        doc['year'] = self.year
        doc['preprocessed_text'] = self.sentences
        doc['raw_text'] = self.raw_text
        return doc
    
class AI_doc(Document):

    def __init__(self, path, typos):
        Document.__init__(self, path, typos)
        self.year = self.get_year()
        cntry = self.get_country('AI_Report_[0-9]{4}((-|_)[0-9]{2})?_')
        self.country_name = cntry['country_name']
        self.country_iso3c = cntry['country_code']
	self.report_name = cntry['report_name']
        self.sentences = self.extract_clean_sentences()

    def get_year(self):
        """
        Extracts the year from the AI document name. AI reports until 1981
        are from summer to summer, therefore covering two half calendar years
        After 1981 they aligned theur coverage year with the calendar year. This
        function accounts for this fact and assigns both calendar years for reports
        prior to 1982
        """
        year = int(re.findall('[0-9]{4}', self.fname)[0])
        if year < 1976:
            return [year, (year + 1)]
        elif year > 1975 and year < 1982:
            return [(year - 1), year]
        else:
            return [(year - 1)]


class SD_doc(Document):
    
    def __init__(self, path, typos):
        Document.__init__(self, path, typos)
        self.year = self.get_year()
        cntry = self.get_country('State_Report_[0-9]{4}_')
        self.country_name = cntry['country_name']
        self.country_iso3c = cntry['country_code']
        self.sentences = self.extract_clean_sentences()
	self.report_name = cntry['report_name']

class CR_doc(Document):

    def __init__(self, path, typos):
        Document.__init__(self, path, typos)
        self.year = self.get_year()
        cntry = self.get_country('Critique_Review_[0-9]{4}_')
        self.country_name = cntry['country_name']
        self.country_iso3c = cntry['country_code']
        self.sentences = self.extract_clean_sentences()
	self.report_name = cntry['report_name']


class HRW_doc(Document):

    def __init__(self, path, typos):
        Document.__init__(self, path, typos)
        self.year = self.get_year()
        cntry = self.get_country('hwr[0-9]{4}_')
        self.country_name = cntry['country_name']
        self.country_iso3c = cntry['country_code']
        self.sentences = self.extract_clean_sentences()
	self.report_name = cntry['report_name']



# ==============================================================================


if __name__ == "__main__":

    def get_doctype(path):
        fname = ntpath.basename(path)
        if re.search('AI_', fname):
            return AI_doc(path, typos)
        elif re.search('Critique_', fname):
            return CR_doc(path, typos)
        elif re.search('hwr[0-9]{4}', fname):
            return HRW_doc(path, typos)
        elif re.search('State_', fname):
            return SD_doc(path, typos)
        else:
            error = 'Unexpected filename: %s' %fname
            raise ValueError(error)


    def track_process(idx, stepsize, tasksize, timing = True):
        global last_call
        global times

        iter_time = time.time() - last_call
        last_call = time.time()
        times.append(iter_time)

        if idx % stepsize == 0 and iter_time is not None:
            mean = np.mean(times)
            estimated = mean * (tasksize - idx) / 3600
            print "Finished %d of %d items. Estimated time remaining: %f h (%f pi)" %(idx, tasksize, estimated, mean)

    def wordcount(sentences):
	count = 0
        for el in sentences:
   	    count += len(el)
	return count


    def recursive_na_delete(doc):
        for key in doc.keys():
       	    if isinstance(doc[key], float):
	        if np.isnan(doc[key]):
		    del doc[key]
	    elif isinstance(doc[key], dict):
	        recursive_na_delete(doc[key])
	    else:
	        continue
	return doc

    file_dir = sys.argv[1]
    log_fname = sys.argv[2]
    database = sys.argv[3]
    collection = sys.argv[4]

    # Load typo file
    typos = {}
    with codecs.open('../../data/coding_files/countryname_typos.csv', encoding = 'utf-8') as infile:
        for line in infile:
            line = re.sub("\", \"", "\"|\"", line)
            line = re.sub("\"", "", line)
            line = re.sub("\n", "", line)
            line = line.lower()
            splits = line.split("|")
            typos[splits[0]] = splits[1]

    # Load meta data file
    metadata = pd.read_csv('../../data/coding_files/hr_codings.csv')
    # Connect to mongo db
    connection = MongoClient()[database][collection]

    print file_dir
    i = 0
    last_call = time.time()
    times = []
    for root, dirs, files in os.walk(file_dir):

        for fname in files:
            if fname == ".DS_Store":
                continue
            path = os.path.join(root, fname)
            doc = get_doctype(path)
            out = doc.export_dict()

	    # Insert metadata
	    if len(out['country_iso3c']) > 3:
		# No country report or country could not be resolved. Just add the wordcounts
		pass
	    else:
		iso = out['country_iso3c']
	        orga = out['organization']
	        year = out['year'][0]
		# Find row in metadata file
	  	row = metadata[(metadata.Year == year) & (metadata.country_iso3c == iso)]
		if row.shape[0] == 1:
			
			out['country_cow_code'] = row.iloc[0]['country_cow']
			out['CIRI_codings'] = {'physical_integrity': {'killing': row.iloc[0]['KILL'],
								      'dissapearance': row.iloc[0]['DISAP'],
								      'imprisonment': row.iloc[0]['POLPRIS'],
								      'torture': row.iloc[0]['TORT']
								      },
						'empowerment': {'assembly': row.iloc[0]['ASSN'],
								'domestic_movement': row.iloc[0]['DOMMOV'],
								'foreign_movement': row.iloc[0]['FORMOV'],
								'speech': row.iloc[0]['SPEECH'],
								'worker_rights': row.iloc[0]['WORKER'],
								'electoral_rights': row.iloc[0]['ELECSD'],
								'religious_rights': row.iloc[0]['NEW_RELFRE']
								}
					       }
			out['hathaway'] = row.iloc[0]['hathaway']
			out['state'] = row.iloc[0]['State']
			out['genocide'] = row.iloc[0]['genocide']
			out['rummel'] = row.iloc[0]['rummel']
			out['massive_repression'] = row.iloc[0]['massive_repression']
			out['amnesty'] = row.iloc[0]['Amnesty']
			out['fariss'] = {'mean': row.iloc[0]['latentmean'],
					 'std_deviation': row.iloc[0]['latentsd']
					}
			out['word_count'] = wordcount(out['preprocessed_text'])
			out = recursive_na_delete(out)
		else:
			pass
	    
            out['word_count'] = wordcount(out['preprocessed_text'])
            
	    # Insert the new filename
            if len(out['country_iso3c']) == 3:
		x = "{}_{}_{}.txt".format(out['country_iso3c'], out['year'][0], out['organization'])
		x = re.sub(" ", "_", x)
		out['new_filename'] = x
	    else:
		x = "{}_{}_{}.txt".format(out['report_name'], out['year'][0], out['organization'])
		x = re.sub(" ", "_", x)
		out['new_filename'] = x
	    connection.update({'file_name': doc.fname}, out, upsert = True)

            i += 1
            track_process(i, 100, 15000, timing = True)
    

