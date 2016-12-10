import os
import urllib
import sys

from nameparser import HumanName

if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scrapers.new_xhelper import Xhelper, Helpers, Sheet

class SheetWithJournalsHelpers:
    @classmethod
    def add_the_to_journal(cls, journal):
        journal_word_list = journal.split(" ")
        if journal_word_list[0].lower() == "journal":
            journal_word_list.insert(0, 'the')
            return " ".join(journal_word_list)
        else:
            return journal

class SheetWithJournals:
    def __init__(self, xhelper, sheet):
        self.xhelper = xhelper
        self.sheet = Sheet(self.xhelper, sheet)

        # names
        self.journal_col_num = Helpers.get_column_number(self.sheet, 'journal')
        self.all_journals = Helpers.get_all_column_vals_as_row(self.sheet, self.journal_col_num)
        self.all_edited_journals = self.add_the_to_relevant_journals()

    def add_the_to_relevant_journals(self):
        all_edited_journals = []
        for journal in self.all_journals:
            edited_journal = SheetWithJournalsHelpers.add_the_to_journal(journal)
            all_edited_journals.append(edited_journal)
        return all_edited_journals

    def run(self):
        to_write = [
            ['edited-journal', self.all_edited_journals],
        ]
        self.sheet.write_to_sheet(to_write)


def google_sheet_main_init(spread_sheet_name):
    f = os.environ['XPYTHON_GSPREAD_CONFIG_FILE']
    opener = urllib.URLopener()
    myfile = opener.open(f)
    file_as_json_str = myfile.read()

    sheet_name = raw_input("What's the name of the sheet? ").strip().lower()
    # sheet_name = "final list"

    print 'finding sheet'
    xhelper = Xhelper(json_file_name = file_as_json_str, spread_sheet_name = spread_sheet_name)
    for sheet in xhelper.worksheets_list:
        if sheet_name in sheet.title.lower():
            print 'found sheet'
            print sheet.title.lower()
            sheet_with_journals = SheetWithJournals(xhelper = xhelper, sheet = sheet)
            sheet_with_journals.run()

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