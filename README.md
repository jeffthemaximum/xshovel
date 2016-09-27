The Science Direct scraper is a very useful tool for scraping a known list of URLs to articles. They often have information like author names, emails, affiliations, etc. This doc will describe how to currently scrape a set of pages. 


### Before scraping
Beforehand, you will have to get a list of article URLs. They look something like this `http://www.sciencedirect.com/science/article/pii/S001632871630088X`. 

The best way to get the URLs is using something like ImportIO to scrape a journal's index page (`http://www.sciencedirect.com/science/journal/00163287`). 

Another way to get the URLs is to just go through ScieceDirect for the papers that are appropriate or that you want to scrape.

Once you have them, put the list of urls in a spreadsheet.

### 1. Prepare the Spreadsheet
Once you have the URLs of journal articles you want to scrape, set up the spreadsheet. First make sure that the spreadsheet has the columns labeled as [pageUrl, email, author, abstract, affiliation, title, journal].

Then invite a collaborator by adding the email **123114053576-compute@developer.gserviceaccount.com** to have edit access.

### 2. Run the Scraper

#### Local
One option is to locally run the scraper by cloning the [xshovel](https://github.com/experiment/xshovel). To do this, make sure you have python installed and virtualenv activated. Then run `python scrapers/scraper/science-direct`. 

You'll be asked to input the name of the spreadsheet. 

#### SSH into droplet
The easier option is to just SSH into our remote machine by typing `ssh experiment@45.55.74.10`, password is `experiment`. 

There, just `cd xshovel` and run `python scrapers/scraper/science-direct`. 
