# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import codecs
import sys
import os
import urllib
import pudb
import string

from nameparser import HumanName


if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scrapers.new_xhelper import Xhelper, Helpers, Sheet

class SheetWithWeirdCharsHelpers:

    @classmethod
    def clear_weird_chars(cls, word):

        # â€™ == '\xe2\u20ac\u2122'
        # '\xe2\u20ac\u2122' should be "'"
        if '\xe2\u20ac\u2122' in word:
            word = word.replace('\xe2\u20ac\u2122', "'")

        # â€˜ == '\xe2\u20ac\u02dc'
        # '\xe2\u20ac\u02dc' should be "'"
        if '\xe2\u20ac\u02dc' in word:
            word = word.replace('\xe2\u20ac\u02dc', "'")

        # â€œ == '\xe2\u20ac\u0153'
        # '\xe2\u20ac\u0153' should be "'"
        if '\xe2\u20ac\u0153' in word:
            word = word.replace('\xe2\u20ac\u0153', "'")

        # â€ == '\xe2\u20ac'
        # '\xe2\u20ac' should be "'"
        if '\xe2\u20ac' in word:
            word = word.replace('\xe2\u20ac', "'")

        # â == '\xe2'
        # '\xe2' should be ''
        if '\xe2' in word:
            word = word.replace('\xe2', '')

        return word.strip()

class SheetWithWeirdChars:
    def __init__(self, xhelper, sheet):
        self.xhelper = xhelper
        self.sheet = Sheet(self.xhelper, sheet)

        # titles
        self.title_col_num = Helpers.get_column_number(self.sheet, 'title')
        self.all_titles = Helpers.get_all_column_vals_as_row(self.sheet, self.title_col_num)
        self.all_cleared_titles = self.clear_weird_chars_from_title()

    def clear_weird_chars_from_title(self):
        cleared_titles = []
        for title in self.all_titles:
            cleared_title = SheetWithWeirdCharsHelpers.clear_weird_chars(title)
            cleared_titles.append(cleared_title)
        return cleared_titles

    def run(self):
        to_write = [
            ['titles-without-wierd-chars', self.all_cleared_titles]
        ]
        self.sheet.write_to_sheet(to_write)


def google_sheet_main_init(spread_sheet_name):
    f = os.environ['XPYTHON_GSPREAD_CONFIG_FILE']
    opener = urllib.URLopener()
    myfile = opener.open(f)
    file_as_json_str = myfile.read()

    sheet_name = raw_input("What's the name of the sheet? ").strip().lower()

    print 'finding sheet'
    xhelper = Xhelper(json_file_name = file_as_json_str, spread_sheet_name = spread_sheet_name)
    for sheet in xhelper.worksheets_list:
        if sheet_name in sheet.title.lower():
            print 'found sheet'
            print sheet.title.lower()

            sheet_with_weird_chars = SheetWithWeirdChars(xhelper = xhelper, sheet = sheet)
            sheet_with_weird_chars.run()

def main():

    sheet_name = raw_input("whatchur Google SpreadSheet name? ")
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