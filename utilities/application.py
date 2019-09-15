import argparse
import inspect
import json
import getpass
from utilities.utils import Options, dropTheMic, Logger, pythonVersionMin
import logging
import os
import sys
logger = logging.getLogger(__file__)

try:
    # PRELOAD menu, to avoid recursion of imports
    from . import menu as supermenu
except Exception:
    logger.error('Module Menu not Available.')

TMP_DIR = '/tmp/'


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

    def verbosity(self):
        return self.logGod.level

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
            if ('other_args' in dir(self.args) and self.args.other_args is not None):
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


if pythonVersionMin(2, 7, raiseIfNotMet=False, majorVersionMustMatch=False):
    def loadConfig(self):
        import yaml
        yaml_config = {}
        conf = ""
        try:
            if self.configFilename and os.path.isfile(self.configFilename):
                conf = self.configFilename
            else:
                conf = self.name + '.conf'
            if os.path.isfile(conf):
                with open(conf) as config_file:
                    yaml_config = yaml.load(config_file.read(), Loader=yaml.FullLoader)
            else:
                logger.debug('No Configuration file was found. %s' % (conf))
        except Exception:
            logger.error('Configuration file was not loaded properly. %s' % (conf))
        if yaml_config != {}:
            self.config = yaml_config

    # Python 2.7+ code.
    Application.loadConfig = loadConfig
