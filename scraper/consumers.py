import re
import json
import logging
from channels import Group
from scraper.scrapers.xhelper import main

log = logging.getLogger(__name__)

def scrape_wiley_by_sheet_name(message):
    sheet_name = message.content.get('sheet_name')
    scraped = main(sheet_name)