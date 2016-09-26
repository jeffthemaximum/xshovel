# -*- coding: utf-8 -*-
import json
import gspread
import requests
import bs4
import pudb
import cgi
import os
import urllib
from oauth2client.service_account import ServiceAccountCredentials
from channels import Group

scrape_id = None
message = None

class Scraper:
    def __init__(self, url, kind = None, json = False):
        self.url = url
        self.kind = kind
        if json is True:
            self.json = self.get_json(self.url)
        else:
            self.soup = self.cook_soup(self.url)
        
    def get_json(self, link):
        if self.kind == "plos":
            cookies = {
                '__gads': 'ID=184c418340fce1da:T=1471832486:S=ALNI_Mafy12txJwM8Ammx0YcAeaMtqiwOQ',
                'JSESSIONID': 'A6B41E4126BB2EFE4837336FA088C3A3',
                '_gat_UA-76325259-3': '1',
                '_gat_journalsMaster': '1',
                '_gat_master': '1',
                '_ga': 'GA1.3.1853032522.1471832485',
                'plos-device-detected': 'desktop',
            }

            headers = {
                'Pragma': 'no-cache',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'en-US,en;q=0.8',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.89 Safari/537.36',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Referer': 'http://journals.plos.org/plosone/search?filterStartDate=2015-01-01&filterEndDate=2016-08-10&resultsPerPage=6000&q=amphibian&page=1',
                'X-Requested-With': 'XMLHttpRequest',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
            }

        response = requests.get(self.url, headers=headers, cookies=cookies)
        response = json.loads(response.text)
        return response
        

    def cook_soup(self, link):
        """
        takes a link as a string
        returns a bs soup object
        """

        if self.kind == 'scidi':
            cookies = {
                'EUID': '88675d40-7e7a-11e6-9d38-00000aab0f27',
                'sd_scs': '8875a044-7e7a-11e6-9d38-00000aab0f27',
                'sid': '14e8aaf7-e962-4f64-9891-68c61458e0bc',
                'optimizelyEndUserId': 'oeu1474297543594r0.4892093811861049',
                'AMCV_4D6368F454EC41940A4C98A6%40AdobeOrg': '793872103%7CMCIDTS%7C17064%7CMCMID%7C87522486594869997002263906783116549148%7CMCAAMLH-1474902344%7C7%7CMCAAMB-1474902344%7CNRX38WO0n5BH8Th-nqAG_A%7CMCAID%7CNONE',
                '__gads': 'ID=c224b0a47aed5ddb:T=1474297545:S=ALNI_MYEPpmrSGEgr4KbFcO21T-H3YxKWQ',
                'USER_STATE_COOKIE': '346fa8c434beaa188373c1181c0ae9a6f9ea30ce9036ed5abadf1cb3e580fb2d',
                'CARS_COOKIE': '6b8b76378462b78a5aec22ed3c768082499c572e082b9dbc8693fcc96bf3c01cca64374c56e6d68f8483e11b4b6f1f8e7f9d137ac8264f90',
                'TARGET_URL': 'fcf74dd786744d87fbaaaf8652a764ab4a79b0d3ed681139e910692376063105cb1468c63e712961e8908ef471ab6177d378e78873d526a2',
                'fingerPrintToken': '14239b7afb1d7eb851e5ae9aeb6b5c9c',
                '__cp': '1474299720557',
                'optimizelySegments': '%7B%22204658328%22%3A%22false%22%2C%22204728159%22%3A%22none%22%2C%22204736122%22%3A%22direct%22%2C%22204775011%22%3A%22gc%22%7D',
                's_pers': '%20v8%3D1474299720762%7C1568907720762%3B%20v8_s%3DFirst%2520Visit%7C1474301520762%3B%20c19%3Dsd%253Aproduct%253Ajournal%253Aarticle%7C1474301520768%3B%20v68%3D1474299720280%7C1474301520778%3B',
                's_cc': 'true',
                'optimizelyBuckets': '%7B%7D',
                'MIAMISESSION': '88607962-7e7a-11e6-9d38-00000aab0f27:3651752521',
                'DEFAULT_SESSION_SUBJECT': '',
                's_sess': '%20v31%3D1474297543729%3B%20s_cpc%3D0%3B%20e41%3D1%3B%20s_ppvl%3Dsd%25253Aproduct%25253Ajournal%25253Aarticle%252C45%252C45%252C826%252C458%252C826%252C1440%252C900%252C2%252CL%3B%20s_ppv%3Dsd%25253Aproduct%25253Ajournal%25253Aarticle%252C45%252C45%252C826%252C458%252C826%252C1440%252C900%252C2%252CL%3B',
            }

            headers = {
                'Pragma': 'no-cache',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'en-US,en;q=0.8',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.89 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            }
            try:
                response = requests.get(self.url, headers=headers, cookies=cookies, timeout=1)
                return bs4.BeautifulSoup(response.text)
            except requests.exceptions.ReadTimeout:
                print "failed, retrying"
                return self.cook_soup(link)
            except requests.exceptions.MissingSchema:
                return ''

        else:
            try:
                response = requests.get(self.url, timeout=1)
                return bs4.BeautifulSoup(response.text)
            except requests.exceptions.ReadTimeout:
                print "failed, retrying"
                return self.cook_soup(link)
            except requests.exceptions.MissingSchema:
                return ''


class Helpers:

    @classmethod
    def get_cell_string(cls, col_letter, idx, offset=0):
        '''
        takes a col_letter like 'B'
        an idx in a list, like 5
        and an option offset like 1, which corresponds to the header of a sheet
        and returns a string like 'B7'
        7 because the list is zero indexed
        and the sheet is 1-indexed
        '''
        row = idx + offset + 1
        return col_letter + str(row)

    @classmethod
    def get_all_column_vals_as_row(cls, sheet, col_num):
        # get just elements at col_num index position
        col_as_list = [el[col_num] for el in sheet.all_vals]
        col_as_list.pop(0)
        return col_as_list

    @classmethod
    def get_column_number(cls, sheet, column_keyword):
        '''
        takes a sheet object
        and a column keyword as string, such as 'email'
        and returns the column number who's column title contains that string
        else none if no column contains that string
        '''
        column_keyword = column_keyword.lower()
        first_row_as_list = sheet.all_vals[0]
        row_lowered = [cell.lower() for cell in first_row_as_list]
        return row_lowered.index(column_keyword) if column_keyword in row_lowered else None

    @classmethod
    def get_last_col_with_text(cls, sheet):
        '''
        takes a sheet
        and returns the last column number
        that contains text
        '''
        counter = 0
        total_cols = sheet.col_count
        top_row = sheet.row_values(1)
        for i, col_val in enumerate(top_row):
            if len(col_val) != 0:
                counter = i
        return counter

    @classmethod
    def get_col_letter_from_number(cls, col_num, fixer = 1):
        '''
        takes a number, like 3
        and returns the column letter
        like D
        assumes zero indexed number
        '''
        return chr(ord('A') + col_num + fixer)

    @classmethod
    def build_range_string(cls, col_letter, num_rows):
        '''
        takes a letter, like 'A'
        and a number, like '15'
        and build a range string
        like 'A2:A17'
        assumes u want to start at 2nd row
        '''
        start = col_letter + str(2)
        end = col_letter + str(2 + num_rows)
        return (start + ':' + end)

    @classmethod
    def and_jr_check(cls, name_string):
        '''
        takes a string, like 'jr', 'jr.', or 'maxim', or 'and'
        returns true if it's 'maxim'
        false if any form of 'jr' or 'and'
        '''
        if name_string.lower() == 'jr':
            return False
        elif name_string.lower() == 'jr.':
            return False
        elif name_string.lower() == 'and':
            return False
        else:
            return True

    @classmethod
    def get_last_col_letter(cls, sheet):
        last_col_num = Helpers.get_last_col_with_text(sheet)
        last_col_letter = Helpers.get_col_letter_from_number(last_col_num)
        return last_col_letter

    @classmethod
    def get_cell_list(cls, sheet, list_of_strs):
        last_col_letter = Helpers.get_last_col_letter(sheet)
        num_rows = len(list_of_strs)
        range_string = Helpers.build_range_string(last_col_letter, num_rows)
        cell_list = sheet.range(range_string)
        return cell_list

    @classmethod
    def get_cell_list_for_plos(cls, sheet, col_letter, len_of_list):
        range_string = Helpers.build_range_string(col_letter, len_of_list)
        cell_list = sheet.range(range_string)
        return cell_list

    @classmethod
    def get_all_wiley_urls(cls, sheet, url_col_num):
        urls = Helpers.get_all_column_vals_as_row(sheet, url_col_num)
        urls = [Helpers.convert_url(url) for url in urls]
        return urls

    @classmethod
    def convert_url(cls, url):
        if '/wol1/' not in url and 'wiley.com' in url:
            foo = url.split('.com')
            bar = foo[0] + '.com/wol1' + foo[1]
            return bar
        else:
            return url

class Xhelper:
    def __init__(self, json_file_name, spread_sheet_name):
        self.json_file_name = json_file_name
        self.spread_sheet_name = spread_sheet_name
        self.errors = []
        self.gc = self.authorize()
        self.spread_sheet = self.open_spread_sheet()
        self.worksheets_list = self.get_all_worksheet_names()
        print "done xhelper init"

    def get_all_worksheet_names(self):
        return self.spread_sheet.worksheets()

    def open_spread_sheet(self):
        return self.gc.open(self.spread_sheet_name)

    def authorize(self):
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(self.json_file_name), scope)
        return gspread.authorize(credentials)


class Sheet:
    def __init__(self, xhelper, sheet):
        self.xhelper = xhelper
        self.sheet = sheet
        self.all_vals = sheet.get_all_values()


class Wiley:
    def __init__(self, xhelper, sheet, scrape_id, message):
        self.xhelper = xhelper
        self.scrape_id = scrape_id
        self.message = message
        print 'getting sheet'
        Group('scraper-'+str(self.scrape_id), channel_layer=self.message.channel_layer).send({'text': 'getting sheet'})
        self.sheet = Sheet(self.xhelper, sheet)
        print 'got sheet'
        Group('scraper-'+str(self.scrape_id), channel_layer=self.message.channel_layer).send({'text': 'got sheet'})
        # self.email_col_num = Helpers.get_column_number(self.sheet, 'email')
        self.url_col_num = Helpers.get_column_number(self.sheet, 'pageUrl')
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



def main(sheet_name, scrape_id, message):
    try:
        scrape_id = scrape_id
        message = message
        f = os.environ['XPYTHON_GSPREAD_CONFIG_FILE']
        opener = urllib.URLopener()
        myfile = opener.open(f)
        file_as_json_str = myfile.read()
        xhelper = Xhelper(json_file_name = file_as_json_str, spread_sheet_name = sheet_name)
        for sheet in xhelper.worksheets_list:
            if 'wiley' in sheet.title.lower():
                wiley = Wiley(xhelper = xhelper, sheet = sheet, scrape_id = scrape_id, message = message)
                return wiley.run()
    except:
        print 'FALSE ' * 100
        Group('scraper-'+str(scrape_id), channel_layer=message.channel_layer).send({'text': "FAILED :("})
        return False

if __name__ == '__main__':
    main()