from new_xhelper_cl import Sheet, Xhelper, Helpers

import os
import urllib

class EmailCleaner:

    f = os.environ['XPYTHON_GSPREAD_CONFIG_FILE']
    opener = urllib.URLopener()
    myfile = opener.open(f)
    file_as_json_str = myfile.read()

    def __init__(self, main, spread_sheet_name = None, sheet_name = None, email_col_name = None, sheet = None):

        if main is True:
            self.xhelper = Xhelper(json_file_name = self.file_as_json_str, spread_sheet_name = spread_sheet_name)
            self.sheet_name = sheet_name
            self.email_col_name = email_col_name
            self.temp_sheet = Helpers.find_sheet_from_spread_sheet(spread_sheet = self.xhelper.spread_sheet, sheet_name = sheet_name)
            self.sheet = Sheet(xhelper = self.xhelper, sheet = self.temp_sheet) # this should be a Sheet object

        self.email_col_num = Helpers.get_column_number(self.sheet, email_col_name)
        self.emails = Helpers.get_all_column_vals_as_row(self.sheet, self.email_col_num)


    def clean(self):

        # check if email is international
        # iterate through list of emails
        # make column to right of last column
        au_col_letter = Helpers.get_last_col_letter(self.sheet.sheet)
        # make header "au emails"
        self.sheet.sheet.update_acell(au_col_letter + '1', 'AU emails')

        ca_col_letter = Helpers.get_last_col_letter(self.sheet.sheet)
        self.sheet.sheet.update_acell(ca_col_letter + '1', 'CA emails')

        gov_col_letter = Helpers.get_last_col_letter(self.sheet.sheet)
        self.sheet.sheet.update_acell(gov_col_letter + '1', 'GOV emails')

        uk_col_letter = Helpers.get_last_col_letter(self.sheet.sheet)
        self.sheet.sheet.update_acell(uk_col_letter + '1', 'UK emails')

        other_col_letter = Helpers.get_last_col_letter(self.sheet.sheet)
        self.sheet.sheet.update_acell(other_col_letter + '1', 'OTHER emails')

        au_count = 0
        ca_count = 0
        gov_count = 0
        uk_count = 0
        other_count = 0
        accepted_domains = ['com', 'net', 'us', 'edu', 'org']
        for idx, email in enumerate(self.emails):
            # get end of emails
            after_dot = email.split('.')[-1]
            # if ends in .au
            if after_dot == 'au':
                au_count += 1
                # put emails in appropriate rows
                self.sheet.sheet.update_acell(au_col_letter + str(idx + 2), email)

            # if ends in .ca
            if after_dot == 'ca':
                ca_count += 1
                self.sheet.sheet.update_acell(ca_col_letter + str(idx + 2), email)
            # if ends in .gov
            if after_dot == 'gov':
                # make grey
                gov_count += 1
                self.sheet.sheet.update_acell(gov_col_letter + str(idx + 2), email)
            # if ends in .uk
            if after_dot == "uk":
                uk_count += 1
                self.sheet.sheet.update_acell(uk_col_letter + str(idx + 2), email)
            # if unrecognized
            if after_dot not in accepted_domains and email != '':
                other_count += 1
                self.sheet.sheet.update_acell(other_col_letter + str(idx + 2), email)

        # make header "au emails"
        self.sheet.sheet.update_acell(au_col_letter + '1', str(au_count) + " " + 'AU emails')
        self.sheet.sheet.update_acell(ca_col_letter + '1', str(ca_count) + " " + 'CA emails')
        self.sheet.sheet.update_acell(gov_col_letter + '1', str(gov_count) + " " + 'GOV emails')
        self.sheet.sheet.update_acell(uk_col_letter + '1', str(uk_count) + " " + 'UK emails')
        self.sheet.sheet.update_acell(other_col_letter + '1', str(other_count) + " " + 'OTHER emails')
        # Group('scraper-'+str(self.scrape_id), channel_layer=self.message.channel_layer).send({'text': "COMPLETE!"})

if __name__ == '__main__':

    spread_sheet_name = raw_input("whatchur Google SpreadSheet name? ")
    print("This is the email address you have to share that sheet with: ")
    print("123114053576-compute@developer.gserviceaccount.com")
    sheet_share_confirm = raw_input("Have you done that yet? (enter y or n): ").rstrip()

    while sheet_share_confirm != "y" and sheet_share_confirm != "n":
        sheet_share_confirm = raw_input("You bricked it. Have you done that yet? (enter y or n): ").rstrip()

    if sheet_share_confirm == "y":
        sheet_name = raw_input("What is the name sheet that you can to clean email addresses on? ")
        email_col_name = raw_input("What is the name of the column that contains the email addresses? ")

        email_cleaner = EmailCleaner(main = True, spread_sheet_name = spread_sheet_name, sheet_name = sheet_name, email_col_name = email_col_name)
        email_cleaner.clean()
