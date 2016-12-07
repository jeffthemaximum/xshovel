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
    from new_xhelper import Scraper

class TandfHelpers:
    @classmethod
    def get_article_type(cls, soup):
        try:
            return soup.find('div', {'class': 'toc-heading'}).text.strip()
        except:
            return ""

    @classmethod
    def get_author_name(cls, soup):
        try:
            author_el = cls.get_author_el(soup)
            return cls.get_author_name_from_author_el(author_el)
        except:
            return ""

    @classmethod
    def get_author_el(cls, soup):
        return soup.find('span', {'class': 'corresponding'}).find('a', {'class': 'entryAuthor'})

    @classmethod
    def get_author_name_from_author_el(cls, el):
        all_text = el.text
        other_text = el.find('span', {'class': 'overlay'}).text.strip()
        return all_text.replace(other_text, '').strip()


    @classmethod
    def get_email(cls, soup):
        try:
            author_el = cls.get_author_el(soup)
            return cls.get_email_from_author_el(author_el)
        except:
            return ""

    @classmethod
    def get_email_from_author_el(cls, el):
        return el.find('span', {'class': 'corr-email'}).text.strip()

    @classmethod
    def get_title(cls, soup):
        try:
            return soup.find('div', {'class': 'toc-heading'}).find_next('h1').text.strip()
        except:
            return ""

    @classmethod
    def get_abstract(cls, soup):
        try:
            return soup.find('div', {'class': 'abstractSection'}).text.strip()
        except:
            return ""

    @classmethod
    def get_journal(cls, soup):
        try:
            return soup.find('div', {'class': 'journal'}).find_next('div', {'class': 'info'}).find('h1').text.strip()
        except:
            return ""

    @classmethod
    def get_first_name(cls, soup):
        try:
            return cls.get_author_name(soup).split(" ")[0]
        except:
            return ""


class TandfGsheet:
    def __init__(self, xhelper, sheet):

        from new_xhelper import Sheet, Scraper, Helpers

        self.xhelper = xhelper
        self.sheet = Sheet(self.xhelper, sheet)

        self.url_col_num = Helpers.get_column_number(self.sheet, 'pageUrl')
        self.all_urls = Helpers.get_all_wiley_urls(self.sheet, self.url_col_num)
        self.all_urls = Helpers.get_all_column_vals_as_row(self.sheet, self.url_col_num)
        print self.all_urls

        self.all_soups = self.get_all_soups()

        self.all_article_types = self.get_all_article_types()

        self.all_author_names = self.get_all_author_names()

        self.all_author_emails = self.get_all_emails()

        self.all_article_titles = self.get_all_article_titles()

        self.all_abstracts = self.get_all_abstracts()

        self.all_journals = self.get_all_journals()

        self.foo = 5

    def get_all_soups(self):
        all_soups = []
        for url in self.all_urls:
            print url
            scraped = Scraper(url)
            all_soups.append(scraped)
        return all_soups

    def get_all_article_types(self):
        all_types = []
        for soup in self.all_soups:
            a_type = TandfHelpers.get_article_type(soup.soup)
            all_types.append(a_type)
        return all_types

    def get_all_author_names(self):
        all_names = []
        for soup in self.all_soups:
            author_name = TandfHelpers.get_first_name(soup.soup)
            all_names.append(author_name)
        return all_names

    def get_all_emails(self):
        all_emails = []
        for soup in self.all_soups:
            email = TandfHelpers.get_email(soup.soup)
            all_emails.append(email)
        return all_emails

    def get_all_article_titles(self):
        all_titles = []
        for soup in self.all_soups:
            title = TandfHelpers.get_title(soup.soup)
            all_titles.append(title)
        return all_titles

    def get_all_abstracts(self):
        all_abstracts = []
        for soup in self.all_soups:
            abstract = TandfHelpers.get_abstract(soup.soup)
            all_abstracts.append(abstract)
        return all_abstracts

    def get_all_journals(self):
        all_journals = []
        for soup in self.all_soups:
            journal = TandfHelpers.get_journal(soup.soup)
            all_journals.append(journal)
        return all_journals

    def run(self):
        to_write = [
            ['type', self.all_article_types],
            ['name', self.all_author_names],
            ['email', self.all_author_emails],
            ['title', self.all_article_titles],
            ['abstract', self.all_abstracts],
            ['journal', self.all_journals]
        ]
        self.sheet.write_to_sheet(to_write)



BASE_URL = 'http://www.tandfonline.com'

def base_url_plus_stub(stub):
    return BASE_URL + stub

def get_datetime_on_ol_page(li):
    date_str = li.find('div', {'class': 'publication-meta'}).find_all('span')[1].text.split(':')[1].strip()
    format = '%d %b %Y'
    return datetime.strptime(date_str, format)

def get_author_name(el):
    try:
        all_text = el.text
        other_text = el.find('span', {'class': 'overlay'}).text.strip()
        return all_text.replace(other_text, '').strip()
    except:
        ""

def get_author_email(el):
    try:
        return el.find('span', {'class': 'corr-email'}).text.strip()
    except:
        ""

def build_search_link(short_link, idx):
    add_on = "&pageSize=20&subjectTitle=&startPage=" + idx
    return short_link + add_on

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
            tandf_gsheet = TandfGsheet(xhelper = xhelper, sheet = sheet)
            tandf_gsheet.run()


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

def main(range_start = None, range_stop = None, topic_start = None, topic_stop = None):
    # get homepage
    res = requests.get(BASE_URL)
    soup = bs4.BeautifulSoup(res.text)

    # get all links on homepage
    topic_divs = soup.find('div', {'class': 'topicalIndex'}).find_all('div', {'class': 'unit'})

    topic_links = []
    for div in topic_divs:
        lis = div.find_all('li')
        for li in lis:
            multi_hit = []
            for i in range(0, 3):
                # get link
                link_stub = base_url_plus_stub(li.find('a')['href']).split('?')[0]
                # get topic
                topic = li.text.strip() 

                # get num results
                # 1 - get first page
                res = requests.get(link_stub)
                topic_soup = bs4.BeautifulSoup(res.text)

                # 2 - find # of last page
                last_page_num = topic_soup.find('a', {'class': 'lastPage'}).text.strip()

                multi_hit.append((topic, link_stub, int(last_page_num)))

                print link_stub
            
            correct_num_list = min(multi_hit, key=itemgetter(2))
            topic_links.append(correct_num_list)

    # just print out stats about how many pages you found
    total = 0
    for tl in topic_links:
        total += tl[2]
        print tl

    print total

    # instantiate topic_start, topic_stop
    if topic_start and topic_start:
        topic_stop = topic_stop + 1
        topic_links = topic_links[topic_start:topic_stop]
    else:
        if topic_start:
            topic_links = topic_links[topic_start:]

        if topic_stop:
            topic_stop = topic_stop + 1
            topic_links = topic_links[:topic_stop]

    # go to topic link pages and
    for j, topic_link in enumerate(topic_links):

        # instantiate range stop
        if j == len(topic_links) - 1:
            if range_stop:
                stop = range_stop
            else:
                stop = range_stop
        else:
            stop = topic_link[2]

        # instantiate range_start
        if j == 0:
            if range_start:
                start = range_start
            else:
                start = range_start
        else:
            start = 0

        # for each search page in the topic
        for idx in range(start, stop):

            p_idx = str(idx) + " "
            print "p_idx " + p_idx * 10
            print "J " + str(j)

            link = topic_link[1] + '?target=topic&pageSize=20&subjectTitle=&startPage=' + str(idx)

            res = requests.get(link)
            topic_soup = bs4.BeautifulSoup(res.text)

            # get links off first page
            ol = topic_soup.find('ol', {'class': 'search-results'})
            lis = ol.find_all('li')
            for li in lis:
                try:
                    article_title = li.find('article').attrs['data-title']
                    article_link = base_url_plus_stub(li.find('a', {'class': 'ref'})['href'])
                    article_date = get_datetime_on_ol_page(li)

                    journal_name = li.find('div', {'class': 'publication-meta'}).find_all('span')[0].text.strip()
                    journal_link = base_url_plus_stub(li.find('div', {'class': 'publication-meta'}).find_all('span')[0].find('a')['href'])

                    # go to article link
                    res = requests.get(article_link)
                    article_soup = bs4.BeautifulSoup(res.text)
                    article_type = article_soup.find('div', {'class': 'toc-heading'}).text.strip()

                    author_el = article_soup.find('span', {'class': 'corresponding'}).find('a', {'class': 'entryAuthor'})
                    author_name = get_author_name(author_el)
                    
                    author_email = get_author_email(author_el)

                    print (article_title, article_link, article_date, journal_name, journal_link, article_type, author_name, author_email)

                    # save journal
                    journal, created = Journal.objects.get_or_create(name = journal_name)
                    if created:
                        journal.link = journal_link
                        journal.save()

                    # save author 
                    if author_email != "":
                        author, created = Author.objects.get_or_create(email = author_email)
                        if created:
                            author.name = author_name
                            author.save()

                        # save article 
                        try:
                            article = Article.objects.get(link = article_link, title = article_title)
                        except Article.DoesNotExist:
                            article = Article.objects.create(
                                link = article_link, 
                                title = article_title,
                                date = article_date.strftime('%Y-%m-%d'),
                                author = author,
                                journal = journal
                            )
                        
                except:
                    site = 'tandf'
                    brick, created = Brick.objects.get_or_create(url = article_link, site = site)
                    print "BRICKED " * 10
                    print article_link
                    print str(Brick.objects.count()) + " bricks"

def ask_for_range_start_range_stop_topic_start_topic_stop():
    topic_help = '''
    (u'Area Studies', 'http://www.tandfonline.com/topic/4251', 6976)
    (u'Arts', 'http://www.tandfonline.com/topic/4250', 4080)
    (u'Behavioral Sciences', 'http://www.tandfonline.com/topic/4252', 12470)
    (u'Bioscience', 'http://www.tandfonline.com/topic/4253', 15117)
    (u'Built Environment', 'http://www.tandfonline.com/topic/4254', 3320)
    (u'Communication Studies', 'http://www.tandfonline.com/topic/4256', 2171)
    (u'Computer Science', 'http://www.tandfonline.com/topic/4255', 3842)
    (u'Development Studies', 'http://www.tandfonline.com/topic/4257', 3412)
    (u'Earth Sciences', 'http://www.tandfonline.com/topic/4258', 6429)
    (u'Economics, Finance, Business & Industry', 'http://www.tandfonline.com/topic/4259', 13503)
    (u'Education', 'http://www.tandfonline.com/topic/4261', 15388)
    (u'Engineering & Technology', 'http://www.tandfonline.com/topic/4260', 20060)
    (u'Environment & Agriculture', 'http://www.tandfonline.com/topic/4248', 14561)
    (u'Environment and Sustainability', 'http://www.tandfonline.com/topic/4262', 7045)
    (u'Food Science & Technology', 'http://www.tandfonline.com/topic/4263', 2749)
    (u'Geography', 'http://www.tandfonline.com/topic/4264', 7626)
    (u'Health and Social Care', 'http://www.tandfonline.com/topic/4266', 7588)
    (u'Humanities', 'http://www.tandfonline.com/topic/4267', 15590)
    (u'Information Science', 'http://www.tandfonline.com/topic/4268', 2158)
    (u'Language & Literature', 'http://www.tandfonline.com/topic/4269', 5395)
    (u'Law', 'http://www.tandfonline.com/topic/4270', 1692)
    (u'Mathematics & Statistics', 'http://www.tandfonline.com/topic/4271', 9059)
    (u'Medicine, Dentistry, Nursing & Allied Health', 'http://www.tandfonline.com/topic/4272', 24867)
    (u'Museum and Heritage Studies', 'http://www.tandfonline.com/topic/4249', 1263)
    (u'Physical Sciences', 'http://www.tandfonline.com/topic/4273', 19203)
    (u'Politics & International Relations', 'http://www.tandfonline.com/topic/4274', 10937)
    (u'Social Sciences', 'http://www.tandfonline.com/topic/4278', 11016)
    (u'Sports and Leisure', 'http://www.tandfonline.com/topic/4277', 3158)
    (u'Tourism, Hospitality and Events', 'http://www.tandfonline.com/topic/4279', 690)
    (u'Urban Studies', 'http://www.tandfonline.com/topic/4280', 1911)
    253276
    '''
    print topic_help
    topic_start = raw_input("enter the number of the topic you want to start scraping at (remember, it's 0-indexed): ")
    topic_stop = raw_input("enter the number of the last  topic you want to complete scraping: ")
    range_start = raw_input("At what point in the range do you want to start? ")
    range_stop = raw_input("What is the last range number in that topic you want to finish at? ")
    return {
        'topic_start': int(topic_start),
        'topic_stop': int(topic_stop),
        'range_start': int(range_start),
        'range_stop': int(range_stop)
    }

def ask_if_part_or_whole():
    ans = raw_input("Do you want to run part of the scraper? Enter y or n: ")
    if ans == 'y':
        return True
    elif ans == 'n':
        return False
    else:
        return ask_for_range_start_range_stop_topic_start_topic_stop()

def start_menu():
    menu = """
Welcome to the Taylor and Francis Scraper!
With this scraper, you can either scrape all of T and F 
or, you can just scrape a Google Sheet thats filled with T and F article URLS.
Which would you like to do?
1 - Scrape all of T and F (warning, this takes about 100 days if you run just one, single-threaded instance)
2 - Scrape a Google Sheet thats filled with T and F article URLS.
"""
    print menu
    choice = raw_input('Enter your choice: ')
    if choice == '1' or choice == '2':
        return int(choice)
    else:
        start_menu()

def run():
    start_menu_choice = start_menu()
    if start_menu_choice == 2:
        google_sheet_main_menu()
    elif start_menu_choice == 1:
        if ask_if_part_or_whole():
            user_settings = ask_for_range_start_range_stop_topic_start_topic_stop()
            main(range_start = user_settings['range_start'], range_stop = user_settings['range_stop'], topic_start = user_settings['topic_start'], topic_stop = user_settings['topic_stop'])
        else:
            main()
    else:
        print "something went wrong"

if __name__ == '__main__':
    run()


# (u'Area Studies', 'http://www.tandfonline.com/topic/4251', 6976)
# (u'Arts', 'http://www.tandfonline.com/topic/4250', 4080)
# (u'Behavioral Sciences', 'http://www.tandfonline.com/topic/4252', 12470)
# (u'Bioscience', 'http://www.tandfonline.com/topic/4253', 15117)
# (u'Built Environment', 'http://www.tandfonline.com/topic/4254', 3320)
# (u'Communication Studies', 'http://www.tandfonline.com/topic/4256', 2171)
# (u'Computer Science', 'http://www.tandfonline.com/topic/4255', 3842)
# (u'Development Studies', 'http://www.tandfonline.com/topic/4257', 3412)
# (u'Earth Sciences', 'http://www.tandfonline.com/topic/4258', 6429)
# (u'Economics, Finance, Business & Industry', 'http://www.tandfonline.com/topic/4259', 13503)
# (u'Education', 'http://www.tandfonline.com/topic/4261', 15388)
# (u'Engineering & Technology', 'http://www.tandfonline.com/topic/4260', 20060)
# (u'Environment & Agriculture', 'http://www.tandfonline.com/topic/4248', 14561)
# (u'Environment and Sustainability', 'http://www.tandfonline.com/topic/4262', 7045)
# (u'Food Science & Technology', 'http://www.tandfonline.com/topic/4263', 2749)
# (u'Geography', 'http://www.tandfonline.com/topic/4264', 7626)
# (u'Health and Social Care', 'http://www.tandfonline.com/topic/4266', 7588)
# (u'Humanities', 'http://www.tandfonline.com/topic/4267', 15590)
# (u'Information Science', 'http://www.tandfonline.com/topic/4268', 2158)
# (u'Language & Literature', 'http://www.tandfonline.com/topic/4269', 5395)
# (u'Law', 'http://www.tandfonline.com/topic/4270', 1692)
# (u'Mathematics & Statistics', 'http://www.tandfonline.com/topic/4271', 9059)
# (u'Medicine, Dentistry, Nursing & Allied Health', 'http://www.tandfonline.com/topic/4272', 24867)
# (u'Museum and Heritage Studies', 'http://www.tandfonline.com/topic/4249', 1263)
# (u'Physical Sciences', 'http://www.tandfonline.com/topic/4273', 19203)
# (u'Politics & International Relations', 'http://www.tandfonline.com/topic/4274', 10937)
# (u'Social Sciences', 'http://www.tandfonline.com/topic/4278', 11016)
# (u'Sports and Leisure', 'http://www.tandfonline.com/topic/4277', 3158)
# (u'Tourism, Hospitality and Events', 'http://www.tandfonline.com/topic/4279', 690)
# (u'Urban Studies', 'http://www.tandfonline.com/topic/4280', 1911)
# 253276

    


        
        
