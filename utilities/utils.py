from __future__ import absolute_import
from __future__ import print_function
import code
from datetime import datetime as dt
import datetime
from datetime import timedelta as td
import fnmatch
import functools
import getpass
import gzip
import inspect
import logging
from hashlib import md5
import os
import re
import socket
import string
import struct
import sys
import time
import traceback
import subprocess
from pprint import pprint, pformat
import curtsies.fmtfuncs as fmtfuncs
import six
from six.moves import map
from six.moves import range
from six.moves import zip
from six.moves import input
import unicodedata

supermenu2 = None

REGEXP_IPADDRESS_FULL = r'[0-9]{1,3}(?:\.[0-9]{1,3}){3}'

# To replace all print statements and control output in module import 
# and unittest
stdout = sys.stdout

# PRELOAD certain modules, used for this own script.
def pythonVersionMin(majorVersion, minorVersion, raiseIfNotMet=True, majorVersionMustMatch=True, description=""):
    """
    2016-06 GuillaumeNM
    Checks python interpreter version and raise an importError if not met
    Input params:
        majorVersion <INT> : Expected Python Major version
        minorVersion <INT> : Minimal Python minor version
        raiseIfNotMet <OPTIONAL ><BOOL> : Tells whether to raise an exception
                                         or not if minimal version if not met
        majorVersionMustMatch <OPTIONAL ><BOOL> : Tells whether major version
                                              must match, or bigger is better
        description <OPTIONAL> custom error message to be appended.
                               __file__ fits nicely here

    Usage :
    pythonVersionMin(2, 5, raiseIfNotMet=True,
                     majorVersionMustMatch=True, description=__file__)

    Return:
        <Bool> Returns if specs are met or not
    """
    # Inferior version
    if (sys.version_info[0] < majorVersion or
        (sys.version_info[1] < minorVersion and
         sys.version_info[0] == majorVersion)):
        if raiseIfNotMet:
            raise PyVersionError("Requires Python %s.%s+ to load %s"
                                 % (majorVersion, minorVersion, __file__))
        else:
            return False
    elif (sys.version_info[0] == majorVersion and
          sys.version_info[1] < minorVersion):
        if raiseIfNotMet:
            raise PyVersionError("Requires Python %s.%s+ to load %s"
                                 % (majorVersion, minorVersion, __file__))
        else:
            return False
    elif (sys.version_info[0] > majorVersion and
          majorVersionMustMatch):
        if raiseIfNotMet:
            raise PyVersionError("Your Python version is too new. Use %s.%s+"
                                 % (majorVersion, minorVersion))
        else:
            return False
    return True


class PyVersionError(Exception):
    pass

if pythonVersionMin(2,5,raiseIfNotMet = False):
    from .utils2_5 import *

if pythonVersionMin(3,0,raiseIfNotMet = False):
    from io import StringIO
    from io import TextIOWrapper as file
else:
    from StringIO import StringIO

# END IMPORTS.
# BEGIN CONSTANTS
TMP_DIR = '/tmp/'
LOGGER_PREFIX = 'GNM.'
TIME_FORMAT = '%Y-%m-%d %H%M%S'
F5_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
# END CONSTANTS


# PRELOAD LOGGER is defined for usage within the module
class Logger(object):
    """Custom logger implementation ala Guillaume
    Usage : logGod = utils.Logger()
            logger = logGod.logger()
            logger.debug('Log away !! ')
    Default to default logger  which defaults to logging.WARNING
    Why use this class? I control all logging in the world, I support multiprocessing logging, and I am the ruler of all the levels !
    """
    # Default global level
    level = logging.WARNING
    root_logger = logging.getLogger()

    def __init__(self, name, outputToFile=False):
        if name == '':
            raise Exception('empty name')
        root_level = Logger.level
        if root_level == 0:
            root_level = logging.WARNING
        self._loggername = name
        if os.getcwd()[-4:] == '/lib':
            filename = '../log/' + name + '.log'
        else:
            filename = 'log/' + name + '.log'
        # logging.basicConfig(level = root_level,
        #     format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        #     datefmt = '%Y-%m-%d %H:%M',
        #     filename = filename,
        #     filemode = 'w')
        self._logger = logging.getLogger(LOGGER_PREFIX + name)
        self._logger.setLevel(root_level)
        # Verify if handlers are already present (to avoid readding multiple)
        if self._logger.handlers == []:
            if outputToFile:
                print('utilities::Logger Warning, logging to file not yet implemented')
            else:
                # create console handler with a higher log level
                self.streamhandler = logging.StreamHandler(sys.stdout)
                self.streamhandler.setLevel(root_level)
                # create formatter and add it to the handlers
                formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d %(name)-12s '
                                              '%(levelname)-8s %(message)s',
                                              datefmt='%Y-%m-%d %H:%M:%S')
                self.streamhandler.setFormatter(formatter)
                #
                self._logger.addHandler(self.streamhandler)
        self.debug = False

    @classmethod
    def multiprocessMe(cls):
        """
        Does not work yet. Copy of the multiprocessing_log snipplet I used.
        """
        # For compatibility with non-multiprocessing host 
        import multiprocessing_logging
        print("Trying to apply multiprocessing logger")
        logger.critical("Trying to apply multiprocessing logger")
        for logger_name, logger_obj in logging.Logger.manager.loggerDict.items():
            if logger_name[0:4]=='GNM.':
                print(("Trying to apply multiprocessing logger on %s" % (logger_name)))
                logger_obj = logging.getLogger(logger_name)
                multiprocessing_logging.install_mp_handler(logger_obj)

    @classmethod
    def setLogLevelFromVerbose(cls, args):
        """Used with argparse, to set proper log level,
        depenging on the number of args.verbose !
        Usage:

        """
        if not args.verbose:
            lvl = 30
        elif args.verbose == 1:
            lvl = 20
        elif args.verbose == 2:
            lvl = 10
        elif args.verbose >= 3:
            lvl = 10
        else:
            logger.critical("UNEXPLAINED NEGATIVE COUNT!")
            lvl = "ERROR"
        return lvl

    @classmethod
    def is_debug(cls):
        return Logger.level == logging.DEBUG

    @classmethod
    def isDebug(cls):
        return Logger.is_debug()

    @classmethod
    def toggle_debug_all(cls, level=None):
        """
        General debug turn off or on. On root logger.
        returns True if in DEBUG mode
        """
        global logger
        if (cls.level == logging.DEBUG or level) and level != logging.DEBUG:
            if not level:
                level = logging.INFO
            # logger.debug("Debugging off ")
        else:
            level = logging.DEBUG
            logger.debug("Mode debugging ")
        cls.root_logger.setLevel(level)
        logger.setLevel(level)
        for handler in cls.root_logger.handlers:
            handler.setLevel(level)
        for handler in logger.handlers:
            handler.setLevel(level)
        # Recursively set level
        cls.set_loggers_lvl(level)
        cls.level = level
        return cls.level == logging.DEBUG

    @classmethod
    def set_loggers_lvl(cls, logger_lvl):
        """
            GuillaumeNM 2016-05
            Sets all my logger to the same level. This is also use to address
            a multiprocess bug, which my new loggers lose their lvl
        """
        if logger_lvl not in [0, 10, 20, 30, 40, 50]:
            raise Exception('Invalid logger_lvl. Expecting logging.DEBUG '
                            '=> CRITICAL, got %s' % (logger_lvl))
        cls.level = logger_lvl
        for lName, lObj in logging.Logger.manager.loggerDict.items():
            if lName[0:4] == 'GNM.':
                logging.getLogger(lName).setLevel(logger_lvl)
                for handler in logging.getLogger(lName).handlers:
                    handler.setLevel(logger_lvl)

    @classmethod
    def get_loggers(cls):
        return list(logging.Logger.manager.loggerDict.items())

    @classmethod
    def get_loggers_level(cls):
        """Will print loggername and level like :
                            unittests GNM GNM.F5_GTM_verify_dns_v2 10
                            GNM.lib 10
                            unittests.F5_GTM_verify_dns 40
                            GNM.lib.test_utilities 10
                            GNM.lib.f5utils 10
                            GNM.lib.utils 10
        """
        print(("RootLogger=%s lvl=%s" % (cls.root_logger.level, cls.root_logger.level)))
        for handler in cls.root_logger.handlers:
            print(("    %s  :: %s" % (handler.level, handler)))
        for logger_name, logger_obj in sorted(Logger.get_loggers()):
            try:
                print(("%s %s" % (logger_name, logger_obj.level)))
                for handler in logger_obj.handlers:
                    print(("    %s  :: %s" % (handler.level, handler)))
            except Exception:
                pass

    def logger(self):
        return self._logger

    def get_handler(self):
        return self.streamhandler

    def toggle_debug(self, level=None):
        """
        Method that toggle global debug flag on or off,
        and try to adjust logger options
        Returns _debug boolean
        """
        if ((level and (level != logging.DEBUG)) or
           (not level and self._logger.level == logging.DEBUG)):
            if not level:
                level = logging.INFO
            logger.warning("Debugging off for logger %s "
                           % (self._logger.name))
        else:
            level = logging.DEBUG
            logger.warning("Mode debugging %s " % (self._logger.name))
        # Set logger and handlers level accordingly.
        self._logger.setLevel(level)
        Logger.level = level
        for handler in self._logger.handlers:
            handler.setLevel(level)
        return self._logger.level == logging.DEBUG


logGod = Logger(__name__)
logger = logGod.logger()


class ArgTypeException(Exception):
    def __init__(self, message):
        if message is None:
            self.message = "ArgTypeException. Please provide correct type"
        else:
            self.message = message

def accepts(exception=ArgTypeException, **types):
    """
    http://code.activestate.com/recipes/578809-decorator-to-check-method-param-types/
    Decorator
    Usage :
    @u.accepts(Exception,a=int,b=list,c=(str,unicode))
    def test(a,b=None,c=None)
        print 'ok'

    test(13,c=[],b='df')
    >Exception

    Supports string (not in tuple).

    for example
    class Test(object):
        def __init__(self):
            pass
        @u.accepts(Exception,self=object, test='Test')
        def add(self, test):
            return self + test

    NoneType is usable via type(None)
    """
    def check_accepts(f):
        assert len(types) == f.__code__.co_argcount, \
        'accept number of arguments not equal with function number of arguments in "%s"' % f.__name__
        @functools.wraps(f)
        def new_f(*args, **kwds):
            for i, v in enumerate(args):
                if f.__code__.co_varnames[i] in types :
                    # GuillaumeNM 2016-09
                    # for not yet defined classes.
                    # FIXME not supported in tuples like (str, int, 'MyCustObj')
                    if isinstance(types[f.__code__.co_varnames[i]], str):
                        if types[f.__code__.co_varnames[i]] != v.__class__.__name__:
                            raise exception("arg '%s'=%s does not match %s" % \
                                (f.__code__.co_varnames[i],v.__class__.__name__,types[f.__code__.co_varnames[i]]))
                            del types[f.__code__.co_varnames[i]]
                    # Normal path
                    else:
                        if not isinstance(v, types[f.__code__.co_varnames[i]]):
                            raise exception("arg '%s'=%r does not match %s" % \
                                (f.__code__.co_varnames[i],v,types[f.__code__.co_varnames[i]]))
                            del types[f.__code__.co_varnames[i]]

            for k, v in six.iteritems(kwds):
                if k in types and not isinstance(v, types[k]):
                    raise exception("arg '%s'=%r does not match %s" % \
                        (k,v,types[k]))

            return f(*args, **kwds)
        new_f.__name__ = f.__name__
        new_f.__doc__ = f.__doc__
        return new_f
    return check_accepts


# other imports after Logger definition
try:
    import argparse
except Exception:
    try:
        # For F5 compatibility, force import from local folder
        logger.info('Module Logparse not Available locally. Trying to import local (for device compatibility)')
        from external import argparse
    except Exception:
        logger.info('Module Logparse not Available')
try:
    # For F5 compatibility, force import from local folder
    # (json not compatible with python 2.4 on F5)
    sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/external/')
    from simplejson.decoder import JSONDecoder as JSONDecoder
except Exception:
    logger.info('Module simplejson not Available.')

try:
    # PRELOAD menu, to avoid recursion of imports
    from . import menu as supermenu
except Exception:
    logger.error('Module Menu not Available.')


def convert_dt_to_utc_dt(dt):
    """
    Function that returns a new utc datetime object for a datetime
        passed in. 
    Requires: datetime object. Can be aware or not of timestamp
    """
    # These 2 modules are not available on F5
    import pytz
    from dateutil import tz
    # If dt is timezone unaware, set it to local timestamp
    if dt.tzinfo == None:
        dt = dt.replace(tzinfo = tz.tzlocal())
    return dt.astimezone(pytz.UTC)


def get_lineprotocol_bool(param):
    """lineprotocol expect boolean values to be string like true or false, not capitalize"""
    if param:
        return "true"
    else:
        return "false"


def get_lineprotocol_str(string):
    # Escape spaces with \
    string.replace(' ', '\ ')
    return "\"" + string + "\""


def unix_time_nanos(dt):
    """Return nanoseconds since epoch"""
    epoch = datetime.datetime.utcfromtimestamp(0)
    return int((dt - epoch).total_seconds() * 1000000)


class Options(object):
    """Class to manage options for other methods.
    Prefix is_something options will be considered boolean. Like is_debug
    Prefix num_something options will be considered integer.
    Prefix list_something options will be considered list.
    Prefix dict_something options will be considered dictionnary.

    Class is serializable via :
    str = json.dumps(utils.Options().attributes)

    And deserializable via
    utils.Options(json.loads(str))
    """
    def __init__(self, options_dict=None, **kwargs):
        if options_dict is None:
            options_dict = {}
        if isinstance(options_dict, Options):
            # This is to avoid setattr and getattr recursion loop. See Stackoverflow q 16237659
            super(Options, self).__setattr__('attributes', options_dict.attributes)
        elif isinstance(options_dict, dict):
            # Parse the debug value
            debug = False
            if '_debug' in options_dict:
                debug = options_dict.pop('_debug')
            if 'debug' in options_dict:
                debug = options_dict.pop('debug')
            if 'is_debug' in options_dict:
                debug = options_dict.pop('is_debug')
            options_dict['_debug'] = debug
            # This is to avoid setattr and getattr recursion loop. See Stackoverflow q 16237659
            super(Options, self).__setattr__('attributes', options_dict)
        else:
            super(Options, self).__setattr__('attributes', {})
        for key, value in six.iteritems(kwargs):
                self.attributes[key] = value
        # Recursive approach to dictionnary to build multiple Options object
        for key, value in six.iteritems(self.attributes):
            if isinstance(value, dict):
                self.attributes[key] = Options(value)

    def __iter__(self):
        """ To overload the iterable operator, like when calling for x in y"""
        for x in self.attributes:
            yield x

    def __repr__(self):
        return "Options < Object> attributes = " + str(self.attributes)

    def __str__(self):
        return "Options < Object> attributes = " + str(self.attributes)

    def has_key(self, name):
        """ Mimic the the dict method, to replace the options={} everywhere"""
        if name == 'debug' or name == '_debug' or name == 'is_debug':
            return True
        else:
            return name in self.attributes

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __dir__(self):
        """ Overload method enumeration to display all accessible methods, which
        are all objects native methods, and all attributes access directly"""
        return sorted(self.__dict__.keys() + self.attributes.keys())

    def __setitem__(self, key, value):
        return self.__setattr__(key, value)

    def __getattr__(self, name):
        if not isinstance(name, str):
            raise TypeError('name must be str. Received + %s'
                            % (name.__class__.__str__))
        if name[0:2] == '__':
            """
            This is to continue supporting built in methods like help()
            which calls in __get__ and __base__
            """
            raise AttributeError("__getattr__ object has no attributes")
        elif name == 'debug' or name == '_debug' or name == 'is_debug':
            # print "1- debug"
            return self.attributes['_debug']
        elif name in self.attributes:
            return self.attributes[name]
        elif name[0:3] == 'is_':
            return False
        elif name[0:4] == 'num_':
            return 0
        elif name[0:5] == 'list_':
            return []
        elif name[0:5] == 'dict_':
            return {}
        else:
            return None

    def __setattr__(self, name, value):
        if name.__class__.__name__ != "str":
            raise TypeError('name must be str. Received + %s' % (name.__class__.__str__))
        if name == 'debug' or name == '_debug' or name == 'is_debug':
            if value.__class__.__name__ == 'bool':
                self.attributes['_debug'] = value
            else:
                raise AttributeError("Setting debug value with a boolean")
        elif name[0:3] == 'is_' and value.__class__.__name__ != 'bool':
            raise AttributeError("Using prefix is_something for a name required a boolean"
                                 " value to be set against. Received : " + str(value))
        elif name[0:4] == 'num_' and value.__class__.__name__ != 'int':
            raise AttributeError("Using prefix num_something for a name required a integer"
                                 " value to be set against. Received : " + str(value))
        elif name[0:5] == 'list_' and value.__class__.__name__ != 'list':
            raise AttributeError("Using prefix list_something for a name required a list "
                                 "value to be set against. Received : " + str(value))
        elif name[0:5] == 'dict_' and value.__class__.__name__ != 'dict':
            raise AttributeError("Using prefix dict_something for a name required a "
                                 "dictionnary value to be set against. Received : " + str(value))
        else:
            self.attributes[name] = value

    def _search(self, pattern):
        results = []
        try:
            pattrn = re.compile(pattern)
        except Exception as e:
            logger.error('Regular Expression is invalid.')
        else:
            results = search(self, pattrn, recursive=True)
            i = 0 
            for res in results:
                print("%s %s" % (i, res))
                i += 1

    def pprint(self, stream=sys.stdout, indent=1):
        indentLvl = indent + 1
        myStream = StringIO()
        for key, item in self.attributes.items():
            if item.__class__.__name__ == 'Options':
                item.pprint(stream=myStream, indent=indentLvl)
            else:
                pprint(item, stream=myStream, indent=indentLvl)
        stream.write(myStream.getvalue())

def search(obj, pattern, recursive=True, recursiveDepth=0):
    """
    Search an object (list, tuple or dict, for a value, and return a list of matching tuple (string, mathing content)
    for example, within the following object :
    my_dict = {"test": 1,
               "test2": ["searchValue"],
               "test3": "Hello World",
               "deepObj": {
                    "Hello": "World",
                    "veryDeepObj": "Hello world"
               }}

    search(my_dict, re.compile('Hello World', re.IGNORECASE), recursive=True)
        -->(obj[\'test3\'], "Hello World",
            obj[\'deepObj\'][\'veryDeepObj\'], "Hello world")

    search(my_dict, re.compile('test', re.IGNORECASE), recursive=True)
        -->[(obj[\'test\'], "test")
            ,(obj[\'test2\'], "test2")
            ,(obj[\'test3\'], "test3")]

    [FIXME] What does recursive do??
    pattern must be a re.compile entity

    [FIXME] Does not support searching for integer values
    """
    results = []
    items = []
    retype = type(re.compile('hello, world'))
    if not isinstance(pattern, retype):
        raise TypeException('pattern must be of type re.compile')
    newDepth = recursiveDepth + 1
    if isinstance(obj, list):
        i = 0
        for item in obj:
            deepResults = []
            if isinstance(item, str):
                if pattern.search(item):
                    results.append(("[%s]" % (i), item))
            else:
                if recursive:
                    deepResults += search(item, pattern, recursive=True, recursiveDepth=newDepth)
                    # Adjust deepResults for this key value
                    for res in deepResults:
                        newRes = ("[%s]%s" % (i, res[0]), res[1])
                        results.append(newRes)
            i += 1
    # If I debug my utility class, can cause conflicts with isinstance
    elif obj.__class__.__name__ == 'Options':
        logger.debug("search():: Option object receive")
        items = obj.attributes.items()
    elif isinstance(obj, dict):
        items = obj.items()
    if items != []:
        for key, attr in items:
            deepResults = []
            if pattern.search(key):
                results.append(("[\'%s\']" % (key), key))
            if isinstance(attr, str) and pattern.search(attr):
                results.append(("[\'%s\']" % (key), attr))
            elif recursive and not isinstance(attr, str):
                deepResults += search(attr, pattern, recursive=True, recursiveDepth=newDepth)
                # Adjust deepResults for this key value
                for res in deepResults:
                    try:
                        newRes = ("[\'%s\']%s" % (key, res[0]), res[1])
                        results.append(newRes)
                    except Exception:
                        logger.error("ERROR searching object:" + str(res), exc_info=Logger.is_debug())
    if recursiveDepth == 0:
        for res in results:
            try:
                # SECURITY ISSUE, using eval should not be package in external apps
                val = eval('obj' + res[0])
                if isinstance(val, str):
                    # Limit length to display
                    val = val[0:100]
                print("%s" % (val))
            except Exception:
                print("%s :: %s" % (res[0], res[1]))
    return results


# http://code.activestate.com/recipes/65211-convert-a-string-into-a-raw-string/
escape_dict = {'\a': r'\a',
               '\b': r'\b',
               '\c': r'\c',
               '\f': r'\f',
               '\n': r'\n',
               '\r': r'\r',
               '\t': r'\t',
               '\v': r'\v',
               '\'': r'\'',
               '\"': r'\"',
               '\0': r'\0',
               '\1': r'\1',
               '\2': r'\2',
               '\3': r'\3',
               '\4': r'\4',
               '\5': r'\5',
               '\6': r'\6',
               '\7': r'\7',
               '\8': r'\8',
               '\9': r'\9'}


def find_files(directory, pattern):
    """Usage find_files('src','*.c')"""
    """stackoverflow q 2186525"""
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


def ip_to_hex(ip_addr, reverse=False):
    """
    Will return hex of ip address.
    reverse will reverse the octet
    exemple
        >>> ip_to_hex('10.1.2.23')
            '0A010217'
        >>> ip_to_hex('10.1.2.23',reverse = True)
            '1702010A'
    """
    array_of_octets = ip_addr.split('.')
    if reverse:
        array_of_octets.reverse()
    return '{:02X}{:02X}{:02X}{:02X}'.format(*list(map(int, array_of_octets)))


# '2013-11-30 17:18:12.556954
def to_d(datetime_string):
    (dt, mSecs) = datetime_string.strip().split(".")
    dt = datetime.datetime(*time.strptime(dt, "%Y-%m-%d %H:%M:%S")[0:6])
    mSeconds = datetime.timedelta(microseconds=int(mSecs))
    fullDateTime = dt + mSeconds
    return str(fullDateTime)


def printTable(arrOfDict, colList=None, streamhandler=sys.stdout, width=240, compact=True):
    """
    Pretty print a list of dictionaries (arrOfDict) as a dynamically sized table.
    If column names (colList) aren't specified, they will show in random order.
    Author: Thierry Husson - Use it as you want but don't blame me.
            Modified, enhanced, pimped up by GNM
    
    arrOfDict :: list of dicts

    colList :: array of string
        Will print only the following keys from the dictionairies in arrOfDict
        ==>if colList is [], will print a list of columns name. Returns nothing.

    streamhandler :: stream object for output. Defaults to sys.stdout

    width :: default print width (if you want to avoid multiline splits, put this high)

    Returns :
        Nothing
    """
    if not isinstance(arrOfDict, list):
        raise TypeError("arrOfDict is not a list")
    i = 0
    for line in arrOfDict:
        i += 1
        if not isinstance(line, dict):
            raise TypeError("line %s is not a dict" % (i))
    if len(arrOfDict) == 0:
        return
    printColList = colList == []
    # Define headers
    # Bug-2018-09-2 headers loses order
    # u.printTable([{'a':True},{'a':False,'betwertertgerterg':2819738964987326423804}])
    # 'betwertertgerterg      | a    '
    # '---------------------- | -----'
    # '                       | True '
    # '2819738964987326423804 | False'

    if not colList or colList == []:
        for i in arrOfDict:
            newColList = list(i.keys())
            # Keep unique values
            if not colList:
                colList = newColList
            elif colList != newColList:
                colList = list(set(newColList + colList))
    if printColList:
        pprint(colList, stream=streamhandler, width=width)
        return

    # 1st row = header
    myList = [colList]
    for item in arrOfDict:
        if compact:
            # Calculate number of line maximum for columns
            maxLine = 1
            for col in colList:
                try:
                    x = pformat(item[col]).splitlines()
                    # Avoiding ternary operator for Python <2.5 compatibility
                    if len(x) > maxLine:
                        maxLine = len(x)
                except Exception:
                    pass
            # Print each column's lines
            for i in range(0, maxLine):
                itemToAdd = []
                for col in colList:
                    if col not in colList:
                        # Display empty on the middle column Line. A 5 maximum line column, should display on the 3rd.
                        if i == round(maxLine/2) + 1:
                            itemToAdd.append('---')
                        else:
                            itemToAdd.append('')
                    else:
                        try:
                            x = pformat(item[col]).splitlines()
                            if i in x and len(x) > i:
                                itemToAdd.append(x[i])
                            else:
                                itemToAdd.append('')
                        except Exception:
                            # Display empty on the middle column Line. A 5 maximum line column, should display on the 3rd.
                            if i == round(maxLine/2) + 1:
                                itemToAdd.append('=ERR=')
                            else:
                                itemToAdd.append('')
                myList.append(itemToAdd)
        else:
            itemToAdd = []
            for col in colList:
                try:
                    itemToAdd.append(str(item[col] or ''))
                except Exception:
                    itemToAdd.append('---')
            myList.append(itemToAdd)
    if len(myList) == 0:
        return
    colSize = [max(map(len, col)) for col in zip(*myList)]
    formatStr = ' | '.join(["{{:<{}}}".format(i) for i in colSize])
    # Seperating line
    myList.insert(1, ['-' * i for i in colSize])
    for item in myList:
        pprint(formatStr.format(*item), stream=streamhandler, width=width)


def format(array_of_array, header_array, options=None, stdout=None):
    """
    stdout: FileHandler object for printing. Defaults to sys.stdout
    Options :
    supports :
        file_handler: FileHandler for opening and closing file (TBC 2016-08)

        Tries to print a nice table format for Python 2.4
        Keyword FILL follow by a field, will be repeated for the length
        of the field. For example:
        FILL=
        If the column length is 10, it will print ==========
        Anything after the repeated character, will be printed in the middle.
        For example
        FILL=MIDDLE
        Will print =====MIDDLE=====
    """
    # 2018-03-21 GuillaumeNM Normalize before printing (unicode to str)
    try:
        for x, arr in enumerate(array_of_array):
            for y, item in enumerate(arr):
                if isinstance(item, unicode):
                    array_of_array[x][y] = unicodedata.normalize('NFKD', item).encode('ascii', 'ignore')
                else:
                    array_of_array[x][y] = str(item)
        for x, item in enumerate(header_array):
            if isinstance(item, unicode):
                header_array[x] = unicodedata.normalize('NFKD', item).encode('ascii', 'ignore')
            else:
                header_array[x] = str(item)
    except Exception:
        logger.error('utils::format() Unable to normalized data', exc_info=logGod.is_debug())
    try:
        if not options:
            options = {}
        if len(array_of_array) == 0:
            return
        output_to_file = False
        if 'file_handler' in options:
            file_handler = options['file_handler']
            output_to_file = True
        if not output_to_file:
            # guillaumeNM 2016-08 Replaced StringIO() by sys.stdout
            # Forgot why it was there in the first place.
            file_handler = sys.stdout
        # 2016-08 Easier stdout support than assuming sys.stdout...
        if stdout is not None:
            file_handler = stdout
        if 'returnValue' in options:
            file_handler = StringIO()
        formatArr = []
        for i in range(0, len(array_of_array[0])):
            # Loop through each row to find longest element of each column
            col_width = 0
            for array in array_of_array + [header_array]:
                try:
                    if (len(str(array[i])) > col_width and
                       not re.match(r'^FILL.+', str(array[i]))):
                        col_width = len(str(array[i]))
                except Exception:
                    logger.error("format:: Error in following line at i=%s "
                                 "Skipping it. %s" % (i, array))
            formatArr.append(col_width)
        # Print using calculated max_width per column
        # ###PRINT HEADER
        for i in range(0, len(array_of_array[0])):
            file_handler.write(
                header_array[i] + (formatArr[i]+1-len(header_array[i]))*" ")
        file_handler.write("\n")
        for i in range(0, len(array_of_array[0])):
            file_handler.write((formatArr[i])*"-"+" ")
        file_handler.write("\n")
        # ###PRINT CONTENT
        for array in array_of_array:
            for i in range(0,len(array_of_array[0])):
                middle_word = ""
                if re.match(r'^FILL.+',str(array[i])):
                    try:
                        repeator = str(array[i]).split('FILL')[1][0]
                        len_left = len_right=(formatArr[i]+1/2)
                        len_total = formatArr[i]
                        if not 'FILL'+repeator == str(array[i]):
                            middle_word = str(array[i])[5:]
                            len_total = formatArr[i]+1
                            len_left=((formatArr[i]+1-len(middle_word))/2)
                            len_right=((formatArr[i]+1-len(middle_word))/2)
                    except Exception:
                        logger.debug('Unable to repeat this character. %s' % (str(array[i])))
                        repeator = '@'
                        middle_word = ""
                        len_left = len_right=(formatArr[i]+1/2)
                        len_total = formatArr[i]+1
                    file_handler.write( len_left*repeator)
                    file_handler.write(middle_word)
                    if len_total%2==1: file_handler.write(' ')
                    file_handler.write( len_right*repeator)
                else:
                    file_handler.write(str(array[i]) + (formatArr[i]+1-len(str(array[i])))*" ")
            file_handler.write("\n")
        if 'returnValue' in options and isinstance(file_handler, StringIO):
            file_handler.seek(0)
            return file_handler.read()
    except KeyboardInterrupt:
        logger.info("CTRL+C Received. Interrupting ... ")
    except Exception:
        logger.error('Cannot print a nice table', exc_info=Logger.is_debug())


def dicts_add(x, y):
    '''Given two dicts, merge them into a new dict as a shallow copy.'''
    try:
        if x.__class__.__name__ == 'dict':
            z = x.copy()
        else:
            raise 'Both objects needs to be dicts received x = ' + str(x) + ' & y = ' + str(y)
        for key in y.keys():
            if key in z:
                if z[key].__class__.__name__=='dict' and y[key].__class__.__name__ == 'dict':
                    # recursive call. Dangerous and exciting at the same time.
                    z[key]=dicts_add(z[key],y[key])
                elif (z[key].__class__.__name__=='int' and y[key].__class__.__name__ == 'int')  or (z[key].__class__.__name__=='list' and y[key].__class__.__name__=='list'):
                    z[key]+=int(y[key])
                else:
                    try:
                        z[key]=int(y[key])+int(z[key])
                    except Exception:
                        print(("Unable to merge these 2 objects together : " + z.__class__.__name__  + ' ' + str(z[key]) + '::' + y.__class__.__name__ + ' ' + str(y[key] )))
            else:
                z[key] = y[key]
    except Exception:
        logger.error('dicts_add General Error')
    return z


def find_line_number_for_x_min_ago(filename, mins_ago, actual_time = None,
                                   options=None):
    """
    actual_time = defaults to Current time. 
    Optionnaly (mostly for testing), you can set time reference of your liking
    Returns:
            matching line index. -1 if not found
    """
    # 2016-08 GuillaumeNM Used by GTM script.
    match_ix = -1
    if not options:
        options = {}
    try:
        o = Options(options)
        # Cannot be set as default value, or else the method, upon load,
        # fixes in time datetime.now()
        if actual_time == None:
            actual_time = datetime.datetime.now()
        logger.debug("actual_time = " + str(actual_time))
        if not os.path.isfile(filename):
            raise Exception("File does not exist" + filename)
        cmd = "wc -l "+ filename
        file_length = int(subprocess.Popen([
                cmd],
                shell=True, stdout=subprocess.PIPE).stdout.read().split()[0])
        left_ix = 0
        right_ix = file_length

        if file_length < 2:
            logger.debug("File too small. Returning line # 1")
            return 1
        current_ix = file_length/2
        time_target = actual_time-td(0, mins_ago*60)
        # GuillaumeNM 2016-03 What does the next 2 line do??
        # if actual_time > last_run_time:
        #    if (dt.now()-last_run_time).seconds> delta_minutes*60:
        # Binary tree search. 0 and 1000 000, first index = 500 000
        # the increase by delta/2 one side or the other (250 000)
        exec_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        # Verify where are we running the script, to determine which awk
        # script to call
        # This is probably a test, running from the lib repository
        if exec_dir.split('/')[-1] == 'lib':
            # Removing the lib folder
            awk_path = "/".join(exec_dir.split('/')[0:-1]) + '/convert_date.awk'
        else:
            awk_path= exec_dir+ '/convert_date.awk'
        if not os.path.isfile(awk_path):
            raise Exception('Utils_find_line_number_for_x_min_ago    Cannot '
                            'locate convert_date.awk script. Attempted search'
                            ' location is :'+ awk_path)
        logger.debug("Utils_find_line_number_for_x_min_ago::awk_path" + awk_path)
        while current_ix != left_ix and current_ix != right_ix:
            logger.debug("current_ix = " + str(current_ix))
            sed_cmd = ("sed -n '%sp;%sq' %s| gawk -v year=%s -f %s" 
                       % (current_ix, current_ix+1, filename,
                          actual_time.year, awk_path))
            line = subprocess.Popen([
                sed_cmd],
                shell=True, stdout=subprocess.PIPE).stdout.read()
            line_datetime = " ".join(line.split()[0:2])
            current_line_datetime = dt.fromtimestamp(time.mktime(time.strptime(line_datetime, F5_TIME_FORMAT)))
            if (current_line_datetime - time_target).seconds < 10 or (time_target - current_line_datetime).seconds < 10:
                match_ix = current_ix
                break
            # If we are passed the time, go back left
            elif current_line_datetime > time_target:
                # Set max boundary
                right_ix = current_ix
                current_ix = current_ix-(current_ix-left_ix) / 2
            # If we are before the time, go forward right
            elif current_line_datetime < time_target:
                # Set max boundary
                left_ix = current_ix
                current_ix = current_ix+(right_ix-current_ix) / 2
            if current_ix <0 or current_ix >file_length:
                raise Error('ExecutionError in find_line_number_for_x_min_'
                            'ago. Out of bounds, need debugging. Args = %s' 
                            % (inspect.getargvalues(inspect.currentframe())))
        if match_ix != -1 :
            logger.debug("find_line_number_for_x_min_ago :: This is the matching"
                         " line " + line)
    except Exception:
        logger.exception("find_line_number_for_x_min_ago::Exception  ")
    return match_ix


# print to stderr output stream
def errorprint(textstr = ""):
    if Logger.is_debug():
        logger.exception("ERROR....==> %s" % (textstr) ) 
    else:
        logger.error(textstr)


# print to stderr output stream
def stderr(textstr = ""):
    sys.stderr.write("" + str(textstr)  )
    

def raw(text):
    """Returns a raw string representation of text"""
    new_string = ''
    for char in text:
        try:
            new_string += escape_dict[char]
        except KeyError:
            new_string += char
    return new_string


def split(str):
    '''
    Methods that split text in array, but preserved quotes from being split
    '''
    PATTERN=re.compile(r'''((?:[^ "']+|"[^"*"]*"|'[^']*'))''')
    array_of_res= PATTERN.split(str)
    for entry in array_of_res:
        if re.match(r'^ +$',entry) or re.match(r'^$',entry):
            array_of_res.remove(entry)
    return array_of_res


# Returns unique array from another array
def unique(arr, objectCompare=False):
    """Uniquify a list. 
    option : objectCompare will be useful for instances of object.
    """
    # 2016-04 GuillaumeNM Change to sorted for Unknown exception with 
    # certain classes of object
    try:
        return list(set(sorted(arr)))
    except Exception:
        return list(set(arr))


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

def compare(a, b):
    """
        Return the # of characters of difference between the 2 strings
    """
    return sum(1 for x,y in zip(a,b) if x!= y)

def check_obj_type_is_or_raise(*args, **kwargs):
    """GuillaumeNM 2016-03 
    Accepts input variable obj=
                              type=
                    optionnal msg=
     Usage is check_obj_type_is_or_raise(obj = object.instance, type = 'list' [,msg = 'This is not a list ! ']) """
    if 'obj' in kwargs and 'type' in kwargs:
        if kwargs['obj'].__class__.__name__==kwargs['type']:
            return True
        elif 'msg' in kwargs:
            raise TypeError(kwargs['msg'])
        else:
            return False
    else:
        logger.info("check_obj_type_is_or_raise::Usage is check_obj_type_is_or_raise(obj = object.instance, type = 'list' [,msg = 'This is not a list ! ']) ")


def d_print(msg, indentation_lvl=0, debug_lvl=0):
    """Debug print. (msg, indentation_lvl = 0,debug_lvl = 0)"""
    global _debug
    global _debug_level
    if "_debug" in globals():
        if (("_debug_level" not in globals()) or
            "_debug_level" in globals() and _debug_level >= debug_lvl):
            logger.info(indentation(indentation_lvl)+msg)


# http://stackoverflow.com/questions/3160699/python-progress-bar
# update_progress() : Displays or updates a console progress bar
# # Accepts a float between 0 and 1. Any int will be converted to a float.
# # A value under 0 represents a 'halt'.
# # A value at 1 or bigger represents 100%
# 2016-08 Change the \r to be at the end instead of the beginning. 
#            For clearer next display
def update_progress(progress, text_progress="", options=None):
    global progressbar_starttime
    global stdout
    if not options:
        options = {}
    _perf_d = False
    if '_perf_d' in options and options['_perf_d']:
        _perf_d = True
    # Modify this to change the length of the progress bar
    barLength = console_width()-len(text_progress)-35
    if barLength < 10:
        barLength = 10
    # if _debug:
    #    print '.... update_progress width:' + str(barLength)
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if 'progressbar_starttime' not in globals():
        progressbar_starttime = datetime.datetime.now()
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        now = datetime.datetime.now()
        totalTime = round((now - progressbar_starttime).seconds/60.0)
        if _perf_d:
            status = ("Done...elapsed time = %s minutes\r\n"
                      % (totalTime, 1))
    block = int(round(barLength*progress))
    text = ("%s\t\tPercent: %s %s%% %s\r"
            % (text_progress,
               "#"*block + "-"*(barLength-block),
               round(progress*100),
               status))
    stdout.write(text)
    stdout.flush()

def hilite(string, status, bold):
    attr = []
    if status:
        # green
        attr.append('32')
    elif string.find('TEMP')!=-1:
        attr.append('33')
    else:
        # red
        attr.append('31')
    if bold:
        attr.append('1')
    return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

"""
return console columns
http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
"""
_console_width = None


def console_width():
    # 2016-04 GuillaumeNM Performance caching
    global _console_width
    try:
        if not _console_width:
            rows, columns = os.popen('stty size', 'r').read().split()
            _console_width = int(columns)
    except Exception:
        # Might be in debugger mode
        _console_width = 100
    return _console_width


def split_string_by(num_char, string):
    return [string[i:i+num_char] for i in range(0, len(string), num_char)]

def contains_ip_address(config):
    count = re.findall('[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}', config)
    return len(count) > 0


def multiline(string, length):
    return split_string_by(length, string)


def most_common(lst):
    """
    This method returns the most frequent value in an array
    """
    y = {}
    for i in lst:
        if i != "":
            if i in y:
                y[i] += 1
            else:
                y[i] = 1
    most_frequent_value = 0
    most_frequent_key = ""
    for key in y.keys():
        if y[key] > most_frequent_value:
            most_frequent_value = y[key]
            most_frequent_key = key
    return most_frequent_key


def menu(array_of_dict_menu, options = None):
    """
        array_of_dict_menu is :
                   {'title':"",
                    'callback method':callback
                    }
    """
    if not options:
        options = {}
    logger.warning('DEPRECATED 2016-06 GuillaumeNM method. '
                   'Use class menu.Menu() instead')
    if '_debug' in globals():
        global _debug
    else:
        _debug = False
    if 'debug' in options and options['debug']:
        _debug = True
    if _debug:
        print("Main menu")
    stay_in_main_menu = True
    while stay_in_main_menu:
        id = 0
        print("==================MENU======================")
        for item in array_of_dict_menu:
            print((str(id)+"- " + item['title']))
            id+=1
        print("d- Debug - Do not use unless you come from Montreal, and are 6'2\"")
        print("     ---------------------------------      ")
        print("Q- Exit")
        print("============================================")
        try:
            selection = input("What do you want to do next? :") 
            answer = selection
            if strIsDigit(answer) and len(array_of_dict_menu)>int(answer):
                item_menu = array_of_dict_menu[int(answer)]
                try:
                    item_menu['callback_method']()
                except Exception:
                    print("Error in menu callback_method")
                    print(("     ==>" + str(sys.exc_info()[0]) + " :: " + str(sys.exc_info()[1]) + str(traceback.extract_tb(sys.exc_info()[2]))))
            elif answer == 'Q' or answer == 'q':
                stay_in_main_menu = False
                sys.exit(1)
            # elif answer == 'd':
            else:
                print(("What what in the Butt ? You said :" + answer + "??"))
        except KeyboardInterrupt:
            print('\nOh... No parlo Americano.')
            stay_in_main_menu = False
            sys.exit()
        except Exception:
            print("Unhandled major error. Probably a MSWindows IRQ error, propagated through quantum finite space. \n If all goes wrong, do not contact the author of this script, he probably doesn't care anymore about it.\n If you are the author of this script, fix your shit." )
            print(("     ==>" + str(sys.exc_info()[0]) + " :: " + str(sys.exc_info()[1]) + str(traceback.extract_tb(sys.exc_info()[2]))))


def strIsDigit(string):
    """
        Method that tells if string is purely an integer or not.
    """
    try:
        int(string)
        return True
    except Exception:
        return False


def multiple_level_hash(current_hash, array_of_keys, count):
    """This will create a hash of hashes, for every sublevel keys provided.
    For example [level1,level2,level3],50 will create
    {level1:{level2:{level3:50}}}.
    Useful to create aggregate statistics base list of entries : ie :
     Company1 Group1 10
     Company2 Group1 5
     Company1 Group2 1
     Company2 Group1 2

    Will give {Company1:{Group1:10,Group2:1},Company2:{Group1:7}}

        Created by : GuillaumeNM 2016-01
    """
    if not isinstance(current_hash, {}):
        print("hash parameter must be of dict type. ")
    if len(array_of_keys) == 0:
        print("array_of_keys length 0")
    current_key = array_of_keys.pop(0)
    current_hash
    if current_key in current_hash:
        # If there is still other level to create hash
        if len(array_of_keys) > 0:
            current_hash[current_key] = multiple_level_hash(current_hash[current_key],
                                                            array_of_keys,count)
        else:
            current_hash[current_key] += count
    else:
        # If there is still other level to create hash
        if len(array_of_keys) > 0:
            current_hash[current_key] = multiple_level_hash({}, array_of_keys,
                                                            count)
        else:
            current_hash[current_key] = count
    return current_hash


class intelligent_file_parsing_for(object):
    """
    This class is use to read a log file, intelligently,
    and store results in a save hash. Next time it is executed,
     we start reading from the last line we read before, if the
     log file wasn't roll over

     Usage example :
     x = u.intelligent_file_parsing_for('python lib/file_seek.py -o START_BYTE -l DELTA_BYTE FILENAME | grep -i "Aug 30 17:07:31"', '/var/log/ltm', 'ProxyInitializationError', options={'reset':True})
     prevRes = x.get_results()
     currentRes = x.get_currentresults()
     # Calculate some results to keep overtime
     resultsToKeep=prevRes+currentRes
     x.update_results(resultsToKeep)
    """

    def __init__(self, command, filename, log_name, options=None):
        """
        command <STR> Command to execute. use keyword
                        START_BYTE DELTA_BYTE and FILENAME
        filename <STR> file to execute command on
        log_name <STR> name of the log file storing the last position.
                       Analog to a baselineName
        options <Options>
                is_reset : will force a reset of the stats
        Example:
            go through logs with
                lib/file_seek.py -o START_BYTE -l DELTA_BYTE FILENAME | grep <SOMETHING>



        """
        if (command and (command.find('START_LINE') != -1 or
           command.find('END_LINE') != -1)):
            raise AttributeError('DEPRECATED keywords START_LINE and END_LINE'
                                 '. Use lib/file_seek.py -o START_BYTE -l '
                                 'DELTA_BYTE FILENAME  instead')
        options = Options(options)
        self.oldmd5 = 'N/A'
        self.currentmd5 = ""
        self.previous_results = {}
        reset = False
        if options.is_reset:
            reset = True
        if options.log_dir is None:
            if os.path.isdir('/shared/log/') and os.access('/shared/log/',
                                                           os.W_OK):
                self.log_dir = '/shared/log/'
            elif os.path.isdir('/var/log/') and os.access('/var/log/',
                                                          os.W_OK):
                self.log_dir = '/var/log/'
            else:
                self.log_dir = '/tmp/'

        self.results_file = self.log_dir+log_name+'.results'
        self.last_run_file = self.log_dir+'.'+log_name+'.lastrun'
        logger.debug('intelligent_file_parsing_for:init results_'
                     'file = ' + self.results_file)
        logger.debug('intelligent_file_parsing_for:init last_run_'
                     'file = ' + self.last_run_file)
        start_byte_num = 0
        # Calculate MD5
        try:
            f4 = open(filename)
            m = md5.new(f4.readline())
            self.currentmd5 = m.hexdigest()
        except IOError:
            logger.error('Filename %s not existing' % (filename))
            raise
        except Exception:
            logger.error( "intelligent_file_parsing_for:init  Unable to verify md5 of first line in file = " + filename )
            if Logger.is_debug():
                logger.exception( 'intelligent_file_parsing_for:init MD5' )
        # ###Check last run file for last run info, md5 and date.
        if not reset and os.path.isfile(self.last_run_file):
            f2 = open(self.last_run_file)
            try:
                content = f2.read()
                # Check if file was resetted
                if content != "":
                    last_run_time, last_byte_num, self.oldmd5 = content.split(',')
                    last_run_time = time.strptime(last_run_time, TIME_FORMAT)
                    start_byte_num = int(last_byte_num)+1
                    if Logger.is_debug():
                        logger.debug('last_run_time,last_byte_num=%s , %s'
                                     % (last_run_time, start_byte_num))
                else:
                    logger.warning("Last Run File is empty")
                    start_byte_num = 1
            except Exception:
                start_byte_num = 1
                if Logger.is_debug():
                    logger.exception('Cannot parse file for last run time' )
            f2.close()
        # #####Find current # of bytes. 
        max_byte_count = os.path.getsize(filename)
        logger.debug('intelligent_file_parsing_for:init max_byte_count=%s '
                     'start_byte_num=%s oldmd5=%s currentmd5=%s '
                     % (max_byte_count, start_byte_num, self.oldmd5,
                        self.currentmd5))
        # If file was rolled over, start new.
        if  self.oldmd5 != self.currentmd5 or (max_byte_count + 1) < start_byte_num:
            start_byte_num = 1
            results = {}
            logger.debug('?File was rolled over?')
        else:
            # Import previous results from file
            # ###Read previous results file
            if os.path.isfile(self.results_file):
                file_res = open(self.results_file)
                try:
                    content = file_res.read()
                    if content != "":
                        try:
                            self.previous_results = eval(content)
                        except Exception:
                            logger.error('Error evaluating saved content %s' % (content))
                            self.previous_results={}
                    else:
                        self.previous_results={}
                finally:
                    file_res.close()
            else:
                self.previous_results={}
        if start_byte_num>= max_byte_count:
            # Nothing to read changes, return empty
            logger.debug( " Nothing to read. (or error) start_byte_num>= max_byte_count " )
            # raise Exception("invalid start_byte_num %s vs max_byte_count %s" % (start_byte_num,max_byte_count) )
        logger.debug('START_BYTE=%s DELTA_BYTE=%s END_BYTE=%s' % (start_byte_num,max_byte_count-start_byte_num,max_byte_count))
        command = command.replace('START_BYTE',str(start_byte_num))
        command = command.replace('END_BYTE',str(max_byte_count))
        command = command.replace('DELTA_BYTE',str(max_byte_count-start_byte_num))
        command = command.replace('FILENAME',filename)
        self.updated_byte_count = max_byte_count
        if Logger.is_debug():
            print('Updated command = ' + command)
        self.command = command

    def get_results(self):
        """Return previous results
        """
        return self.previous_results
    def get_currentresults(self):
        """Return current results
        """
        status,self.currentresults = subprocess.Popen([
                self.command],
                shell=True, stdout=subprocess.PIPE).stdout.read()
        return self.currentresults
    def update_results(self, results):
        # Write results
        file_res = open(self.results_file,'w+')
        file_res.write(str(results ))
        file_res.close()
        ###########
        # Write updated information
        # Only run this if no unhandled errors previously
        f2=open(self.last_run_file,'w+')
        f2.write(str(datetime.datetime.strftime(datetime.datetime.now(),TIME_FORMAT))+','+str(self.updated_byte_count)+','+self.currentmd5)
        f2.close()
        ############
        self.previous_results = results
    def reset(self):
        # Write results
        file_res = open(self.results_file,'w+')
        file_res.write("")
        file_res.close()
        ###########
        # Write updated information
        # Only run this if no unhandled errors previously
        f2=open(self.last_run_file,'w+')
        f2.write("")
        f2.close()
        ############ 
        self.previous_results = {}
        logger.info("Results successfully reseted")


""" 
This class is use compare in time certain values. You can define after how long the kept value will be replace. Useful for threshold over time metrics. For example, # of packets drops over 60 min
"""
class monitor_over_time:
    def __init__(self,command,delta_minutes,update_frequency_minutes,log_name,options = None):
        """ update_frequency_minutes= num of minutes before updating in a new results save. For example, do you want precision up to the minute for an hourly threshold?"""
        if not options: options={}
        _debug = False
        self.previous_results={}
        self.results_to_write = True
        self.discard_previous_results = False
        self.baseline_old_time = None
        self.baseline_new_time = None
        last_run_time_delta_secs = 0
        if options.is_debug:
            _debug = True
        self._debug=_debug
        self.results_file = '/shared/log/monitor_over_time_'+log_name+'.results.gz'
        logger.debug('monitor_over_time::init:: results_file = '+ self.results_file)
        # Get all results.
        self.load_prev_results()
        # Find results closest in time to the delta_minutes
        candidate = None
        for key in self.results_dict.keys():
            if self.results_dict[key]["date"]> dt.now():
                continue
            # Verify if an entry has already been written to the results since the last update_frequency_minutes value
            if (dt.now()-self.results_dict[key]["date"]).seconds < update_frequency_minutes*60:
                self.results_to_write = False
            # Candidate is the first object, unless date is in the past.
            if candidate == None and self.results_dict[key]["date"]< dt.now():
                candidate = self.results_dict[key]
            # Candidate will be replace by the closest result in time, not closer to the limit asked.
            if (dt.now()-self.results_dict[key]["date"]).seconds > delta_minutes*60:
                # Delete all older value, except the choosen one. See below.
                self.results_dict[key]['delete']=True
                # Oldest is the smallest value
                if self.results_dict[key]["date"]>candidate["date"]:
                    candidate = self.results_dict[key]
                    if _debug:
                        print("New candidate found= " + str(candidate["date"]))
        ####
        if candidate != None:
            if _debug:
                print("candidate = " + str(candidate))
            candidate['delete']=False
            if (dt.now()-candidate["date"]).seconds > uptime():
                self.discard_previous_results = True
            self.baseline_old_time = candidate['date']
            self.previous_results = candidate['result']
        else:
            if _debug:
                print("No candidate found")
        if self.discard_previous_results:
            if _debug:
                print("Resetting stats")
            self.reset()
        self.command = command
    def load_prev_results(self):
        self.results_dict={}
        if os.path.isfile(self.results_file):
            res_file = x = gzip.open(self.results_file)
            for line in res_file.readlines():
                try:
                    date_str = line[0:17]
                    results_str = line[18:]
                    # Write to a dict all time and entries.
                    self.results_dict[date_str]={}
                    self.results_dict[date_str]['result']=eval(results_str)
                    self.results_dict[date_str]['date']=dt.fromtimestamp(time.mktime(time.strptime(date_str,TIME_FORMAT)))
                    self.results_dict[date_str]['delete']=False
                except Exception:
                    if self._debug:
                        print(line+"     ==>" + str(sys.exc_info()[0]) + " :: " + str(sys.exc_info()[1]) + str(traceback.extract_tb(sys.exc_info()[2])))
    def get_results(self):
        """Return previous results and last_run_Time
        """
        return self.previous_results,self.baseline_old_time
    def get_currentresults(self):
        """Return current results
        """
        status,self.currentresults = subprocess.Popen([
                self.command],
                shell=True, stdout=subprocess.PIPE).stdout.read()
        self.baseline_new_time = dt.now()
        return self.currentresults
    def write_results_if_required(self, results):
        from datetime import datetime as dt
        # Verify if this result must be write. Depends on init__
        if self.results_to_write:
            if self._debug:
                print("Writing results")
            # Delete Old entries
            for key in self.results_dict.keys():
                if self.results_dict[key]["delete"]:
                    deleted_val = self.results_dict.pop(key)
                    if self._debug:
                        print("Deleting old object ="  + str(deleted_val))
            # Write results
            file_res = gzip.open(self.results_file,'w+')
            # Write old results, not expired
            for key in self.results_dict.keys():
                file_res.write(key + " " + str(self.results_dict[key]['result'] )  + '\n' )
            # Write current result
            file_res.write( str(dt.strftime(self.baseline_new_time,TIME_FORMAT)) + " " + str(results)  + '\n' )
            file_res.close()
        elif self._debug:
            print("Not writing result")
    def reset(self):
        # Write results
        file_res = gzip.open(self.results_file,'w+')
        file_res.write("")
        file_res.close()
        ###########
        # Write updated information
        # Only run this if no unhandled errors previously
        f2=open(self.last_run_file,'w+')
        f2.write("")
        f2.close()
        ############ 
        print("Results successfully reseted")

def normalize_unix_filename(filename):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in filename if c in valid_chars)

def uptime():
    '''Return UNIX system in seconds.'''
    from datetime import timedelta
    f = open('/proc/uptime')
    uptime_seconds = float(f.readline().split()[0])
    f.close()
    return uptime_seconds

def addressInNetwork(ip, network_n_mask):
    """INPUT:
           ip <string>
           network_n_mask <string> format : 192.168.0.0/16
       RETURN <boolean> : is ip in network ?"""
    try:
        ipaddr = struct.unpack('>L', socket.inet_aton(ip))[0]
        net, bits = network_n_mask.split('/')
        if bits == '32':
            return ip == net
        # allmatch
        elif bits == '0':
            return True
        else:
            netmask = struct.unpack('>L',socket.inet_aton(net))[0]
            ipaddr_masked = ipaddr & (4294967295 << (32-int(bits))-1)
            if netmask == netmask & (4294967295 << (32-int(bits))-1):
                return ipaddr_masked == netmask
            else:
                print("****WARNING**** Network",netaddr,"not valid with mask /"+bits)
                return ipaddr_masked == netmask        
    except Exception:
        raise socket.error('illegal IP address string passed to Utils::addressInNetwork')
    return False

def get_bandwidth_str(bits, secs_delta):
    """Methods that will nicely print bandwidth usage. (in bps, Kbps, Mbps or Gbps)"""
    if bits/secs_delta > 1000000000:
        return str(round(float(bits)/secs_delta/1024/1024/1024,2)) + ' Gbps'
    elif bits/secs_delta > 1000000:
        return str(round(float(bits)/secs_delta/1024/1024,1)) + ' Mbps'
    elif bits/secs_delta > 1000:
        return str(round(float(bits)/secs_delta/1024,1)) + ' Kbps'
    else:
        return str(round(float(bits)/secs_delta,0)) + ' bps'


class LinuxServer(object):
    _hostname = None

    def __init__(self):
        pass

    @staticmethod
    def crontab_verify(options=None):
        if options is None:
            options = {}
        cmd = "crontab -l"
        results = subprocess.Popen([
                cmd],
                shell=True, stdout=subprocess.PIPE).stdout.read()
        total = exec_total = err = 0
        for line in results.splitlines():
            try:
                # skip comments and empty lines
                if (line.split() != [] and
                   line.split()[0][0] != '#' and
                   line.split()[0].find('=') == -1 and
                   line.split()[0][0] in "0123456789*"):
                    total += 1
                    filename = line.split()[5]
                    exec_bit = os.access(filename, os.X_OK)
                    if exec_bit:
                        exec_total += 1
                        stdout.write("OK::" + line)
                    else:
                        stdout.write("NOT_EXEC::" + line)
            except Exception:
                err += 1
                logger.error("ERR::" + line, exc_info=Logger.isDebug())
        stdout.write("CronJob::Permissions = OK{" + str(exec_total) + "}BAD{" + str(total-exec_total) + "}ERROR{" + str(err) + "}")

    @classmethod
    def hostname(cls):
        """
        Returns hostname
        for unittest, set LinuxServer.__hostname to desired value
        """
        # 2016-08 Added _hostname for unittest
        if cls._hostname is None:
            return subprocess.Popen([
                "hostname"],
                shell=True, stdout=subprocess.PIPE).stdout.read()
        else:
            return cls._hostname


class Hosts(Options):

    def __init__(self, hostsfile_filenameOrStr, options=None):
        if options is None:
            options = {}
        super(Hosts, self).__init__(options)
        # Check if it looks like a fileName
        if (os.path.isfile(hostsfile_filenameOrStr) or
           re.match(r'^[0-9a-z_\-\.]+$',
                    hostsfile_filenameOrStr,
                    re.IGNORECASE)):
            try:
                x = open(hostsfile_filenameOrStr)
                self.hostsfile_filename = hostsfile_filenameOrStr
                self.hostsfile_data = x.read()
            finally:
                try:
                    x.close()
                except Exception:
                    pass
        else:
            self.hostsfile_data = hostsfile_filenameOrStr
            self.hostsfile_filename = 'From <str>'
        self.load_host_file()

    def __getattr__(self, key):
        if key.upper() in list(self.attributes.keys()):
            return self.attributes[key.upper()]
        else:
            try:
                return self.attributes[key]
            except Exception:
                matches = []
                for hostname, ipaddress in six.iteritems(self.attributes):
                    if ipaddress == key:
                        matches.append(hostname)
                if matches != []:
                    return matches
                raise HostNonDefined(key + ' does not exists')

    def __iter__(self):
        """
        This is to overload the iterable object returned when accessing
        the object like : for x in hosts
        """
        for x in self.attributes:
            yield x

    def __getitem__(self, key):
        return self.__getattr__(key)

    def load_host_file(self):
        self.hosts = {}
        try:
            host_array = self.hostsfile_data.splitlines()
            for host_data in host_array:
                # represents different alias for an IP address
                _hostsAliases = []
                # logger.debug("Hosts::load_host_file host_data=%s"
                #              % (host_data))
                modified_array = [a for a in re.split(r'[ \t,]', host_data) if a != '']
                # Skip empty lines, or commented
                if len(modified_array) < 2 or host_data[0] == "#":
                    continue
                host_ip = modified_array.pop(0)
                # Parse every fields
                while len(modified_array) > 0:
                    host_name = modified_array.pop(0).upper()
                    # End of host section entries
                    if host_name.find('#') > -1:
                        description = host_name[1:]
                        description += " ".join(modified_array) if len(modified_array)>0 else ""
                        for _host in _hostsAliases:
                            try:
                                self.hosts[_host].description = description
                                # logger.info('Setting description %s to Host %s' % (description, _host))
                            except Exception:
                                logger.warning('Host cannot set description to _host=%s' % (_host))
                        break
                    _hostsAliases.append(host_name.upper())
                    # host_description =  modified_array[2:100]
                    if host_name.upper() in self.hosts:
                        logger.error(
                            'Error importing Host file %s duplicate entry: %s'
                            % (self.hostsfile_filename, host_name))
                    else:
                        # logger.debug('....... Adding host %s  :: %s'
                        #              % (host_name, host_ip))
                        self.hosts[host_name.upper()] = IP({'ip': host_ip})
                        self[host_name.upper()] = IP({'ip': host_ip})
        except Exception:
            logger.critical('No host file, or error while loading it')
            raise

class IP(Options):

    """
    This class allows access to a string IP, but with additionnal parameter available if needed.
    i = IP('10.0.0.1')
    i == '10.0.0.1'
    > True
    i.des
    """

    def __init__(self, ip_or_optionsDict=None, **kwargs):
        if isinstance(ip_or_optionsDict, str) and re.match(REGEXP_IPADDRESS_FULL, ip_or_optionsDict):
            ip_or_optionsDict = {'ip': ip_or_optionsDict}
        super(IP, self).__init__(ip_or_optionsDict, **kwargs)
        pass

    def __str__(self):
        return str(self.ip)

    def __repr__(self):
        return self.__str__()

    def __ne__(self, other):
        """Define a non-equality test"""
        return not self.__eq__(other)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.ip == other
        elif isinstance(other, IP):
            self.ip = self.ip
        else:
            return self.ip == other


class HostNonDefined(Exception):
    def __init__(self, message):
        self.message = message


# http://code.activestate.com/recipes/577659-decorators-for-adding-aliases-to-methods-in-a-clas/
class alias(object):
    """
    http://code.activestate.com/recipes/577659-decorators-for-adding-aliases-to-methods-in-a-clas/
    Alias class that can be used as a decorator for making methods callable
    through other names (or "aliases").
    Note: This decorator must be used inside an @aliased -decorated class.
    For example, if you want to make the method shout() be also callable as
    yell() and scream(), you can use alias like this:

        @alias('yell', 'scream')
        def shout(message):
            # ....
    """

    def __init__(self, *aliases):
        """Constructor."""
        self.aliases = set(aliases)

    def __call__(self, f):
        """
        Method call wrapper. As this decorator has arguments, this method will
        only be called once as a part of the decoration process, receiving only
        one argument: the decorated function ('f'). As a result of this kind of
        decorator, this method must return the callable that will wrap the
        decorated function.
        """
        f._aliases = self.aliases
        return f


def aliased(aliased_class):
    """
    Decorator function that *must* be used in combination with @alias
    decorator. This class will make the magic happen!
    @aliased classes will have their aliased method (via @alias) actually
    aliased.
    This method simply iterates over the member attributes of 'aliased_class'
    seeking for those which have an '_aliases' attribute and then defines new
    members in the class using those aliases as mere pointer functions to the
    original ones.

    Usage:
        @aliased
        class MyClass(object):
            @alias('coolMethod', 'myKinkyMethod')
            def boring_method():
                # ...

        i = MyClass()
        i.coolMethod() # equivalent to i.myKinkyMethod() and i.boring_method()
    """
    original_methods = aliased_class.__dict__.copy()
    for name, method in six.iteritems(original_methods):
        if hasattr(method, '_aliases'):
            # Add the aliases for 'method', but don't override any
            # previously-defined attribute of 'aliased_class'
            for alias in method._aliases - set(original_methods):
                setattr(aliased_class, alias, method)
    return aliased_class


is_unittest = None
@alias('in_unittests')
def in_unittest():
    '''Method to tell appart if we are running in Unittest mode. Result is cached'''
    global is_unittest
    if is_unittest == None:
        is_unittest = False
        for line in traceback.format_stack():
            if line.find('unittest.main(')!=-1:
                is_unittest = True
                break
    return is_unittest

is_bpython = None
def in_bpython():
    '''Method to tell appart if we are running in Python interpreter : bpython. Result is cached.'''
    global is_bpython
    if is_bpython == None:
        is_bpython = False
        for line in traceback.format_stack():
            if line.find('/bpython/')!=-1:
                is_bpython = True
                break
    return is_bpython


is_defaultinterpreter = None
def in_defaultinterpreter():
    '''Method to tell appart if we are running in Python interpreter : default. Result is cached.'''
    global is_defaultinterpreter
    if is_defaultinterpreter == None:
        is_defaultinterpreter = False
        for line in traceback.format_stack():
            if line.find('File "<stdin > "')!=-1:
                is_defaultinterpreter = True
                break
    return is_defaultinterpreter

is_interpreter = None
def in_interpreter():
    '''Method to tell appart if we are running in Python interpreter : bpython or default. Result is cached.'''
    global is_interpreter
    is_interpreter= (is_defaultinterpreter or is_bpython)
    return is_interpreter

try:
    from multiprocessing.managers import BaseManager
    class MultiprocessingManager(BaseManager): pass
except Exception:
    logger.info('Cannot import multiprocessing, Manager() not available')
    class MultiprocessingManager(object): pass    

def Manager():
    m = MultiprocessingManager()
    m.start()
    return m


def _init_worker(loglevel=None):
    """For signal handling. Use by work_in_parallel"""
    try:
        import multiprocessing_logging
    except Exception:
        logger.warning('Cannot import multiprocessing_logging. Multiprocess logging will not work')
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    Logger.toggle_debug_all(loglevel)
    # Bug with multiprocessing library. I need to reset my loglevels to the same valuesMake sure all my loggers
    for logger_name,logger_obj in logging.Logger.manager.loggerDict.items():
        if logger_name[0:4]=='GNM.':
            logger_obj = logging.getLogger(logger_name)
            multiprocessing_logging.install_mp_handler(logger_obj)
            # logger.info('utils::_init_worker Logger is now Multiprocessing enabled. logger_name=%s  pid=%s' % (logger_name,os.getpid()))

def work_in_parallel(worker_method, working_list, args=(), **kwargs):
    """
    This method will parallelize anything!!!! Just make sure your program 
    supports parallelism : http://stackoverflow.com/questions/9436757/
        how-does-multiprocessing-manager-work-in-python
        http://noswap.com/blog/python-multiprocessing-keyboardinterrupt
        http://chriskiehl.com/article/parallelism-in-one-line/
        http://stackoverflow.com/questions/8533318/
            python-multiprocessing-pool-when-to-use-apply-apply-async-or-map
        Supports CTRL+C
            http://stackoverflow.com/questions/11312525/
            catch-ctrlc-sigint-and-exit-multiprocesses-gracefully-in-python
        GuillaumeNM 2016-05

        Usage:
            Multithreaded mode : 
                Good for IO bound tasks
                Good for tasks which requires access to other object 
                    (not registered in MultiprocessingManager)
            Multiprocessing mode:
                Good for CPU bound tasks
                Good for repetitive tasks that are independant.
                Good for tasks with registered Manager objects

            # you must register new orchestror classes to the 
                MultiprocessingManager, in Multiprocess mode, to keep in sync.
            
            utils.MultiprocessingManager.register('Result', Result)
            multiprocessing_manager = utils.Manager()
            results = multiprocessing_manager.Result(startat = 10)
            work_in_parallel(worker_method,working_list,args=(), **kwargs)

            Another option is to define multiprocessing shared variables in a 
            class

            class Orchestrator(object):
                def __init__(self,**kwargs):
                    self.manager = multiprocessing.Manager()
                    self.mp_shared_ns = self.manager.Namespace()
                    # This will be shared across process, not copied
                    self.mp_shared_ns.integer_variable = 0
                    # List and dicts needs to be proxied differently
                    self.ips = self.manager.dict({})
                    self.macaddresses = self.manager.dict({})
                def run(self):
            orchestrator = Orchestrator
            def run(orchestrator):
                orchestrator.run()
            work_in_parallel(Orchestrator().run, working_list, args=(orchestrator), **kwargs)
                    

            Finally if all tasks are independent, just run it !
                
                work_in_parallel(run, working_list, args=(), **kwargs)

            kwargs supported:
                 is_benchmarked for time performance output
                 num_thread : Number of working threads
                 is_cpu_bounded = False  . For CPU bound tasks, multiple thread
                                           will slow down the environment,
                                           while muliple process will speed it
                                           up.
         ***Vary the number of threads to verify best performance for your environment.

         Troubleshooting  : If you are getting pickle error
                          ___________
                         [___________]
                         /           \
                        /~~^~^~^~^~^~^\
                       |===============|
                       | P I C K L E S |
                       | ,-.   __      |
                       | \ ,'-'. )     |
                       |  '._'_;'      |
                       ;===============;
                        \             /
                         `""'""``""'"`
                It is because you are trying to pass between process a class 
                object which is not registered with the manager
        Example : 
            def test(args):
                if args.__class__.__name__!='list' or len(args)!=2:
                       # logger.error("Invalid parameters given to worker method")
                       print "Invalid parameters given to worker method"
                work_unit,options = args
                i = work_unit
                j = i
                while j < 10000000:
                    # print "Thread i=%s iteration j=%s" % (i,j)
                    j+=1
                    # time.sleep(0.01)
                print "Thread i=%s completed! "% (i)
                return i 

            results = work_in_parallel(test,range(0,9),num_thread = 4,is_cpu_bounded = True,is_benchmarked = True)
    """
    from multiprocessing import Pool
    from multiprocessing.dummy import Pool as ThreadPool 
    import multiprocessing
    import signal
    if not hasattr(working_list, '__iter__'):
        raise TypeError('working_list arg must be an iterable.')
    # FIXME 2016-05 GuillaumeNM Multiprocessing logger does not have any handlers, therefore missing critical valid logs. 
    # mp_logger = multiprocessing.get_logger()
    # mp_logger.setLevel(logging.getLogger().level)
    # for handler in mp_logger.handlers:
    #     handler.setLevel(logging.getLogger().level)
    logger.debug('Current processID=%s' % (os.getpid()))
    options = Options(**kwargs)
    logger.debug( 'work_in_parallel: options=%s args=%s kwargs=%s' % ( options, str(args) ,str(kwargs) ) )
    # Prepare array for arguments. Map function does not support arguments
    num_thread = options.num_thread
    if num_thread == 0:
        num_thread = None
    try:
        try:
            start = time.time()
            # Ignore SIGINT before forking
            original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
            if options.is_cpu_bounded:
                logger.debug('Multiprocessing mode num_thread=%s' % (num_thread))
                pool = Pool(num_thread, initializer=_init_worker,
                            initargs=(logging.getLogger().level,))
            else:
                logger.debug('Multiprocessing mode num_thread=%s'
                             % (num_thread))
                # Defaults to num cpu in the machine
                pool = ThreadPool(num_thread)
            # Restore SIGINT after forking
            signal.signal(signal.SIGINT, original_sigint_handler)
            jobs = []
            for work in working_list:
                args_to_pass = (work,)+args
                jobs.append(pool.apply_async(func=worker_method,
                                             args=args_to_pass))
                logger.debug('Async task started for method%s args=%s'
                             % (worker_method, args_to_pass))
            logger.debug('Async task completed. Waiting for termination')
            for job in jobs:
                # Without the timeout this blocking call ignores all signals.
                job.get(36000)
            logger.debug('Async task completed. Closing pool')
            pool.close()
            pool.join()
            end = time.time()
            if options.is_benchmarked or options.is_debug:
                if options.is_cpu_bounded:
                    logger.info("Time #processes=%s time=%s"
                                % (num_thread, end - start))
                else:
                    logger.info("Time #threads=%s time=%s"
                                % (num_thread, end - start))
        except KeyboardInterrupt:
            logger.info("So disappointed of you.... Go CTRL+C yourself ! ")
            try:
                pool.terminate()
                pool.join()
            except Exception:
                pool = None
            raise
        except multiprocessing.TimeoutError:
            # FIXME 2016-05 GuillaumeNM Find the filename!
            logger.error('A Task exceeded the max time allowed of 600 mins.')
            pool.terminate()
            pool.join()
            pool = None
        except Exception:
            logger.exception('Forcing Thread/process closure')
            pool.terminate()
            pool.join()
            pool = None
        else:
            logger.info('Normal closure')
        pool = None
    except KeyboardInterrupt:
        raise
    except Exception:
        logger.exception('Unexpected closure')
    try:
        output = {'time': end - start}
    except Exception:
        output = {'time': -1}
    return output


def timeit(method):
    '''https://www.andreas-jung.com/contents/a-python-decorator-for-'''
    '''measuring-the-execution-time-of-methods'''
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        try:
            to_print_args = ""
            # Shorten args
            for arg in args:
                if len(str(arg)) < 40:
                    to_print_args += (str(arg)+', ')
                else:
                    to_print_args += (str(arg)[0:40]+'..., ')
            if te-ts > 100:
                logger.info('Very slow method captured. :: %r (%r, %r)'
                            ' %2.2f sec' %
                            (method.__name__, to_print_args, kw, te-ts))
            logger.debug('%r (%r, %r) %2.2f sec'
                         % (method.__name__, to_print_args, kw, te-ts))
        except Exception:
            logger.exception('Error while timing : %r %2.2f sec'
                             % (method.__name__, te-ts))
        return result

    return timed


def function_get_current_name():
    return inspect.stack()[1][3]


def get_calling_function_name():
    return "Method %s() in file %s:%s " % (inspect.stack()[3][3],
                                           inspect.stack()[3][1],
                                           inspect.stack()[3][2])


def is_piped():
    """ Returns if the program has piped input
    tail -f | this_program ==> True
    """
    return not sys.stdin.isatty()


def string_apply_case(reference, string_to_apply):
    '''Used on strings, to apply case level for each char in reference
                        to string_to_apply
        (reference,string_to_apply)
           (TesT ValuE     , test value) ==> TesT ValuE
           (TesT ValuE     , asdj ljayw) ==> TsdT VjayE
    '''
    result = ""
    min_length = len(reference)
    if len(string_to_apply) < min_length:
        min_length = len(string_to_apply)
    for i in range(0, min_length):
        if reference[i] == reference[i].upper():
            result += string_to_apply[i].upper()
        elif reference[i] == reference[i].lower():
            result += string_to_apply[i].lower()
    return result


def str_binary_or(s1, s2):
    """
    returns a string of 1 and 0 specifying if letters are the same or not
     test1,test2 ==> 11110
    use .find('0') to determine the first diff character.
    """
    return ''.join(str(int(a == b)) for a, b in zip(s1, s2))


@accepts(template_filename=str, template_text=str, data=str)
def apply_textfsm_template(template_filename='', template_text='', data=''):
    """
    Use for influxDB, creating tags and fields parameters.
    Input Parameter :
        template_filename <STR> : template file location
        data <STR> : text to apply textfsm template on

    Return:
        json_bodies <LIST> of dictionaries, compatible with InflubDB JSON
    """
    json_bodies = []
    try:
        from external.textfsm import textfsm
    except Exception: 
        logger.warning('Cannot use textfsm functions without the external.textfsm library')
        return json_bodies
    if template_text != '' and template_filename != '' : raise AttributeError('Cannot have both a template_filename and template_text provided.')
    elif template_text != '':
        template_text = template_text
    else:
        if not os.path.isfile(template_filename): raise IOError('Invalid File =%s' % (template_filename))
        try:
            template_text = open(template_filename).read()
        except Exception:
            logger.error('Unable to open FH for template_filename=%s' % (template_filename) )
    # Split post processing data
    index = template_text.find('POST_PROCESSING')
    if index != -1:
        textfsm_template = template_text[0:index]
        postprocessing_template = "\n".join(template_text[index:].splitlines()[1:])
    else:
        textfsm_template = template_text
        postprocessing_template = ""
    try:
        template_fh = StringIO(textfsm_template)
    except Exception:
        logger.error('Unable to create StringIO FH for text=%s' % (template_text))

    if not data or (data.__class__.__str__ == 'str' and not len(data)>0): raise AttributeError('Data is empty ' )
    try:
        InfluxDB_TIME_FORMAT='%Y-%m-%dT%H:%M:%S.%fZ'
        textfsm_parser = textfsm.TextFSM( template_fh )
        parsed_text = textfsm_parser.ParseText( data )
        list_of_dict = [dict(list(zip(textfsm_parser.header,line))) for line in parsed_text]
        for result in list_of_dict:
            json_body = {}
            json_body['tags'] = {}
            json_body['fields'] = {}
            for key,value in result.items():
                if key[0:2]=='t_':
                    try: value = float(value)
                    except Exception: pass
                    json_body['tags'][key[2:]] = value
                elif key[0:2]=='f_':
                    try: value = float(value)
                    except Exception: pass
                    json_body['fields'][key[2:]] = value
                elif key == 'TIMESTAMP':
                    try:
                        try:
                            dt_object = dt.strptime(value,'%Y-%m-%d%H:%M:%S.%f')
                        except Exception:
                            dt_object = dt.strptime(value,'%Y-%m-%d %H:%M:%S.%f')
                        utc_dt = convert_dt_to_utc_dt(dt_object)
                        json_body['time'] = dt.strftime(utc_dt,InfluxDB_TIME_FORMAT)
                    except : 
                        logger.exception('Unable to parse time correctly value=%s' % (value))
                        json_body['time'] = value
                else:
                    logger.warning('Column will not be mapped correctly key=%s ,value=%s' % (key,value))
            json_bodies.append(json_body)
    except Exception:
        if Logger.is_debug():
            logger.exception('Unable to build JSON_bodies for text=%s template_text=%s' % (data[0:100]+'...', template_text ))
        else:
            logger.error('Unable to build JSON_bodies for text=%s template_text=%s' % (data[0:100]+'...', template_text ))
    # Apply postprocessing matches
    json_bodies = applyPostProcessingTemplate(postprocessing_template, json_bodies)

    return json_bodies

@accepts(template=(str, file), data=str)
def textfsmParse(template, data):
    """
    Template can be the text, a filename, or a FileHandler to the template
    help for template = https://github.com/google/textfsm/wiki/Code-Lab
    """
    json_bodies = []
    template_text = ""
    try:
        from external.textfsm import textfsm
    except Exception: 
        logger.warning('Cannot use textfsm functions without the external.textfsm library')
        return json_bodies
    if isinstance(template, str) and not os.path.isfile(template):
        if template == '':
            raise AttributeError('Cannot have an empty template')
        elif template != '':
            template_text = template_text
    elif isinstance(template, str) and os.path.isfile(template):
        try:
            f = open(template)
            template_text = f.read()
        except Exception:
            logger.error('Unable to open FH for template_filename=%s' % (template) )
        # Python 2.4 retro compatibility
        try:
            f.close()
        except Exception:
            pass
    elif isinstance(template, file):
        template_fh = template
    else:
        logger.error('How come Im here???')
    if not isinstance(template, file):
        try:
            template_fh = StringIO(template_text)
        except Exception:
            logger.error('Unable to create StringIO FH for text=%s' % (template_text))
    textfsm_parser = textfsm.TextFSM(template_fh)
    parsed_text = textfsm_parser.ParseText(data)
    list_of_dict = [dict(list(zip(textfsm_parser.header,line))) for line in parsed_text]
    return list_of_dict


def applyPostProcessingTemplate(postProcessingTemplate, json_bodies):
    """take an array of json_bodies formatted for InfluxDB
    and a postProcessingTemplate <STRING>

    This method will add tags and fields base on  additionnal logic and regular expression"""
    try:
        index = postProcessingTemplate.find('POST_PROCESSING')
        if index != -1:
            postProcessingTemplate = "\n".join(postProcessingTemplate[index:].splitlines()[1:])
        else:
            postProcessingTemplate = postProcessingTemplate
        # Remove initial line with keyword POST_PROCESSING
        for postprocessing_rule in postProcessingTemplate.splitlines():
            """
            Expected format is :
                    [t_|f_]key_name validation_type [value_to_set] 
                                     key_to_apply_regexp_on regexp
            validation_type supported :
                matchAndReplaceStatic : Will verify <regexp>, if it's a match,
                                        will set <key_name> to <value_to_set>
                replaceWithMatch : Will set <key_name> with first value return
                                   from regexp (applying re.findall method)
                default : Will set default value
            example :
                    t_ENCRYPTED matchAndReplaceStatic YES TARGET https\:\/\/
                    t_IPADDRESS replaceWithMatch TARGET https\:\/\/([\d\.]+)
                    t_HOSTNAME default N/A

            t_ means will be set as a tag
            f_ means will be set as a field

            # are interpreted as comments.
            """
            logger.log(5, 'postprocessing_rule=%s' % (postprocessing_rule))
            # Skip commented lines
            if postprocessing_rule.lstrip(' ')[0] == '#':
                continue
            rule_data = postprocessing_rule.split(' ')
            # Remove empty entries
            try:
                while True:
                    rule_data.remove('')
            except Exception:
                pass
            key_name = rule_data[0]
            validation_type = rule_data[1]
            if validation_type not in ['default','matchAndReplaceStatic', 'replaceWithMatch'] : raise AttributeError('valitation_type %s not supported. See documentation.' % (valitation_type))
            if validation_type == 'replaceWithMatch':
                # In case there are spaces in the regexp
                key_target = rule_data[2]
                value = "N/A"
                regexp = " ".join(rule_data[3:])
                logger.log(5,'     rule_data=%s key_name=%s value=%s key_target=%s' % ( rule_data, key_name, value, key_target))
            elif validation_type == 'matchAndReplaceStatic':
                # In case there are spaces in the regexp
                value = rule_data[2]
                key_target = rule_data[3]
                regexp = " ".join(rule_data[4:])
                logger.log(5,'     rule_data=%s key_name=%s value=%s key_target=%s' % ( rule_data, key_name, value, key_target))
            elif validation_type == 'default':
                # In case there are spaces in the regexp
                value = rule_data[2]
            for json_body in json_bodies:
                logger.log(5,'    json_body=%s ' % (json_body))
                if validation_type != 'default':
                    if key_target in json_body['tags']:
                        tag_or_field = json_body['tags'][key_target]
                    elif key_target in json_body['fields']:
                        tag_or_field = json_body['fields'][key_target]
                    else:
                        continue
                    logger.log(5, '     key_target=%s tag_or_field=%s re.match(regexp, tag_or_field)=%s' % ( key_target, tag_or_field, re.match(regexp, tag_or_field)))
                else:
                    logger.log(5, '     DEFAULT match' )
                if validation_type == 'default' or re.match(regexp, tag_or_field):
                    if validation_type == 'replaceWithMatch':
                        try:
                            value = re.findall(regexp, tag_or_field)[0]
                            logger.log(5, 'Found match value=%s' % (value)) 
                        except Exception:
                            logger.debug('Cannot match regexp=%s in tag_or_field=%s ' % (regexp, tag_or_field)) 
                    if key_name[0:2] == 't_':
                        json_body['tags'][key_name[2:]] = value
                        logger.log(5, 'key_name=%s')
                    elif key_name[0:2] == 'f_':
                        json_body['fields'][key_name[2:]] = value
                    else:
                        logger.error('Invalid key_name=%s in Postprocessing template=%s' % (key_name, template_filename))
    except Exception:
        if Logger.is_debug():
            logger.exception('Unable to post process due to an unknown error ')
        else:
            logger.error('Unable to post process due to an error. Please review your configuration and/or run with Debug on. ')
    return json_bodies


class Application(object):
    """
    Generic framework for new application/script

    self.args = Parsed arguments
    self.settings = Current running settings.
    self.config = Configuration loaded from file

    """

    def __init__(self, preserveArgs=False, **kwargs):
        """
        named args:
            preserveArgs <--> Defaults to False. Overrides some argparse 
                              for compatibility (ie unittest)
        Supported [all optional] kwargs :
            history = <str>
            version = <str>
            author = <str>
            buildDate = <str>
            description = <str>
            name = <str>
            configFilename= <filename str>',

        """
        self.useArgParser = True
        self.history = ''
        self.version = ''
        self.author = ''
        self.buildDate = '0000-00-00'
        self.description = ''
        self.logGod = Logger(__name__)
        self.logger = self.logGod.logger()
        self.parser = None
        self.args = Options()
        self.interactive = True
        # Default Application standard output
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.configFilename = None
        # Set kwargs to attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
        if not hasattr(self, 'name'):
            try:
                frame = inspect.stack()[1]
                name = frame[1].split('/')[-1].split('.py')[0]
            except Exception:
                name = 'UnknownApplication'
            self.name = name
        self.settings = Options()
        self.settingsFile = ('%s.%s_%s.lastrun'
                             % (TMP_DIR, self.name, getpass.getuser()))
        self.config = {}
        self.__setDefaultParams()
        self.menu = supermenu.Menu()
        self.preserveArgs = preserveArgs
        if self.preserveArgs:
            self.__preserveArgs()


    def loadConfig(self):
        logger.critical('Method not implemented. See utils 2.7 for minimal implementation')

    def debug(self):
        return self.__isDebug()

    def isDebug(self):
        return self.__isDebug()

    def is_debug(self):
        return self.__isDebug()

    def __isDebug(self):
        return Logger.is_debug()

    def start(self, callbackMethod=None, *args, **kwargs):
        """At the moment, it only parse the params"""
        self.__parseParams()
        if self.__preserveArgs:
            # Reassign ARGS for other program. Like unittest.main()
            if ('other_args' in dir(self.args) and
               self.args.other_args is not None):
                sys.argv[1:] = self.args.other_args
        self.loadConfig()
        if callbackMethod:
            try:
                callbackMethod(*args, **kwargs)
            except KeyboardInterrupt:
                logger.info('Received CTRL+C. Interrupting.')
            except SystemExit:
                logger.debug('Received SystemExit Exiting.')
            except Exception:
                if self.interactive:
                    logger.exception('Application, received unhandled crash.')
                    dropTheMic(globals(), locals())
                else:
                    raise

    def getVersion(self):
        vStr = "VERSION=%s BUILD_DATE=%s" % (self.version, self.buildDate)
        return vStr

    def __setDefaultParams(self):
        """
        Default parse params for scripts and set debug levels.
        Will set application.parser to argparser
        """
        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument("-v", "--verbose",
                            help="increase output verbosity...repeat up to 3x"
                                 " (-vvv) for WARNING,==>INFO==>DEBUG. ",
                            action="count")
        parser.add_argument("-V", "--version",
                            help="Returns the program version",
                            action="store_true")
        parser.add_argument("-b", "--batch",
                            help="Program is not running in interactive mode.",
                            action="store_false",
                            dest="interactive",
                            default=True)
        self.parser = parser

    def __parseParams(self):
        """
        Do the actual params parsing work. Decoupled from the init method to
        allow user to customize new params to be expected via the
        self.parser options
        """
        self.args = self.parser.parse_args()
        logLvl = Logger.setLogLevelFromVerbose(self.args)
        self._debug = Logger.toggle_debug_all(level=logLvl)
        if self.args.version:
            print(self.getVersion())
            sys.exit(0)
        self.interactive = self.args.interactive


    def loadSettings(self):
        """
        Method to import this application settings to the default
        application file
        """
        try:
            logger.debug('About to load settings from %s'
                         % (self.settingsFile))
            try:
                try:
                    f = open(self.settingsFile)
                    newSettings = json.loads(f.read())
                except Exception:
                    logger.exception('Cannot load file')
                    raise
            finally:
                try:
                    f.close()
                except Exception:
                    pass
            self.settings = Options(newSettings)
            logger.info('Settings loaded')
        except Exception:
            if Logger.is_debug():
                logger.exception('Cannot import previous settings.')
            else:
                logger.error('Cannot import previous settings.')

    def saveSettings(self):
        """
        Method to export this application settings to the default
        application file
        """
        try:
            logger.debug('About to save settings from %s'
                         % (self.settingsFile))
            try:
                try:
                    f = open(self.settingsFile, 'w+')
                    f.write(json.dumps(self.settings.attributes))
                except Exception:
                    logger.exception('Cannot save settings file')
                    raise
                logger.info('Settings saved')
            finally:
                try:
                    f.close()
                except Exception:
                    pass
            logger.info('Settings saved')
        except Exception:
            if Logger.is_debug():
                logger.exception('Cannot export settings.')
            else:
                logger.error('Cannot export settings.')

    def __preserveArgs(self):
        """
        Method used to avoid toggling argParser, for unittests own argParser
        """
        self.parser.add_argument("other_args", nargs='*', help="""Examples:
  mylib.unittests.py                               - run default set of tests
  mylib.unittests.py MyTestSuite                   - run suite 'MyTestSuite'
  mylib.unittests.py MyTestCase.testSomething      - run MyTestCase.testSomething
  mylib.unittests.py MyTestCase                    - run all 'test*' test methods
                                               in MyTestCase
            """)


class defaultdict(dict):
    """
    Backport of collections.defaultdict for F5 that only supports Python 2.4
    http://stackoverflow.com/questions/3785433/python-backports-for-some-methods
    """
    def __init__(self, default_factory, *args, **kwargs):
        """
        default_factory : must be an object type.

        For example 
        x = defaultdict(list)
        x['test']
        >> []
        """
        super(defaultdict, self).__init__(*args, **kwargs)
        self.default_factory = default_factory

    def __missing__(self, key):
        try:
            self[key] = self.default_factory()
        except TypeError:
            raise KeyError("Missing key %s" % (key, ))
        else:
            return self[key]

    def __getitem__(self, key):
        try:
            return super(defaultdict, self).__getitem__(key)
        except KeyError:
            return self.__missing__(key)

def __loadCfg(configFilename):
    """
    Try to load a JSON config file if available
    return conf object
    """
    confObj = None
    jsonCfg = {}
    try:
        try:
            if os.path.isfile(configFilename):
                confF = open(configFilename, 'r')
                confContent = confF.read()
                confF.close()
                try:
                    jsonObj = JSONDecoder()
                    jsonCfg = jsonObj.decode(confContent)
                except Exception:
                    logger.error('Cannot parse json in config file :%s'
                                 % (confContent),
                                 exc_info=Logger.isDebug())
        except Exception:
            logger.error('Configuration file was not loaded properly. %s' %
                         (self.config_filename))
    finally:
        if isinstance(jsonCfg, dict):
            confObj = Options(jsonCfg)
        else:
            logger.error('Error setting configuration file :%s' % (jsonCfg),
                         exc_info=Logger.isDebug())
        return confObj

def dropTheMic(globs, locls, banner='DropTheMic debug mode'):
    """
    Use to drop to a console mode.
    Usage requires globals() and locals() to be given.
    """
    try:
        res = input('Do you want to go to debug '
                        'console (Y or N) ?')
        if res.lower() == 'y':
            code.interact(local=dict(globs, **locls),
                          banner=banner)
    except KeyboardInterrupt:
        pass
    except Exception:
        logger.critical('FEEDBACK NOISE.', exc_info=True)

# 2016-08 GuillaumeNM Added global config
try:
    configFilename = ('%s.config'
                      % (path.dirname(path.dirname(path.abspath(__file__)))))
except Exception:
    configFilename = '.config'

conf = __loadCfg(configFilename)
logger.debug('Loading the following global config file %s'
             % (os.path.abspath(configFilename)))


def inheritors(klass):
    subclasses = set()
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses

def heritingFrom(instanceOrType):
    """
    Return classes name this is heriting from
    """
    klasses = []
    if isinstance(instanceOrType, type):
        bases = instanceOrType.__bases__
    else:
        bases = instanceOrType.__class__.__bases__
    for base in bases:
        klasses.append(base.__name__)
    return klasses


def isHeritingFrom(instance, typeName):
    '''
    Verify all inheritors class names, to see if this instance
    is derived from its master.

    x=1
    isHeritingFrom(x, 'int')
        ==> True
    class A(B):
    class B(C):
    isHeritingFrom(A(), 'C')
        ==> True
    '''

    if isinstance(instance, type):
        klass = instance
    else:
        klass = instance.__class__
    if isinstance(typeName, type):
        klassName = typeName.__name__
    else:
        klassName = typeName
    matchingClasses = [x for x in inspect.getmro(klass) if x.__name__ == klassName]
    return len(matchingClasses) > 0


class NeverMatchException(Exception):
    '''An exception class that is never raised by any code anywhere
    http://stackoverflow.com/questions/8146386/python-conditionally-catching-exceptions
    try:
        10/0
    except (Exception if False else NeverMatchException) as e:
        print 'Should not match' + str(e)
    except (Exception if True else NeverMatchException) as e:
        print 'Handled error' + str(e)
    except ZeroDivisionError:
        print 'zero division error handled'
    except Exception as e:
        print 'no match' + str(e)
    Use case: Handle error only in certain conditions, like if in interactive mode.
'''


class F5Exception(Exception):

    def __init__(self, message):
        self.message = message


def is_F5(raiseIfFalse=False):
    """returns boolean if the script is running on an F5"""
    is_f5_cmd = "tmsh -v"
    result = subprocess.Popen([
                is_f5_cmd],
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.read().split()
    if len(result) == 1 and result[0].find('The current TMSH version')!=-1:
        return True
    if raiseIfFalse:
        raise F5Exception('This is no F5 baby!')
    return False
