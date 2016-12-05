import requests
import bs4
import pudb
import os
import urllib
import gspread
import sys
import retinasdk
import json

from nltk.corpus import wordnet
from itertools import chain
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

if __name__ != '__main__':
    from scraper.models import Journal, Author, Article, Brick

if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scrapers.new_xhelper import Xhelper, Helpers, Sheet


class SheetToScoreHelpers:
    def __init__(self, countdown):
        self.cortical_api_key = "03dc0630-bb14-11e6-a057-97f4c970893c"
        self.cortical_full_client = retinasdk.FullClient(self.cortical_api_key, apiServer="http://api.cortical.io/rest", retinaName="en_associative")
        self.cortical_api_call_countdown = countdown
    
    @classmethod
    def score_by_levenshtein(cls, abstract, keywords):
        '''
        takes an array of keywords
        like ['terrorism', 'radicalization', 'refugees', 'daesh', 'syria', 'iraq', 'jihad']
        and a string, in this case an article abstract
        returns levenshtein similarity score
        as float between 0 and 1
        '''
        keywords = " ".join(keywords)
        return fuzz.ratio(abstract, keywords)

    @classmethod
    def build_cortical_text_compare_data_structure(cls, text1, text2, text1_type="text", text2type="text"):
        return [{"text": text1}, {"text": text2}]

    @classmethod
    def synonyms(cls, word):
        '''
        takes a word as a string, like 'change'
        returns a set of synonyms
        like [u'interchange', u'convert', u'variety', u'vary', u'exchange', u'modify', u'alteration', u'switch', u'commute', u'shift', u'modification', u'deepen', u'transfer', u'alter', u'change']
        '''
        synonyms = wordnet.synsets(word)
        return set(chain.from_iterable([word.lemma_names() for word in synonyms]))

    @classmethod
    def score_by_jeff_with_synonyms(cls, abstract, keywords):
        '''
        takes an array of keywords
        like ['terrorism', 'radicalization', 'refugees', 'daesh', 'syria', 'iraq', 'jihad']
        and a string, in this case an article abstract
        counts unique occurences of keywords in the abstract as 1
        counts unique occurences of synonyms of those keywords as 0.3
        returns that total score
        '''
        count = 0
        jeff = 0.3

        synonyms_list_of_lists = [SheetToScoreHelpers.synonyms(word) for word in keywords]

        flattened_synonyms = [item for sublist in synonyms_list_of_lists for item in sublist]

        flattened_synonyms = [word.replace("_", " ") for word in flattened_synonyms]

        for word in keywords:
            if word.lower() in abstract.lower():
                count += 1

        for word in flattened_synonyms:
            if word.lower() in abstract.lower():
                count += jeff

        return count 

    def single_score_by_cortical_api(self, abstract, keywords):
        '''
        takes an array of keywords
        like ['terrorism', 'radicalization', 'refugees', 'daesh', 'syria', 'iraq', 'jihad']
        and a string, in this case an article abstract
        .compare returns a json blob like
        {
            "jaccardDistance": 0.925764192139738,
            "cosineSimilarity": 0.1382113821138211,
            "sizeLeft": 984,
            "overlappingAll": 136,
            "overlappingLeftRight": 0.13821138211382114,
            "overlappingRightLeft": 0.13821138211382114,
            "sizeRight": 984,
            "weightedScoring": 22.979370274207152,
            "euclideanDistance": 0.8617886178861789
        }
        right now, this method just records the "weightedScoring" value
        hitting this api endpoint: http://api.cortical.io/Compare.htm#!/compare/compare_post_0
        see documentation on what other scores mean here: 
        '''

        keywords = " ".join(keywords)

        try:
            scores_as_json = self.cortical_full_client.compare(json.dumps([{"text": abstract}, {"text": keywords}]))
            
            print(self.cortical_api_call_countdown)
            self.cortical_api_call_countdown -= 1

        except retinasdk.client.exceptions.CorticalioException as e:
            if e.message == 'Response 422: {"errors":["elements[0].text The input text was empty. (was )"]}':
                return 0
            else:
                pu.db

        return scores_as_json.weightedScoring

    def bulk_score_by_cortical_api(self, abstracts, keywords):
        '''
        hits bulk api endpoint for def single_score_by_cortical_api
        otherwise, does the same as def single_score_by_cortical_api
        '''

        keywords = " ".join(keywords)

        # cortical api can't accept empty strings or None.
        # so send them just a random { to avoid errors
        for i, abstract in enumerate(abstracts):
             if not abstract:
                 abstracts[i] = '{'

        abstracts_and_keywords = [SheetToScoreHelpers.build_cortical_text_compare_data_structure(abstract, keywords) for abstract in abstracts]
        resp = self.cortical_full_client.compareBulk(json.dumps(abstracts_and_keywords))
        return [el.weightedScoring for el in resp]
        

class SheetToScore:
    
    def __init__(self, xhelper, sheet):
        self.xhelper = xhelper
        self.sheet = Sheet(self.xhelper, sheet)

        # keywords
        self.keyword_col_num = Helpers.get_column_number(self.sheet, 'keywords')
        # list comp removes empty strings
        self.all_keywords = [x for x in Helpers.get_all_column_vals_as_row(self.sheet, self.keyword_col_num) if x]

        # abstracts
        self.abstract_col_num = Helpers.get_column_number(self.sheet, 'abstract')
        self.all_abstracts = Helpers.get_all_column_vals_as_row(self.sheet, self.abstract_col_num)

        ### good scores
        # levenshtein
        self.all_abstracts_scores_by_levenshtein = self.score_by_levenshtein()
        # coritcal
        self.all_abstract_scores_by_cortical = self.score_by_cortical_api(self.all_keywords)
        # jeff
        self.all_abstract_scores_by_jeff = self.score_by_jeff(self.all_keywords)

        ### bad scores
        # cortical
        self.badword_col_num = Helpers.get_column_number(self.sheet, 'badwords')
        self.all_badwords = [x for x in Helpers.get_all_column_vals_as_row(self.sheet, self.badword_col_num) if x]
        self.all_badwords_scores_by_cortical = self.score_by_cortical_api(self.all_badwords)
        # jeff
        self.all_badwords_scores_by_jeff = self.score_by_jeff(self.all_badwords)

    def score_by_cortical_api(self, array_of_words):
        ### Code for single score api
        # all_abstracts_scores = []
        # cortical_api_full_client = SheetToScoreHelpers(len(self.all_abstracts))
        # for abstract in self.all_abstracts:
        #     score = cortical_api_full_client.single_score_by_cortical_api(abstract, self.all_keywords)
        #     all_abstracts_scores.append(score)

        ### Code for bulk score api
        cortical_api_full_client = SheetToScoreHelpers(len(self.all_abstracts))
        return cortical_api_full_client.bulk_score_by_cortical_api(self.all_abstracts, array_of_words)

    def score_by_levenshtein(self):

        all_abstracts_scores = []
        for abstract in self.all_abstracts:
            score = SheetToScoreHelpers.score_by_levenshtein(abstract, self.all_keywords)
            all_abstracts_scores.append(score)
        return all_abstracts_scores

    def score_by_jeff(self, array_of_words):
        all_abstracts_scores = []
        for abstract in self.all_abstracts:
            score = SheetToScoreHelpers.score_by_jeff_with_synonyms(abstract, array_of_words)
            all_abstracts_scores.append(score)
        return all_abstracts_scores

    def run(self):
        to_write = [
            ['levenshtein', self.all_abstracts_scores_by_levenshtein],
            ['coritcal', self.all_abstract_scores_by_cortical],
            ['jeff with synonyms', self.all_abstract_scores_by_jeff],
            ['bw-cortical', self.all_badwords_scores_by_cortical],
            ['bw-jeff', self.all_badwords_scores_by_jeff]
        ]
        self.sheet.write_to_sheet(to_write)
        

def google_sheet_main_init(spread_sheet_name):
    f = os.environ['XPYTHON_GSPREAD_CONFIG_FILE']
    opener = urllib.URLopener()
    myfile = opener.open(f)
    file_as_json_str = myfile.read()

    # sheet_name = raw_input("What's the name of the sheet? ").strip().lower()
    sheet_name = "final list"

    print 'finding sheet'
    xhelper = Xhelper(json_file_name = file_as_json_str, spread_sheet_name = spread_sheet_name)
    for sheet in xhelper.worksheets_list:
        if sheet_name in sheet.title.lower():
            print 'found sheet'
            print sheet.title.lower()

            sheet_to_score = SheetToScore(xhelper = xhelper, sheet = sheet)
            sheet_to_score.run()

def main():

    sheet_name = "Copy of polisci"
    google_sheet_main_init(spread_sheet_name = sheet_name)  

    # sheet_name = raw_input("whatchur Google SpreadSheet name? ")
    # print("This is the email address you have to share that sheet with: ")
    # print("123114053576-compute@developer.gserviceaccount.com")
    # sheet_share_confirm = raw_input("Have you done that yet? (enter y or n): ").rstrip()
    # while sheet_share_confirm != "y" and sheet_share_confirm != "n":
    #     sheet_share_confirm = raw_input("You bricked it. Have you done that yet? (enter y or n): ").rstrip()
    # if sheet_share_confirm == "y":
    #     google_sheet_main_init(spread_sheet_name = sheet_name)
    # else:
    #     print("well go do that then")

if __name__ == '__main__':
    main()