import os
import urllib
import sys

from nameparser import HumanName


if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scrapers.new_xhelper import Xhelper, Helpers, Sheet


class SheetWithNamesHelper:
    @classmethod
    def find_first_name_from_name(cls, name):
        '''
        please don't judge me.
        this is a much harder problem than it seems
        '''
        name = HumanName(name)
        if '.' in name.first or len(name.first) < 2:
            if name.middle:
                return name.middle
            else:
                return name.first
        else:
            return name.first


class SheetWithNames:    
    def __init__(self, xhelper, sheet):
        self.xhelper = xhelper
        self.sheet = Sheet(self.xhelper, sheet)

        # names
        self.name_col_num = Helpers.get_column_number(self.sheet, 'name')
        self.all_names = Helpers.get_all_column_vals_as_row(self.sheet, self.name_col_num)
        self.all_first_names = self.find_first_names_from_names()

    def find_first_names_from_names(self):
        all_first_names = []
        for name in self.all_names:
            first_name = SheetWithNamesHelper.find_first_name_from_name(name)
            all_first_names.append(first_name)
        return all_first_names

    def run(self):
        to_write = [
            ['first-name-best-guess', self.all_first_names]
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
            sheet_with_names = SheetWithNames(xhelper = xhelper, sheet = sheet)
            sheet_with_names.run()

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