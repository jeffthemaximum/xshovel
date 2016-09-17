from celery.decorators import task
from celery.utils.log import get_task_logger
import requests
import os
import json
import pudb

from scraper.scrapers.xhelper import main

logger = get_task_logger(__name__)


@task(name="scraper.scrape_and_update_sheet_task")
def scrape_and_update_sheet_task(sheet_name, sheet_id):
    logger.info("scraping sheet")
    scraped = main(sheet_name)
    print "SCRAPED" * 100
    print "Jeff" + str(scraped)
    if scraped is True:
        status = 'success'
        # call rails app and update with status: 'success'
    else:
        # call rails app and update with status: 'failed'
        status = 'failed'
    callback(sheet_name, sheet_id, status)


def callback(sheet_name, sheet_id, status):
    url = os.environ['XCUBE_URL']
    data = {'sheet_name': sheet_name, 'sheet_id': sheet_id, 'status': status}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.get(url, data=json.dumps(data), headers=headers)
    print 'callback!!!!' * 100
    return True
