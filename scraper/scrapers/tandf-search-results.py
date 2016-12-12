import os
import urllib
import sys

if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scrapers.new_xhelper import Xhelper, Helpers, Sheet, Scraper


MAX_COUNT = 3
BASE_URL = "http://www.tandfonline.com"

class TandfSearchResultsHelpers:

    @classmethod
    def find_search_result_urls(cls, url):
        count = 0
        all_found_urls = []
        all_soups = []
        while count < MAX_COUNT:
            print url
            scraped = Scraper(url)
            link = scraped.soup.find('b', {'class': 'selected'}).find_next('li').find('a')['href']
            next_url = BASE_URL + link
            all_found_urls.append(next_url)
            all_soups.append(scraped)
            url = next_url
            count += 1
        return {'soups': all_soups, 'found_urls': all_found_urls}

    @classmethod
    def find_article_url(cls, soup):
        all_article_els = soup.find_all('article', {'class': 'searchResultItem'})
        all_article_links = []
        for el in all_article_els:
            article_link = el.find('a')['href']
            all_article_links.append(BASE_URL + article_link)
        return all_article_links


class TandfSearchResults:
    def __init__(self, xhelper, sheet):
        self.xhelper = xhelper
        self.sheet = Sheet(self.xhelper, sheet)
        
        # soups
        self.all_soups = []

        # search result URLs
        self.all_original_search_results_urls_col_num = Helpers.get_column_number(self.sheet, 'pageUrl')
        self.all_original_search_results_urls = Helpers.get_all_column_vals_as_row(self.sheet, self.all_original_search_results_urls_col_num)
        self.all_found_search_result_urls = self.find_all_found_search_result_urls()

        # article link URLs
        self.all_article_urls = self.find_article_urls()

    def find_article_urls(self):
        all_article_urls = []
        for soup in self.all_soups:
            article_urls = TandfSearchResultsHelpers.find_article_url(soup.soup)
            all_article_urls.extend(article_urls)
        return all_article_urls

    def find_all_found_search_result_urls(self):
        all_found_search_result_urls = []
        for url in self.all_original_search_results_urls:
            found_search_result_urls = TandfSearchResultsHelpers.find_search_result_urls(url)
            all_found_search_result_urls.extend(found_search_result_urls['found_urls'])
            self.all_soups.extend(found_search_result_urls['soups'])
        return all_found_search_result_urls

    def run(self):
        to_write = [
            ['found_search_urls', self.all_found_search_result_urls],
            ['article_urls', self.all_article_urls]
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
            tandf_search_results = TandfSearchResults(xhelper = xhelper, sheet = sheet)
            tandf_search_results.run()

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