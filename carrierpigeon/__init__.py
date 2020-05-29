import tempfile
import errno
from pkg_resources import resource_stream, resource_string
import configparser
import logging


# Read settings file
settings = resource_string("carrierpigeon","settings.conf").decode()
config = configparser.ConfigParser()
config.read_string(settings)

# Set up logging
logger = logging.getLogger() # Root logger for __init__.py
logger.setLevel(logging.DEBUG)
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
log_location = config['GENERAL']['log']
file_handler = logging.FileHandler(log_location)
file_handler.setFormatter(log_format)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.info("Configuration file parsed")
logger.info("Logging to {}".format(log_location))

# Process the audio file types
audio_formats_file = resource_string("carrierpigeon", "audio_formats.txt").decode()
# For each line, strip whitespace and split by comma
audio_formats = tuple(line.strip() for line in audio_formats_file.strip().splitlines() if not line.startswith('#') and line.strip())
logger.debug("Read in {} audio file types".format(len(audio_formats)))


def isWritable(path):
    try:
        testfile = tempfile.TemporaryFile(dir = path)
        testfile.close()
    except OSError as e:
        if e.errno == errno.EACCES:  # 13
            return False
        e.filename = path
        raise
    return True


# Check the in/out directory for permissions
msg_in = config['GENERAL']['msg_in']
msg_out = config['GENERAL']['msg_out']
assert isWritable(msg_in)
assert isWritable(msg_out)
