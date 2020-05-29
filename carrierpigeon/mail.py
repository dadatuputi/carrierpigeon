from pkg_resources import resource_filename
import configparser
import logging
from imapclient import IMAPClient
import email
import threading
import time
import dateutil.parser
import os

from carrierpigeon import config, audio_formats

# Set up module logger
logger = logging.getLogger(__name__)

# Connect to the server
imap_ssl = bool(config['IMAP']['ssl'])
imap_port = int(config['IMAP']['port'])
imap_host = config['IMAP']['host']


class IMAPThread(threading.Thread):
    
    
    server = None
    whitelist = None
    pollingfreq = None


    def __init__(self):
        super().__init__()

        # whitelist checks
        wl_cfg = config['GENERAL']['whitelist']
        # If whitelist defined, make sure the file exists and can be read
        if wl_cfg and os.access(wl_cfg, os.R_OK):
            with open(wl_cfg) as f:
                # For each line, strip whitespace and split by comma
                self.whitelist = {line.split(",")[1].strip(): line.split(",")[0].strip() for line in f.read().splitlines() if line.strip() and not line.startswith('#')}
                logger.info("Read in {} whitelist entries".format(len(self.whitelist)))

        # Get polling frequency from config
        self.pollingfreq = config['GENERAL'].getint('pollingfreq', fallback=30)
                

    def run(self):
        with IMAPClient(imap_host, ssl=imap_ssl, port=imap_port) as self.server:
            self.server.login(config['CREDENTIALS']['username'], config['CREDENTIALS']['password'])
            self.firstRun()
            logger.info("Completed IMAPClient setup")
            logger.info("Starting IMAPClient refresh loop, refreshing every {} seconds".format(self.pollingfreq))

            while True:
                self.refresh()
                logger.info("Completed poll of server")
                time.sleep(self.pollingfreq)


    def firstRun(self):
        # Make sure the inbox is set up with:
        # - Folder: DROP, PROCESSED
        required_folders = ['DROPPED', 'PROCESSED', 'FAILED']
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
        logger.info("Found {} emails in the inbox".format(len(inbox_emails)))

        for uid, message_data in self.server.fetch(inbox_emails, 'RFC822').items():
            email_message = email.message_from_bytes(message_data[b'RFC822'], _class=email.message.EmailMessage)
            email_address = email.utils.parseaddr(email_message.get('From'))[1]
            logger.info("Processing email from {}".format(email_address))

            # Check if email is in whitelist and drop if not
            dest_folder = None
            if self.whitelist and email_address not in self.whitelist.keys():
                dest_folder = 'DROPPED'
            elif self.process_email(self.whitelist[email_address], email_message):
                dest_folder = 'PROCESSED'
            else:
                pass
#                dest_folder = 'FAILED'

#            self.server.move(messages=[uid], folder=dest_folder)
#            logger.info("Moved email from {} to {}".format(email_address, dest_folder))


    def process_email(self, name, email_message):
        # Process email
        for attachment in email_message.get_payload():
            attachment_filename = attachment.get_filename()
            if attachment_filename and attachment_filename.endswith(audio_formats):
                # Convert timezone date to timestamp
                email_date = dateutil.parser.parse(email_message.get('Date'))
                logger.info("Processing file {} from {} received at {}".format(attachment_filename, name, email_date.strftime('%d%b%Y %H:%M')))

                
        return False
