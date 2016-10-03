### Scrapers

Remote machine is hosted at: `experiment@develubber.com`.

The strategy is:
 - 1. Find an index of journal URLs (Wiley, Tnf, Sciencedirect... etc)
 - 2. Run scrapers
 - 3. Clean emails for international and dupes

Guides:
- [How to source leads](https://github.com/experiment/xshovel/wiki/How-to-source-leads)
- [Science Direct](https://github.com/experiment/xshovel/wiki/ScienceDirect-Scraper)


This repo currently contains python scripts for filtering a list of existing emails (emails.py), gathering abstracts and emails from PLOS (plos.py), and crawling for emails from a list of wiley abstract links (xhelper.py).

# Clone the repo (if you haven't yet)

- in terminal

```
git clone https://github.com/jeffthemaximum/xshovel.git
```

# Install virtualenv (if you haven't yet)

- from the root of the repository, enter this in your terminal

```
pip install virtualenv
```

# make a new virtualenv (if you haven't yet)

- from the root of the repository, enter this in your terminal

```
virtualenv env
```

# activate the virtual environment

- from the root of the repository, enter this in your terminal

```
source env/bin/activate
```

# Install the dependencies (if you haven't yet)

- from the root of the repository, enter this in your terminal

```
pip install -r requirements.txt
```

# To run the emails.py

- from the root of the repository, enter this in your terminal

```
python emails.py
```

video demo of how to use emails.py
https://www.opentest.co/share/c95f960084c411e68aef974fe4b8e57d?focus_title=1


# Setup your spreadsheet for xhelper.py. This is not for emails.py or plos.py.

- Make a Google Spreadsheet
- Make sure you have a sheet with **wiley** in it's sheet name
- Share your Google Spreadsheet with **123114053576-compute@developer.gserviceaccount.com**
- Make a column titled **pageUrl** on the 'wiley' sheet
- Fill your Wiley url's in that column
- Change `spread_sheet_name` on line 389 of `xhelper.py` and save
- You're done. Enjoy the magic. Or maybe not, cuz it might not work, too.
