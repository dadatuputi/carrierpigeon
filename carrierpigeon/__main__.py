import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='log', level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main(args=None):
    from carrierpigeon import mail, audio
    thread_imap = mail.IMAPThread()
    thread_imap.run()



if __name__ == "__main__":
    main()
