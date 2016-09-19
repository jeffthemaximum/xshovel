from new_xhelper import Xhelper

import os
import requests
import urllib
import pudb

def main(search = None, spread_sheet_name = None):
    search = "amphibians"
    spread_sheet_name = "Copy of Herpetology abstracts"
    plos_sheet_name = "plos " + search

    url_1 = "http://journals.plos.org/plosone/dynamicSearch?filterStartDate=2015-01-01&filterEndDate=2016-08-10&resultsPerPage=6000&q="
    url_2 = "&page=1"

    if " " in search:
        search = "+".join(search.split(" "))

    url = url_1 + search + url_2

    print url

    f = os.environ['XPYTHON_GSPREAD_CONFIG_FILE']
    opener = urllib.URLopener()
    myfile = opener.open(f)
    file_as_json_str = myfile.read()
    pu.db
    xhelper = Xhelper(json_file_name = file_as_json_str, spread_sheet_name = spread_sheet_name)

    worksheet = xhelper.spread_sheet.add_worksheet(title=plos_sheet_name, rows="10000", cols="20")

if __name__ == '__main__':
    main()