import requests
import bs4
import pudb
import os
import urllib

from datetime import datetime
from operator import itemgetter

if __name__ != '__main__':
    from scraper.models import Journal, Author, Article, Brick

if __name__ == '__main__':
    from new_xhelper import Sheet, Scraper, Helpers

class Wiley:
    def __init__(self, xhelper, sheet, scrape_id, message):
        self.xhelper = xhelper
        self.sheet = Sheet(self.xhelper, sheet)

        self.url_col_num = Helpers.get_column_number(self.sheet, 'pageUrl')
        self.all_urls = Helpers.get_all_wiley_urls(self.sheet, self.url_col_num)
        self.all_urls = Helpers.get_all_column_vals_as_row(self.sheet, self.url_col_num)
        print self.all_urls

        self.all_soups = self.get_all_soups()

        

        # self.author_col_num = Helpers.get_column_number(self.sheet, 'author')
        # self.all_emails = Helpers.get_all_column_vals_as_row(self.sheet, self.email_col_num)
        self.all_urls = Helpers.get_all_wiley_urls(self.sheet, self.url_col_num)
        # self.all_urls = self.get_all_urls()
        # self.all_urls = Helpers.get_all_column_vals_as_row(self.sheet, self.url_col_num)
        # self.all_authors = Helpers.get_all_column_vals_as_row(self.sheet, self.author_col_num)
        self.all_soups = []
        # self.found_first_names = [None] * len(self.all_emails)
        # self.found_emails = [None] * len(self.all_emails)
        print "done wiley init"
        Group('scraper-'+str(self.scrape_id), channel_layer=self.message.channel_layer).send({'text': "done wiley init"})

    def clean_author_email(self, author):
        author = author.encode('ascii', 'replace').split(' ')
        return ["".join([char for char in el if char.isalpha()]) for el in author if len(el) > 0]

    def get_first_name_by_url(self, url):
        print url
        Group('scraper-'+str(self.scrape_id), channel_layer=self.message.channel_layer).send({'text': url})
        scraped = Scraper(url)
        self.all_soups.append(scraped)
        try:
            authors_as_list = scraped.soup.find("ol", {"id": "authors"}).find_all('li')
        except:
            return ''
        authors_as_text_list = [el.text for el in authors_as_list]
        for author in authors_as_text_list:
            if '*' in author:
                return author
        for author in authors_as_text_list:
            # if † in author name
            if author is not None:
                try:
                    if "\xe2\x80\xa0".decode('utf-8') in cgi.escape(author):
                        return author
                except:
                    pu.db
        # try corresponding author
        if authors_as_list[0] is not None:
            return authors_as_text_list[0]
        error = "ERROR WITH WILEY. COULDN'T FIND FIRST NAME FOR " + url
        print(error)
        self.xhelper.errors.append(error)
        return ''

    def get_first_name_if_initial(self, name, idx=0):
        # catch case like ['T', 'Whitten']
        # if self.all_urls[idx] == 'http://onlinelibrary.wiley.com/wol1/doi/10.1111/oik.01745/abstract':
        #     pu.db
        email = ''
        try:
            name[0]
        except:
            return ''
        if len(name[0]) == 1:
            email = self.get_email(idx)
            username = email.split('@')[0]
            if '.' in username:
                first_name = username.split('.')[0]
                if len(first_name) > 1:
                    return first_name
            # handle case like ['E', 'J', 'Cartwright'] and email='ecartw2@emory.edu'
            else:
                last_name = name[-1] if Helpers.and_jr_check(name[-1]) else name[-2]
                soup = self.all_soups[idx]
                correspondence = soup.soup.find("p", {"id": "correspondence"})
                if correspondence is None:
                    correspondence = soup.soup.find("p", {"id": "contactDetails"})
                try:
                    correspondence_text = correspondence.text.encode('ascii', 'ignore')
                except:
                    return ''
                correspondence_text_list = ["".join([char for char in el if char.isalpha()]) for el in correspondence_text.split(' ')]
                # if self.all_urls[idx] == 'http://onlinelibrary.wiley.com/wol1/doi/10.1111/oik.01745/abstract':
                #     pu.db
                if last_name in correspondence_text_list or last_name.title() in correspondence_text_list:
                    try:
                        last_name_idx = correspondence_text_list.index(last_name)
                    except ValueError:
                        last_name_idx = correspondence_text_list.index(last_name.title())
                    correspondence_idx = correspondence_text_list.index('Correspondence') if 'Correspondence' in correspondence_text_list else None
                    if correspondence_idx:
                        name_after_correspondence = correspondence_text_list[correspondence_idx + 1]
                        if name_after_correspondence == '':
                            name_after_correspondence = correspondence_text_list[correspondence_idx + 2]
                        return name_after_correspondence
                    else:
                        first_name = correspondence_text_list[last_name_idx - 1] if len(correspondence_text_list[last_name_idx - 1]) != 1 else correspondence_text_list[last_name_idx - 2]
                        return first_name
                else:
                    # handle case like ['J', 'Sean', 'Doody'] and email='jseandoody@gmail.com'
                    # and correspondence_text='*Corresponding author. E-mail: jseandoody@gmail.com'
                    if len(name) == 3:
                        middle_name = name[1]
                        if len(middle_name) > 1:
                            return middle_name
        if len(name[0]) > 1:
            return name[0]
        else:
            print name[0]
            print "URLURLURL" + self.all_urls[idx]
            return ''
            


    def get_first_names(self):
        names = [self.get_first_name_by_url(url) for url in self.all_urls]
        cleaned_names = [self.clean_author_email(name) for name in names]
        first_names = [self.get_first_name_if_initial(idx=i, name=name) for i, name in enumerate(cleaned_names)]
        return first_names

    def get_email(self, idx):
        email = ''
        soup = self.all_soups[idx]
        try:
            correspondence = soup.soup.find("p", {"id": "correspondence"})
        except:
            return ''
        if correspondence is None:
            try:
                correspondence = soup.soup.find("p", {"id": "contactDetails"})
                email = correspondence.find("span", {"class": "email"}).text.split('(')[1].split(')')[0]
            except:
                try:
                    email = soup.soup.find("a", {"title": "Link to email address"}).text
                except:
                    return ''
        if email != '' or correspondence.find('a') is not None:
            email = correspondence.find('a').text.encode('ascii', 'ignore') if email == '' else email
        return email


    def get_emails(self):
        emails = [self.get_email(idx=i) for i, url in enumerate(self.all_soups)]
        return emails

    def wiley(self):
        # return and print error if 
        if self.url_col_num == None:
            error = "ERROR WITH WILEY. MAKE SURE THERE'S A COLUMN NAMED 'pageUrl'"
            print(error)
            self.xhelper.errors.append(error)
            return None
        # else get list of all emails
        else:

            # TODO get first name
            first_names = self.get_first_names()
            cell_list = Helpers.get_cell_list(self.sheet.sheet, first_names)
            col_letter = Helpers.get_last_col_letter(self.sheet.sheet)
            self.sheet.sheet.update_acell(col_letter + '1', 'names')
            for i, cell in enumerate(first_names):
                cell_list[i].value = first_names[i].title()
            self.sheet.sheet.update_cells(cell_list)
            print first_names
            Group('scraper-'+str(self.scrape_id), channel_layer=self.message.channel_layer).send({'text': json.dumps(first_names)})

            # TODO get email
            emails = self.get_emails()
            cell_list = Helpers.get_cell_list(self.sheet.sheet, emails)
            col_letter = Helpers.get_last_col_letter(self.sheet.sheet)
            self.sheet.sheet.update_acell(col_letter + '1', 'email')
            for i, cell in enumerate(emails):
                cell_list[i].value = emails[i]
            self.sheet.sheet.update_cells(cell_list)
            print emails
            Group('scraper-'+str(self.scrape_id), channel_layer=self.message.channel_layer).send({'text': json.dumps(emails)})

            # check if email is international
            # iterate through list of emails
            # make column to right of last column
            au_col_letter = Helpers.get_last_col_letter(self.sheet.sheet)
            # make header "au emails"
            self.sheet.sheet.update_acell(au_col_letter + '1', 'AU emails')

            ca_col_letter = Helpers.get_last_col_letter(self.sheet.sheet)
            self.sheet.sheet.update_acell(ca_col_letter + '1', 'CA emails')

            gov_col_letter = Helpers.get_last_col_letter(self.sheet.sheet)
            self.sheet.sheet.update_acell(gov_col_letter + '1', 'GOV emails')

            other_col_letter = Helpers.get_last_col_letter(self.sheet.sheet)
            self.sheet.sheet.update_acell(other_col_letter + '1', 'OTHER emails')

            au_count = 0
            ca_count = 0
            gov_count = 0
            other_count = 0
            accepted_domains = ['com', 'net', 'us', 'edu', 'org']

            for idx, email in enumerate(emails):
                # get end of emails
                after_dot = email.split('.')[-1]
                # if ends in .au
                if after_dot == 'au':
                    au_count += 1
                    # put emails in appropriate rows
                    self.sheet.sheet.update_acell(au_col_letter + str(idx + 2), email)

                # if ends in .ca
                if after_dot == 'ca':
                    ca_count += 1
                    self.sheet.sheet.update_acell(ca_col_letter + str(idx + 2), email)
                # if ends in .gov
                if after_dot == 'gov':
                    # make grey
                    gov_count += 1
                    self.sheet.sheet.update_acell(gov_col_letter + str(idx + 2), email)
                # if unrecognized
                if after_dot not in accepted_domains and email != '':
                    other_count += 1
                    self.sheet.sheet.update_acell(other_col_letter + str(idx + 2), email)

            # make header "au emails"
            self.sheet.sheet.update_acell(au_col_letter + '1', str(au_count) + " " + 'AU emails')
            self.sheet.sheet.update_acell(ca_col_letter + '1', str(ca_count) + " " + 'CA emails')
            self.sheet.sheet.update_acell(gov_col_letter + '1', str(gov_count) + " " + 'GOV emails')
            self.sheet.sheet.update_acell(other_col_letter + '1', str(other_count) + " " + 'OTHER emails')
            Group('scraper-'+str(self.scrape_id), channel_layer=self.message.channel_layer).send({'text': "COMPLETE!"})

    def run(self):
        return self.wiley()

def google_sheet_main_init(search = None, spread_sheet_name = "Copy of Herpetology abstracts"):
    from new_xhelper import Xhelper

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
            wiley_gsheet = WileySheet(xhelper = xhelper, sheet = sheet)
            wiley_gsheet.run()

def google_sheet_main_menu():
    sheet_name = raw_input("whatchur Google SpreadSheet name? ")
    print("This is the email address you have to share that sheet with: ")
    print("123114053576-compute@developer.gserviceaccount.com")
    sheet_share_confirm = raw_input("Have you done that yet? (enter y or n): ").rstrip()
    while sheet_share_confirm != "y" and sheet_share_confirm != "n":
        sheet_share_confirm = raw_input("You bricked it. Have you done that yet? (enter y or n): ").rstrip()
    if sheet_share_confirm == "y":
        google_sheet_main_init(spread_sheet_name = sheet_name)
    else:
        print("well go do that then")

def run():
    google_sheet_main_menu()

if __name__ == '__main__':
    run()