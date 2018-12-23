from pkg_resources import resource_filename
import configparser
import logging
from imapclient import IMAPClient
import email
import threading
import time
import os

from carrierpigeon import config

# Set up module logger
logger = logging.getLogger(__name__)

# Connect to the server
imap_ssl = bool(config['IMAP']['ssl'])
imap_port = int(config['IMAP']['port'])
imap_host = config['IMAP']['host']

class IMAPThread(threading.Thread):
    server = None
    whitelist = None
    
    def __init__(self):
        super().__init__()

        # whitelist checks
        wl_cfg = config['GENERAL']['whitelist']
        # If whitelist defined, make sure the file exists and can be read
        if wl_cfg and os.access(wl_cfg, os.R_OK):
            with open(wl_cfg) as f:
                self.whitelist = f.read().splitlines()
            print(self.whitelist)
                



    def run(self):
        with IMAPClient(imap_host, ssl=imap_ssl, port=imap_port) as self.server:
            self.server.login(config['CREDENTIALS']['username'], config['CREDENTIALS']['password'])
            self.firstRun()
            self.refresh()

    def firstRun(self):
        # Make sure the inbox is set up with:
        # - Folder: DROP, PROCESSED
        required_folders = ['DROPPED', 'PROCESSED']
        folder_tuples = self.server.list_folders()
        folders = [folder_tuple[2] for folder_tuple in folder_tuples]

        for f in required_folders:
            if f not in folders:
                self.server.create_folder(f)
                logger.info("Created folder {} on server".format(f))


    def refresh(self):
        # Get all emails in the INBOX and process them in the following way:
        # - Is sender in the whitelist?
        #   - No: Archive email in DROP
        #   - Yes: Does it have an attachment?
        #     - No: Archive email in PROCESSED
        #     - Yes: Send attachment to attachment thread (use queue)
        #            Archive email in PROCESSED
        select_info = self.server.select_folder('INBOX')
        inbox_emails = self.server.search()
        print(inbox_emails)
        for uid, message_data in self.server.fetch(inbox_emails, 'RFC822').items():
            email_message = email.message_from_bytes(message_data[b'RFC822'])
            email_address = email.utils.parseaddr(email_message.get('From'))[1]
            # Check if email is in whitelist and drop if not
            if self.whitelist and email_address not in self.whitelist:
                self.server.move(messages=[uid], folder='DROPPED')
            else:
                self.server.move(messages=[uid], folder='PROCESSED')

#print(uid, email_message.get('From'), email_message.get('Subject'))




    def archive(self, id, folder):
        # Archive specified email into folder
        pass
