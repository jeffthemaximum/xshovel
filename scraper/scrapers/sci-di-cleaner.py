import os
import urllib
import pudb
from new_xhelper import Xhelper, Sheet, Helpers, Scraper

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

        self.abstract_col_num = Helpers.get_column_number(self.sheet, 'abstract')
        self.all_abstracts = Helpers.get_all_column_vals_as_row(self.sheet,self.abstract_col_num)

        self.title_col_num = Helpers.get_column_number(self.sheet, 'title')
        self.all_titles = Helpers.get_all_column_vals_as_row(self.sheet,self.title_col_num)

        self.all_soups = [None] * len(self.all_urls)
        # self.found_first_names = [None] * len(self.all_emails)
        # self.found_emails = [None] * len(self.all_emails)
        print "done scidi init"

    def run(self):
        # find author if missing
        for idx, author in enumerate(self.all_authors):
            if author == "":

                soup = self.get_or_find_soup(idx)
                author = self.scrape_author(soup)
                # write author back to sheet
                # 1 - get cell str
                col_letter = Helpers.get_col_letter_from_number(self.author_col_num, fixer=0)
                cell_str = Helpers.get_cell_string(col_letter, idx, offset=1)
                # 2 - write to sheet
                self.sheet.sheet.update_acell(cell_str, author)
                # 3 - write author back to list of authors
                self.all_authors[idx] = author

        # find email if missing
        for idx, email in enumerate(self.all_emails):
            if email == "":
                soup = self.get_or_find_soup(idx)
                email = self.scrape_email(soup)

                col_letter = Helpers.get_col_letter_from_number(self.email_col_num, fixer=0)
                cell_str = Helpers.get_cell_string(col_letter, idx, offset=1)

                self.sheet.sheet.update_acell(cell_str, email)

                self.all_emails[idx] = email

        # find abstract if missing
        for idx, abstract in enumerate(self.all_abstracts):
            if abstract == "":
                soup = self.get_or_find_soup(idx)
                abstract = self.scrape_abstract(soup)

                col_letter = Helpers.get_col_letter_from_number(self.abstract_col_num, fixer=0)
                cell_str = Helpers.get_cell_string(col_letter, idx, offset=1)

                self.sheet.sheet.update_acell(cell_str, abstract)

                self.all_abstracts[idx] = abstract

        # find title if missing
        for idx, title in enumerate(self.all_titles):
            if title == "":
                soup = self.get_or_find_soup(idx)
                title = self.scrape_title(soup)

                col_letter = Helpers.get_col_letter_from_number(self.title_col_num, fixer=0)
                cell_str = Helpers.get_cell_string(col_letter, idx, offset=1)

                self.sheet.sheet.update_acell(cell_str, title)

                self.all_titles[idx] = title


    def get_or_find_soup(self, idx):
        if self.all_soups[idx] is None:
            # find author
            soup = self.get_soup(idx)
            self.all_soups[idx] = soup
        else:
            soup = self.all_soups[idx]
        return soup

    def get_soup(self, idx):
        url = self.all_urls[idx]
        print url
        scraper = Scraper(url = url, kind = 'scidi')
        return scraper.soup

    def scrape_abstract(self, soup):
        # abstract_div = soup.find("div", {"class": "abstract"})
        # abstract_div_children = abstract_div.findChildren()

        abstract_nav_str = soup.find(text="Abstract")
        if abstract_nav_str:
            abstract_element = abstract_nav_str.parent.findNext("p")
            text = abstract_element.get_text()
            print text
            return text

    def scrape_title(self, soup):

        title_str = soup.find("h1", {"class": "svTitle"})
        text = title_str.get_text()
        print text
        return text


    def scrape_author(self, soup):
        author = soup.find("a", {"class": "authorName"})
        return author.text

    def scrape_email(self, soup):
        try:
            email = soup.find("a", {"class": "auth_mail"})['href'].split(':')[1]
        except:
            email = ""
        return email

if __name__ == '__main__':

    sheet_name = raw_input("whatchur Google SpreadSheet name? ")
    print("This is the email address you have to share that sheet with: ")
    print("123114053576-compute@developer.gserviceaccount.com")
    sheet_share_confirm = raw_input("Have you done that yet? (enter y or n): ").rstrip()

    while sheet_share_confirm != "y" and sheet_share_confirm != "n":
        sheet_share_confirm = raw_input("You bricked it. Have you done that yet? (enter y or n): ").rstrip()

    if sheet_share_confirm == "y":
        f = os.environ['XPYTHON_GSPREAD_CONFIG_FILE']
        opener = urllib.URLopener()
        myfile = opener.open(f)
        file_as_json_str = myfile.read()
        xhelper = Xhelper(json_file_name = file_as_json_str, spread_sheet_name = sheet_name)

        for sheet in xhelper.worksheets_list:
            if 'science direct' in sheet.title.lower():
                print sheet.title
                sci_di = SciDi(xhelper = xhelper, sheet = sheet)
                sci_di.run()

    else:
        print "Well go do that then"

