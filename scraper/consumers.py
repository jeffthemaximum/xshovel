import re
import json
import logging
from channels import Group
from scraper.scrapers.new_xhelper import main

log = logging.getLogger(__name__)

def scrape_wiley_by_sheet_name(message):
    sheet_name = message.content.get('sheet_name')
    scrape_id = message.content.get('scrape_id')
    scraped = main(sheet_name, scrape_id, message)