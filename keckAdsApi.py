import numpy as np
import pandas as pd
import requests
import urllib.request
import urllib
import time
import re
from nltk.stem import PorterStemmer
import json
import sys
from progressbar import ProgressBar
import os

class Keck_ADS_API(object):

    def __init__(self):
        self.instruments = 'kcwi nirspec nirc deimos nires lris mosfire esi hises osiris'.split(' ') # instruments
        self.keck_str = ['keck', 'keck observatory', 'wm keck observatory']
        self.cwd = os.getcwd()
        try:
            self.df = pd.read_csv(self.cwd+'/ADS_exportTObibDB.csv')
        except:
            self.df = None
        self.keck_papers = []
        self.counter_keck = 0
        self.counter_instrument = 0
        self.doc_len = 0
        #self.token="rwsDbVt7K2fPw9Dmuvt8aGQT6SM9SEiD1uvL1V52"
        #self.token='wci61Rh6Vj0NLrSk67rjHblKynMM1If4TnAAslrA'
        self.token='6wxQSKv6oQHm6q0ho8bVlgjETKcBaoDWWiXMRZ4x' # peggi's
        self.token='UZtOCwFDekUFOL4HIppwFENnMTNttBlvth2uWSHW' # tfcox2019

    def search(self, query, rows = 2000):
        v = sys.version
        if int(v[0]) == 2:
            encoded_query = urllib.quote_plus(query)
        else:
            from urllib.parse import urlencode, quote_plus
            query = {'q':query, 'rows':rows, 'fl':'bibcode body title author volume page pubdate year identifier bibcode doi citation_count bibstem'}
            encoded_query = urlencode(query,quote_via=quote_plus)
        # print(encoded_query)


        # the query parameters can be included as part of the URL
        r = requests.get("https://api.adsabs.harvard.edu/v1/search/query?"+encoded_query,\
                        headers={'Authorization': 'Bearer ' + self.token})
        #print(r)
        #print(r.json())
        try:
            r = r.json()
        except:
            print('Request was not allowed: %s'(query['q']))

        try:
            responses = r['response']
            responseHeader = r['responseHeader']
            keck_papers = self._check_papers(responses['docs'])
        except:
            print(r.keys())
            keck_papers = self.keck_papers

        keck_papers = self._check_papers(responses['docs'])
        return keck_papers

    def cite_by_bibcode(self, bibcodes):
        if isinstance(bibcodes, str):
            if len(bibcode) == 19:
                bibcodes = [bibcodes]
            else:
                if bibcodes.contains('\\n'):
                    bibcodes = bibcodes.split('\\n')
                else:
                    bibcodes = bibcodes.split(' ')

        length = 19
        bibcodes = list(set(list(bibcodes)))
        cleaned_bibcodes = []
        for code in bibcodes:
            if len(code) == length:
                cleaned_bibcodes.append(code)

        pbar = ProgressBar()
        for bibcode in pbar(cleaned_bibcodes):
            self.search('bibcode:%s'%bibcode, rows = 1)


    def add(self):
        if self.df is None:
            #print(self.keck_papers)
            self.df = pd.DataFrame(self.keck_papers).sort_values(by='Year', ascending=False)
        else:
            counter_there = 0
            for paper in self.keck_papers:
                if paper['Bibcode'] not in list(self.df['Bibcode']):
                    self.df = self.df.append([paper], ignore_index=True)
                else:
                    counter_there += 1
            self.df.sort_values(by='Year', ascending=False)

            print('Documents added: %s'%(len(self.keck_papers)-counter_there))
            print('Documents already there: %s'%(counter_there))
        print('%s of %s likely keck related'%(self.counter_keck, self.doc_len))
        print('%s of %s have keck instrument in text'%(self.counter_instrument, self.doc_len))

        self.keck_papers = []
        self.counter_keck = 0
        self.counter_instrument = 0
        self.doc_len = 0

    def _check_papers(self, docs):
        counter_instrument = 0
        counter_keck = 0
        pbar = ProgressBar()

        for paper in pbar(docs):
            try:
                temp_body = self._clean_string(paper['body']).split(' ')
            except:
                temp_body = 'this does not have K3CK in it.'

            if 'keck' in temp_body:
                instrument_dict = {}
                for instrument in self.instruments:
                    value = temp_body.count(instrument)
                    if value > 0:
                        instrument_dict[instrument] = value
                columns = self._create_columns(paper)
                columns['Instruments'] = instrument_dict
                self.keck_papers.append(columns)
                if len(instrument_dict) > 0:
                    counter_instrument +=1
                counter_keck += 1


        self.counter_keck += counter_keck
        self.counter_instrument += counter_instrument
        self.doc_len += len(docs)
        # print('%s of %s likely keck related'%((counter_keck), len(docs)))
        # print('%s of %s have keck instrument in text'%(counter_instrument, len(docs)))
        # print('Number of papers not added: %s'%len(self.keck_papers))
        # print('-------------------------------------------------------------------------')
        # print(keck_papers[0]['bib'])
        # print(keck_papers[1]['bib'])
        return self.keck_papers


    def _clean_string(self, line):
        '''takes a string and processes it (removes digits, makes lowercase, ...)

        Parameters
        ----------
        line : str
            a raw line that needs to be cleaned

        Returns
        -------
        str
            the cleaned string
        '''
        string = line
        #REMOVE_NUMBERS = re.compile("[0-9]") # Init Remove any number
        REPLACE_NO_SPACE = re.compile("[.;:!\'?,\"\(\)\[\]]|[\\n]") # Init replace these characters without a space
        REPLACE_WITH_SPACE = re.compile("(<br\s*/><br\s*/>)|(\-)|(\/)|[+-_]") # Init replace these characters with a space
        ps = PorterStemmer() # Init a PorterStemmer object
        #print(line)
        #string = REMOVE_NUMBERS.sub('', line) # Remove numbers
        #print(string)
        string = string.lower() # Make letters lowercase
        string = string.strip() # strip all dead space
        string = string.strip("\n\r\s") # strip newlines and \r and \s
        temp = '' # Init 'temp' string
        string = REPLACE_NO_SPACE.sub('', string) # replace characters in REPLACE_NO_SPACE
        string = REPLACE_WITH_SPACE.sub(" ", string) # replace characters in REPLACE_WITH_SPACE with a space
        #print(string)
        string = string.strip() # Strip all dead space
        return string


    def _create_columns(self, paper):
        try:
            if len(paper['author']) > 3:
                authors = list(paper['author'][:3])
            elif len(paper['author']) == 4:
                authors = list(paper['author'])
            else:
                authors = list(paper['author'])


            for i in range(len(authors)):
                first_last = authors[i].split(' ')
                if len(first_last) == 1:
                    authors[i] = first_last[0]
                elif ',' in authors[i]:
                    first_last = authors[i].split(', ')
                    authors[i] = first_last[0] + ' ' + first_last[1][0] + '.'
                else:
                    authors[i] = first_last[-1] + ' ' + first_last[0][0] + '.'

            if len(paper['author']) > 3 and not len(paper['author']) == 4:
                authors.append('et. al.')

            author_string = " | ".join(authors)
        except:
            author_string = ''

        arxiv = ''
        for code in paper['identifier']:
            if code[:5] == 'arXiv':
                arxiv = code
        try:
            volume = '%s'%paper['volume']
        except:
            volume = ''

        try:
            page = '%s'%paper['page'][0]
        except:
            page = ''

        try:
            doi = '%s'%paper['doi'][0]
        except:
            doi = ''

        try:
            title = paper['title'][0]
        except:
            title = ''

        try:
            date = paper['pubdate'][:7].replace("-", " ")
        except:
            date = ''

        try:
            year = int(paper['year'])
        except:
            year = ''

        try:
            bibcode = paper['bibcode']
        except:
            bibcode = ''

        try:
            bibstem = paper['bibstem'][0]
        except:
            bibstem = ''

        publication = '%s %s %s'%(bibstem, volume, page)

        the_columns = {'Title': title,
                        'Author':author_string,
                        'Publication':publication,
                        'Date':date,
                        'Year':year,
                        'URL':arxiv,
                        'Bibcode':bibcode,
                        'DOI':doi}
        return the_columns

    def export(self):
        try:
            keck_papers = self.keck_papers
        except:
            'Need to search something first.'

        #df = pd.DataFrame(self.keck_papers).sort_values(by='year', ascending=False)
        bibcodes = self.df['Bibcode']
        print('In Folder: '+self.cwd)
        bibcodes.to_csv(self.cwd+'/bibcode_test.txt', index=False, header = True)
        self.df.to_csv(self.cwd+'/ADS_exportTObibDB_test.csv', index=False)
