import os
import urllib
from new_xhelper import Xhelper, Sheet, Helpers

f = os.environ['XPYTHON_GSPREAD_CONFIG_FILE']
opener = urllib.URLopener()
myfile = opener.open(f)
file_as_json_str = myfile.read()
xhelper = Xhelper(json_file_name = file_as_json_str, spread_sheet_name = "Copy of Herpetology abstracts")

class SciDi:
    def __init__(self, xhelper, sheet):
        self.xhelper = xhelper
        # self.scrape_id = scrape_id
        # self.message = message
        print 'getting sheet'
        self.sheet = Sheet(self.xhelper, sheet)
        print 'got sheet'
        # Group('scraper-'+str(self.scrape_id), channel_layer=self.message.channel_layer).send({'text': 'got sheet'})
        
        self.author_col_num = Helpers.get_column_number(self.sheet, 'author')
        self.all_authors = Helpers.get_all_column_vals_as_row(self.sheet, self.author_col_num)
        print self.all_authors

        self.email_col_num = Helpers.get_column_number(self.sheet, 'email')
        self.all_emails = Helpers.get_all_column_vals_as_row(self.sheet, self.email_col_num)
        print self.all_emails
        
        self.url_col_num = Helpers.get_column_number(self.sheet, 'pageUrl')
        self.all_urls = Helpers.get_all_wiley_urls(self.sheet, self.url_col_num)
        self.all_urls = Helpers.get_all_column_vals_as_row(self.sheet, self.url_col_num)
        print self.all_urls
        
        self.all_soups = []
        # self.found_first_names = [None] * len(self.all_emails)
        # self.found_emails = [None] * len(self.all_emails)
        print "done scidi init"


for sheet in xhelper.worksheets_list:
    if 'science direct' in sheet.title.lower():
        print sheet.title
        sci_di = SciDi(xhelper = xhelper, sheet = sheet)