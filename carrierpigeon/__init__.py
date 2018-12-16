import tempfile
import errno
from pkg_resources import resource_filename
import configparser

settings = resource_filename("carrierpigeon","settings.conf")
#logger.info(f"Located settings.conf file at {settings}")
config = configparser.ConfigParser()
config.read(settings)



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
