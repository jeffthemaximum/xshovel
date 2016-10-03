from new_xhelper import Xhelper, Sheet, Scraper, Helpers

import os
import requests
import urllib
import pudb
import datetime

class PlosHelpers:
    @classmethod
    def find_title_from_soup(cls, soup):
        try:
            title = soup.soup.find('h1', {'id': 'artTitle'}).text.strip()
        except:
            title = ""
        return title

    @classmethod
    def find_abstract_from_soup(cls, soup):
        try:
            abstract = soup.soup.find('div', {'class': 'abstract'}).find_next('p').text.strip()
        except:
            abstract = ""
        return abstract

    @classmethod
    def find_affiliation_from_soup(cls, soup):
        try:
            a = soup.soup.find('p', {'id': 'authAffiliations-0'}).text.strip()
        except:
            a = ""
        return a

    @classmethod
    def find_art_type_from_soup(cls, soup):
        try:
            art_type = soup.soup.find('div', {'class': 'article-type'}).find_next('p').text.strip()
        except:
            art_type = ""
        return art_type

class Plos:
    def __init__(self, xhelper, sheet, search = None, search_url = None):
        self.xhelper = xhelper
        # self.scrape_id = scrape_id
        # self.message = message
        self.sheet = Sheet(self.xhelper, sheet)

        self.all_soups = self.get_all_soups()
        self.all_emails = self.get_emails()
        self.all_names = self.get_names()
        self.all_affiliations = self.init_affiliations()
        self.all_art_types = self.init_art_types()


    def get_all_soups(self):
        soups = []
        for url in self.all_urls:
            print url
            scraper = Scraper(url)
            soups.append(scraper)
        return soups

        # return [Scraper(url) for url in self.all_urls]

    def get_names(self):
        names = []
        for i, url in enumerate(self.all_urls):
            try:
                soup = self.all_soups[i].soup
                email_el = soup.find("span", {"class": "email"})
                name = email_el.parent.text.strip()
                first_name = name.split(" ")[0]

                # if first name is initial, try to get middle name
                if list(first_name)[-1] == ".":
                    if len(name.split(" ")) > 2:
                        first_name = name.split(" ")[1]
                print first_name
            except:

                first_name = ""
            names.append(first_name)
        return names


    def get_emails(self):
        emails = []
        for i, url in enumerate(self.all_urls):
            try:
                soup = self.all_soups[i].soup
                email_el = soup.find("span", {"class": "email"}).findNext("a")
                email = email_el["href"].split(":")[1]
                print email
            except:

                email = ""
            emails.append(email)
        return emails

    def init_urls(self):
        base = "http://journals.plos.org"
        urls = []
        for result in self.list_of_results_as_json:
            partial_url = result["link"].decode('unicode-escape')
            full_url = base + partial_url
            print full_url
            urls.append(full_url)
        return urls

    def init_abstracts(self):
        abstracts = []
        for idx, result in enumerate(self.list_of_results_as_json):
            try:
                abstract = " ".join(result["figure_table_caption"])
            except KeyError:
                abstract = ""

            abstracts.append(abstract)
            print abstract

        return abstracts

    def init_titles(self):
        titles = []
        for idx, result in enumerate(self.list_of_results_as_json):
            try:
                title = result["title"]
            except KeyError:
                try:
                    title = result["title_display"]
                except KeyError:
                    title = ""
            titles.append(title)
            print title

        return titles

    def init_affiliations(self):
        affiliations = []
        for soup in self.all_soups:
            affiliation = PlosHelpers.find_affiliation_from_soup(soup)
            affiliations.append(affiliation)
        return affiliations

    def init_art_types(self):
        art_types = []
        for soup in self.all_soups:
            art_type = PlosHelpers.find_art_type_from_soup(soup)
            art_types.append(art_type)
        return art_types

class PlosGsheet(Plos):
    def __init__(self, xhelper, sheet):
        self.sheet = Sheet(xhelper, sheet)
        self.url_col_num = Helpers.get_column_number(self.sheet, 'pageUrl')
        self.all_urls = Helpers.get_all_wiley_urls(self.sheet, self.url_col_num)
        self.all_urls = Helpers.get_all_column_vals_as_row(self.sheet, self.url_col_num)
        Plos.__init__(self, xhelper, sheet)
        self.all_titles = self.init_titles()
        self.all_abstracts = self.init_abstracts()

    def run_gspread(self):
        to_write = [
            ['name', self.all_names],
            ['email', self.all_emails],
            ['affiliation', self.all_affiliations],
            ['title', self.all_titles],
            ['abstract', self.all_abstracts],
            ['type', self.all_art_types]
        ]
        self.sheet.write_to_sheet(to_write)

    def init_titles(self):
        all_titles = []
        for soup in self.all_soups:
            title = PlosHelpers.find_title_from_soup(soup)
            all_titles.append(title)
        return all_titles

    def init_abstracts(self):
        all_abstracts = []
        for soup in self.all_soups:
            abstract = PlosHelpers.find_abstract_from_soup(soup)
            all_abstracts.append(abstract)
        return all_abstracts

class PlosAll(Plos):
    def __init__(self, xhelper, sheet, search, search_url):
        self.search = search
        self.search_url = search_url
        self.scraped_search_url = Scraper(url = self.search_url, kind = "plos", json = True)
        self.list_of_results_as_json = self.scraped_search_url.json['searchResults']['docs']
        self.url_col_num = 0
        self.all_urls = self.init_urls()

        Plos.__init__(self, xhelper = xhelper, sheet = sheet, search = search, search_url = search_url)

        self.abstract_col_num = 1
        
        self.title_col_num = 2
    
        self.email_col_num = 3
        
        self.name_col_num = 4

        self.all_abstracts = self.init_abstracts()
        self.all_titles = self.init_titles()

    def run(self, url_col_name = "pageUrl", title_col_name = "title", abstract_col_name = "abstract", email_col_name = "email", name_col_name = "name"):
        # write urls to Sheet

        # 1 - print pageUrl at top of col
        url_col_letter = Helpers.get_col_letter_from_number(self.url_col_num, fixer = 0)
        url_col_header_cell_str = Helpers.get_cell_string(url_col_letter, 0)

        self.sheet.sheet.update_acell(url_col_header_cell_str, url_col_name)

        # 2 - write list of urls to that col
        url_cell_list = Helpers.get_cell_list_for_plos(self.sheet.sheet, url_col_letter, len(self.all_urls))

        for i, cell in enumerate(self.all_urls):
            url_cell_list[i].value = self.all_urls[i]

        self.sheet.sheet.update_cells(url_cell_list)

        # titles
        title_col_letter = Helpers.get_col_letter_from_number(self.title_col_num, fixer = 0)
        title_col_header_cell_str = Helpers.get_cell_string(title_col_letter, 0)

        self.sheet.sheet.update_acell(title_col_header_cell_str, title_col_name)

        title_cell_list = Helpers.get_cell_list_for_plos(self.sheet.sheet, title_col_letter, len(self.all_titles))

        for i, cell in enumerate(self.all_titles):
            title_cell_list[i].value = self.all_titles[i]

        self.sheet.sheet.update_cells(title_cell_list)

        # abstracts
        abstract_col_letter = Helpers.get_col_letter_from_number(self.abstract_col_num, fixer = 0)
        abstract_col_header_cell_str = Helpers.get_cell_string(abstract_col_letter, 0)

        self.sheet.sheet.update_acell(abstract_col_header_cell_str, abstract_col_name)

        abstract_cell_list = Helpers.get_cell_list_for_plos(self.sheet.sheet, abstract_col_letter, len(self.all_abstracts))

        for i, cell in enumerate(self.all_abstracts):
            abstract_cell_list[i].value = self.all_abstracts[i]

        self.sheet.sheet.update_cells(abstract_cell_list)

        # emails
        email_col_letter = Helpers.get_col_letter_from_number(self.email_col_num, fixer = 0)
        email_col_header_cell_str = Helpers.get_cell_string(email_col_letter, 0)

        self.sheet.sheet.update_acell(email_col_header_cell_str, email_col_name)
        
        email_cell_list = Helpers.get_cell_list_for_plos(self.sheet.sheet, email_col_letter, len(self.all_emails))

        for i, cell in enumerate(self.all_emails):
            email_cell_list[i].value = self.all_emails[i]

        self.sheet.sheet.update_cells(email_cell_list)

        # names
        name_col_letter = Helpers.get_col_letter_from_number(self.name_col_num, fixer = 0)
        name_col_header_cell_str = Helpers.get_cell_string(name_col_letter, 0)

        self.sheet.sheet.update_acell(name_col_header_cell_str, name_col_name)

        name_cell_list = Helpers.get_cell_list_for_plos(self.sheet.sheet, name_col_letter, len(self.all_names))

        for i, cell in enumerate(self.all_names):
            name_cell_list[i].value = self.all_names[i]

        self.sheet.sheet.update_cells(name_cell_list)


def search_main(search = None, spread_sheet_name = "Copy of Herpetology abstracts"):
    # search = "amphibians"

    now = datetime.datetime.now()

    start_year = raw_input("What's the beginning year of yer search? ")
    start_month = raw_input("What's the beginning month of yer search? Use two digit format, such as 08. ")
    end_year = str(now.year)
    end_month = str(now.month) if len(str(now.month)) == 2 else "0" + str(now.month)
    end_day = str(now.day) if len(str(now.day)) == 2 else "0" + str(now.day)
    per_page = raw_input("How many results you want? ")
    search = raw_input("What do you want to search for? ")

    plos_sheet_name = "plos " + search

    url = "http://journals.plos.org/plosone/dynamicSearch?filterStartDate={0}-{1}-01&filterEndDate={2}-{3}-{4}&resultsPerPage={5}&q={6}&page=1"

    if " " in search:
        search = "+".join(search.split(" "))

    url = url.format(start_year, start_month, end_year, end_month, end_day, per_page, search)

    print url

    f = os.environ['XPYTHON_GSPREAD_CONFIG_FILE']
    opener = urllib.URLopener()
    myfile = opener.open(f)
    file_as_json_str = myfile.read()

    print 'making sheet'
    xhelper = Xhelper(json_file_name = file_as_json_str, spread_sheet_name = spread_sheet_name)
    worksheet = xhelper.spread_sheet.add_worksheet(title=plos_sheet_name, rows="10000", cols="20")
    print 'made sheet'

    plos = PlosAll(xhelper = xhelper, sheet = worksheet, search = search, search_url = url)
    plos.run()

def gsheet_main(spread_sheet_name):
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
            plos = PlosGsheet(xhelper = xhelper, sheet = sheet)
            plos.run_gspread()



def plos_menu():
    menu = """
    The Plos scraper can be used for one of two things:

    It can take a google spreadsheet with plos article URL's,
    And then scrape those articles to find all the info in them.

    Or, you can just enter a search term here, and then the Scraper
    will go search PLOS, find articles, and display the info from them in
    a google sheet.

    Which do you want to do?

    1: Give it a google sheet with PLOS article URL's 
    2: Search Plos
"""
    print menu
    return int(raw_input("Enter your choice (1 or 2): "))

if __name__ == '__main__':

    sheet_name = raw_input("whatchur Google SpreadSheet name? ")
    print("This is the email address you have to share that sheet with: ")
    print("123114053576-compute@developer.gserviceaccount.com")
    sheet_share_confirm = raw_input("Have you done that yet? (enter y or n): ").rstrip()


    while sheet_share_confirm != "y" and sheet_share_confirm != "n":
        sheet_share_confirm = raw_input("You bricked it. Have you done that yet? (enter y or n): ").rstrip()
    if sheet_share_confirm == "y":

        choice = plos_menu()

        while (choice != 1 and choice != 2):
            choice = plos_menu()

        if choice == 1:
            gsheet_main(spread_sheet_name = sheet_name)
        else:
            search_main(spread_sheet_name = sheet_name)
    else:
        print("well go do that then")