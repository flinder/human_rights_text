## Takes original human rights documents and transforms them into json docs

import re
import ntpath
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer
import sys
import os
import json

class Document(object):

    def __init__(self, path):
        self.path = path
        self.fname = ntpath.basename(path)
        self.organization = self.get_organization()
        with open(path) as infile:
            self.raw_text = unicode(infile.read(), encoding = 'utf-8', errors = 'ignore')

    def get_organization(self):
        if re.search('AI_', self.fname):
            return 'Amnesty International'
        elif re.search('Critique_', self.fname):
            return 'Critique'
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
        
        fname_wo_extension = self.fname[:-4]
        country = re.sub(regex, '', fname_wo_extension)
        return country.lower()

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
        doc['country'] = self.country
        doc['year'] = self.year
        doc['preprocessed_text'] = self.sentences
        doc['raw_text'] = self.raw_text
        return doc


class AI_doc(Document):

    def __init__(self, path):
        Document.__init__(self, path)
        self.year = self.get_year()
        self.country = self.get_country('AI_Report_[0-9]{4}((-|_)[0-9]{2})?_')
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
    
    def __init__(self, path):
        Document.__init__(self, path)
        self.year = self.get_year()
        self.country = self.get_country('State_Report_[0-9]{4}_')
        self.sentences = self.extract_clean_sentences()


class CR_doc(Document):

    def __init__(self, path):
        Document.__init__(self, path)
        self.year = self.get_year()
        self.country = self.get_country('Critique_Review_[0-9]{4}_')
        self.sentences = self.extract_clean_sentences()

        
class HRW_doc(Document):

    def __init__(self, path):
        Document.__init__(self, path)
        self.year = self.get_year()
        self.country = self.get_country('hwr[0-9]{4}_')
        self.sentences = self.extract_clean_sentences()


# ==============================================================================


if __name__ == "__main__":

    def get_doctype(path):
        fname = ntpath.basename(path)
        if re.search('AI_', fname):
            return 'Amnesty International'
        elif re.search('Critique_', fname):
            return 'Critique'
        elif re.search('hwr[0-9]{4}', fname):
            return 'Human Rights Watch'
        elif re.search('State_', fname):
            return 'State Department'
        else:
            error = 'Unexpected filename: %s' %fname
            raise ValueError(error)
    
    file_dir = sys.argv[1]
    out_fname = sys.argv[2]

    i = 0
    with open(out_fname, 'w') as outfile:
        
        for root, dirs, files in os.walk(file_dir):
            
            for fname in files:
                
                path = os.path.join(root, fname)

                organization = get_doctype(path)
                if organization == 'Amnesty International':
                    doc = AI_doc(path)
                elif organization == 'Critique':
                    doc = CR_doc(path)
                elif organization == 'Human Rights Watch':
                    doc = HRW_doc(path)
                elif organization == 'State Department':
                    doc = SD_doc(path)
                else:
                    raise ValueError('No organization')
                
                outfile.write(json.dumps(doc.export_dict()))
                outfile.write('\n')

                i += 1
                print 'Processed %d files' %i
