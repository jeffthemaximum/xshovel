import kickbox
import os
import urllib
import sys
import pudb

from flanker.addresslib import address

if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scrapers.new_xhelper import Xhelper, Helpers, Sheet

class KickBox:
    client   = kickbox.Client('02badd7192b1aa34282e2dff7e569b340b49283ea3c7cacc20910e42be9b5083')
    kickbox  = client.kickbox()

    @classmethod
    def verify_single_email(cls, email):
        return cls.kickbox.verify(email)

class Mailgun:
    @classmethod
    def verify_single_email(cls, email):
        return address.validate_address(email)

class SheetWithEmailsHelper:
    @classmethod
    def find_verified_email_by_kickbox(cls, email):
        return KickBox.verify_single_email(email)

    @classmethod
    def find_verified_email_by_mailgun(cls, email):
        mg_email = Mailgun.verify_single_email(email)
        if mg_email:
            return mg_email
        else:
            return 0

class SheetWithEmails:    
    def __init__(self, xhelper, sheet):
        self.xhelper = xhelper
        self.sheet = Sheet(self.xhelper, sheet)

        self.email_col_num = Helpers.get_column_number(self.sheet, 'email')
        self.all_emails = Helpers.get_all_column_vals_as_row(self.sheet, self.email_col_num)


        ### Kickbox
        self.all_kb_responses = self.find_verified_emails_from_kb()

        self.all_kb_results = self.results_kb()
        self.all_kb_reasons = self.reasons_kb()
        self.all_kb_did_you_mean = self.did_you_mean_kb()
        self.all_kb_sendex = self.sendex_kb()
        self.all_kb_normalized_emails = self.normalized_kb()
        self.all_kb_users = self.users_kb()
        self.all_kb_domains = self.domains_kb()

        ### Mailgun
        self.all_mg_emails = self.find_verified_emails_from_mg()

    def find_verified_emails_from_mg(self):
        all_mg_emails = []
        count = 0

        for email in self.all_emails:
            count += 1
            print("mailgun verify " + str(count))

            mg_email = SheetWithEmailsHelper.find_verified_email_by_mailgun(email)
            all_mg_emails.append(mg_email)
        return all_mg_emails

    def find_verified_emails_from_kb(self):

        count = 0

        all_kb_responses = []

        for email in self.all_emails:

            count += 1
            print("kickbox verify " + str(count))

            response = SheetWithEmailsHelper.find_verified_email_by_kickbox(email)

            all_kb_responses.append(response.body)

        return all_kb_responses

    def results_kb(self):
        return [el['result'] if el['success'] else 'error' for el in self.all_kb_responses]

    def reasons_kb(self):
        return [el['reason'] if el['success'] else 'error' for el in self.all_kb_responses]

    def did_you_mean_kb(self):
        return [el['did_you_mean'] if el['success'] else 'error' for el in self.all_kb_responses]

    def sendex_kb(self):
        return [el['sendex'] if el['success'] else 'error' for el in self.all_kb_responses]

    def normalized_kb(self):
        return [el['email'] if el['success'] else 'error' for el in self.all_kb_responses]

    def users_kb(self):
        return [el['user'] if el['success'] else 'error' for el in self.all_kb_responses]

    def domains_kb(self):
        return [el['domain'] if el['success'] else 'error' for el in self.all_kb_responses]

    def run(self):
        to_write = [
            ['KB-results', self.all_kb_results],
            ['KB-reason', self.all_kb_reasons],
            ['KB-did-u-mean', self.all_kb_did_you_mean],
            ['KB-sendex', self.all_kb_sendex],
            ['KB-normalized', self.all_kb_normalized_emails],
            ['KB-user', self.all_kb_users],
            ['KB-domain', self.all_kb_domains],
            ['MG-emails', self.all_mg_emails]
        ]
        self.sheet.write_to_sheet(to_write)

def google_sheet_main_init(spread_sheet_name):
    f = os.environ['XPYTHON_GSPREAD_CONFIG_FILE']
    opener = urllib.URLopener()
    myfile = opener.open(f)
    file_as_json_str = myfile.read()

    sheet_name = raw_input("What's the name of the sheet? ").strip().lower()
    # sheet_name = "final list"

    print 'finding sheet'
    xhelper = Xhelper(json_file_name = file_as_json_str, spread_sheet_name = spread_sheet_name)
    for sheet in xhelper.worksheets_list:
        if sheet_name in sheet.title.lower():
            print 'found sheet'
            print sheet.title.lower()
            sheet_with_emails = SheetWithEmails(xhelper = xhelper, sheet = sheet)
            sheet_with_emails.run()

def main():

    sheet_name = raw_input("whatchur Google SpreadSheet name? ")
    google_sheet_main_init(spread_sheet_name = sheet_name)  

    
    # print("This is the email address you have to share that sheet with: ")
    # print("123114053576-compute@developer.gserviceaccount.com")
    # sheet_share_confirm = raw_input("Have you done that yet? (enter y or n): ").rstrip()
    # while sheet_share_confirm != "y" and sheet_share_confirm != "n":
    #     sheet_share_confirm = raw_input("You bricked it. Have you done that yet? (enter y or n): ").rstrip()
    # if sheet_share_confirm == "y":
    #     google_sheet_main_init(spread_sheet_name = sheet_name)
    # else:
    #     print("well go do that then")

if __name__ == '__main__':
    main()