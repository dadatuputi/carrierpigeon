from pkg_resources import resource_filename
import configparser
import logging
from imapclient import IMAPClient
import threading
import time

from carrierpigeon import config

# Set up module logger
logger = logging.getLogger(__name__)

# Connect to the server
imap_ssl = bool(config['IMAP']['ssl'])
imap_port = int(config['IMAP']['port'])
imap_host = config['IMAP']['host']

class IMAPThread(threading.Thread):
    def __init__(self):
        super().__init__()


    def run(self):
        server = IMAPClient(imap_host, ssl=imap_ssl, port=imap_port)
        server.login(config['CREDENTIALS']['username'], config['CREDENTIALS']['password'])
        print(server.list_folders())
 

