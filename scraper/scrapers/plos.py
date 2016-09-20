from new_xhelper import Xhelper, Sheet, Scraper, Helpers

import os
import requests
import urllib
import pudb

class Plos:
    def __init__(self, xhelper, sheet, search, search_url):
        self.xhelper = xhelper
        # self.scrape_id = scrape_id
        # self.message = message
        self.sheet = Sheet(self.xhelper, sheet)

        self.search = search
        self.search_url = search_url
        self.scraped_search_url = Scraper(url = self.search_url, kind = "plos", json = True)
        self.list_of_results_as_json = self.scraped_search_url.json['searchResults']['docs']

        self.url_col_num = 0
        self.all_urls = self.init_urls()

        self.abstract_col_num = 1
        self.all_abstracts = self.init_abstracts()

        self.title_col_num = 2
        self.all_titles = self.init_titles()

        self.all_soups = self.get_all_soups()

        self.email_col_num = 3
        self.all_emails = self.get_emails()

        self.name_col_num = 4
        self.all_names = self.get_names()

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

def main(search = None, spread_sheet_name = None):
    search = "amphibians"
    spread_sheet_name = "Copy of Herpetology abstracts"
    plos_sheet_name = "plos " + search

    url_1 = "http://journals.plos.org/plosone/dynamicSearch?filterStartDate=2015-01-01&filterEndDate=2016-08-10&resultsPerPage=100&q="
    url_2 = "&page=1"

    if " " in search:
        search = "+".join(search.split(" "))

    url = url_1 + search + url_2

    print url

    f = os.environ['XPYTHON_GSPREAD_CONFIG_FILE']
    opener = urllib.URLopener()
    myfile = opener.open(f)
    file_as_json_str = myfile.read()

    print 'making sheet'
    xhelper = Xhelper(json_file_name = file_as_json_str, spread_sheet_name = spread_sheet_name)
    worksheet = xhelper.spread_sheet.add_worksheet(title=plos_sheet_name, rows="10000", cols="20")
    print 'made sheet'

    plos = Plos(xhelper = xhelper, sheet = worksheet, search = search, search_url = url)
    plos.run()

if __name__ == '__main__':
    main()