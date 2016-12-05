import os
import urllib
import sys
import pudb

from nameparser import HumanName

if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scrapers.new_xhelper import Xhelper, Helpers, Sheet

class SheetWithWeirdCharsHelpers:
    @classmethod
    def remove_values_from_list(cls, the_list, val):
        return [value for value in the_list if value != val]

    @classmethod
    def clear_weird_chars(cls, title):

        weird_chars = ['\xc3\xa2']
        for weird_char in weird_chars:
            if weird_char in title:
                title_list = title.split(" ")
                title_list = SheetWithWeirdCharsHelpers.remove_values_from_list(title_list, weird_chars)
                title0 = " ".join(title_list)
        return title



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
            ['titles-without-\xc3\xa2', self.all_cleared_titles]
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

            sheet_with_weird_chars = SheetWithWeirdChars(xhelper = xhelper, sheet = sheet)
            sheet_with_weird_chars.run()

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