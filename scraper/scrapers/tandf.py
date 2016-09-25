import requests
import bs4

BASE_URL = 'http://www.tandfonline.com/'

def base_url_plus_stub(stub):
    return BASE_URL + stub

# get homepage
res = requests.get(BASE_URL)
soup = bs4.BeautifulSoup(res.text)

# get all links on homepage
topic_divs = soup.find('div', {'class': 'topicalIndex'}).find_all('div', {'class': 'unit'})

topic_link_stubs = []
for div in topic_divs:
    lis = div.find_all('li')
    for li in lis:
        link_stub = li.find('a')['href']
        topic_link_stubs.append(link_stub)

topic_links = [base_url_plus_stub(stub) for stub in topic_link_stubs]
print topic_links