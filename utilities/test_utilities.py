import os
import argparse
from . import utils3_5 as utils
import time
import traceback
import inspect
import unittest

logGod = utils.Logger(__name__)
logger = logGod.logger()

baseFolder = os.path.dirname(traceback.extract_stack()[-2][0])
# baseFolder = os.path.dirname(os.path.abspath(__file__))
if baseFolder.find('/tests/') != -1:
    LIBPATH = baseFolder[:-7] + '/'
elif baseFolder.find('/tests') != -1:
    LIBPATH = baseFolder[:-6] + '/'
elif baseFolder == 'tests':
    LIBPATH = '.'
elif baseFolder[-4:] == '/lib' or baseFolder[-5:] == '/lib/':
    LIBPATH = baseFolder
else:
    LIBPATH = baseFolder + '/lib'


def get_fixture_path(filename):
    return LIBPATH + '/tests/fixtures/' + filename


def open_n_parse(filename):
    logger.warning('DEPRECATED METHOD OF HELL : open_n_parse')
    import f5utils as f5
    f = open(get_fixture_path(filename), 'r')
    config = f.read()
    f.close()
    dict_of_type = {}
    return f5.parse(config, dict_of_type, {'is_silent': True})


def parse_params():
    """Default test case parse params and set debug levels"""
    parser = argparse.ArgumentParser(
        description='Unittest parser'
    )
    parser.add_argument("-v", "--verbose",
                        help='increase output verbosity...'
                             'repeat up to 3x (-vvv) for DEBUG',
                        action="count")

    args = parser.parse_args()
    logGod = utils.Logger(__name__)
    logger = logGod.logger()
    logger.warning('test_utilities::parse_params DEPRECATED - Use '
                   'utils.Application() now')
    utils.Logger.toggle_debug_all(level=utils.Logger.setLogLevelFromVerbose(args))
    return logGod, logger


class EnsurePerformance(object):
    """
    Usage
    with EnsurePerformance('test', timeLimit=5) as a:
        a.context='test'
        time.sleep(1)
    """

    def __init__(self, description, timeLimit):
        """
        description: description of the test
        TimeLimit is in seconds
        """
        self.description = description
        self.timeLimit = timeLimit

    def __enter__(self):
        self.startTime = time.time()
        return self

    def __exit__(self, type, value, traceback):
        self.endTime = time.time()
        totalTime = self.endTime - self.startTime
        # logger.debug("%s Total time = %s secs, timeLimit=%s"
        #               % (self.description,
        #                  self.endTime - self.startTime,
        #                  self.timeLimit))
        if totalTime > self.timeLimit:
            raise PerformanceException('%s Expected totalTime under'
                                       '%s, took %s' % (self.description,
                                                        self.timeLimit,
                                                        totalTime))
        else:
            if not traceback:
                logger.critical(
                    'Success. %s Expected totalTime under %s, took %s'
                    % (self.description,
                       self.timeLimit,
                       totalTime))
            else:
                raise


class PerformanceException(Exception):
    pass


# def test_init():
    # #To support relative imports when running unittests files
    # if __name__ == '__main__' and __package__ is None:
    #     sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


def unittest_verbosity():
    """
    Return the verbosity setting of the currently running unittest
    program, or 0 if none is running.
    Unittest must be called via python -m unittest method

    """
    frame = inspect.currentframe()
    while frame:
        self = frame.f_locals.get('self')
        if isinstance(self, unittest.TestProgram):
            return self.verbosity
        frame = frame.f_back
    return 0


def is_in_unittest():
    """
    Tells whether we are being called from unittest or not
    """
    frame = inspect.currentframe()
    while frame:
        self = frame.f_locals.get('self')
        if isinstance(self, unittest.TestProgram):
            return True
        frame = frame.f_back
    return False


def s_unittest_verbosity():
    """
    Will set unittest verbosity in sync with utils.Logger
    """
    global logGod
    if is_in_unittest():
        if unittest_verbosity() == 2:
            verbosity = 10
        elif unittest_verbosity() == 1:
            verbosity = 20
        else:
            verbosity = 40
        logGod.toggle_debug(verbosity)
    else:
        raise Exception('Not running in unittest')
