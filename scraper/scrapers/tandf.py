import requests
import bs4
import pudb

from datetime import datetime
from operator import itemgetter

from scraper.models import Journal, Author, Article

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

for tl in topic_links:
    print tl

# go to topic link pages and
for topic_link in topic_links:
    
    for idx in range(0, topic_link[2]):

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
                p_idx = str(idx) + " "
                print p_idx * 10

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
                print "BRICKED " * 10
                print article_link



    


        
        

