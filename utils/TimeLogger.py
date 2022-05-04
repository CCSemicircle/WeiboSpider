import datetime
import logging.handlers
import time
from utils import helper

log_dir = 'log/'
helper.ensureDir(log_dir)

logger = logging.getLogger('Weibo Spider')
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, filename='log/res.log', filemode='a')

logmsg = ''
timemark = dict()
saveDefault = False


def log(msg, save=None, oneline=False):
    global logmsg
    global saveDefault
    time = datetime.datetime.now()
    tem = '%s: %s' % (time, msg)
    if save != None:
        if save:
            logmsg += tem + '\n'
            logger.info(tem)
    elif saveDefault:
        logmsg += tem + '\n'
    if oneline:
        print(tem, end='\r')
    else:
        print(tem)


def marktime(marker):
    global timemark
    timemark[marker] = datetime.datetime.now()


def SpentTime(marker):
    global timemark
    if marker not in timemark:
        msg = 'LOGGER ERROR, marker', marker, ' not found'
        tem = '%s: %s' % (time, msg)
        print(tem)
        return False
    return datetime.datetime.now() - timemark[marker]


def SpentTooLong(marker, day=0, hour=0, minute=0, second=0):
    global timemark
    if marker not in timemark:
        msg = 'LOGGER ERROR, marker', marker, ' not found'
        tem = '%s: %s' % (time, msg)
        print(tem)
        return False
    return datetime.datetime.now() - timemark[marker] >= datetime.timedelta(days=day, hours=hour, minutes=minute,
                                                                            seconds=second)
